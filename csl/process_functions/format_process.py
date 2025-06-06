from process_functions.utils import *
from utils import inst_code_csl_mapping
from utils.sql_utils import create_session
from abc import ABC, abstractmethod
from config import DEFAULT_PAIRS_INST_CHROM


class FormatProcess(ABC):
    def __init__(self, path_csl, path_data):
        self.path_csl = path_csl
        self.path_data = path_data

    def process(self):
        raise NotImplementedError("Subclasses should implement this!")


    def read_files(self, var_regex):
        """
        Collects file paths and extracts data using format-specific regular expressions.

        Args:
            var_regex (dict) : Mapping of parameters (keys) to format-specific identifiers (values) for data extraction.

        Returns:
            data_extract_all (DataFrame) : Extracted data from all files based on regular expressions.
        """
        import pandas as pd

        # Collect valid file paths
        file_paths = get_file_paths(self.path_data)

        # Data extraction based on the subclass-specific method and regular expressions
        data_extract_all = []
        for file in file_paths:
            data_extract_file = self.extract_data_regex(file, var_regex)
            data_extract_file['file_path'] = file  # Add current file path for every entry
            data_extract_all.append(data_extract_file)

        # Merge into one pandas DataFrame and reset index
        if len(data_extract_all) > 0 and isinstance(data_extract_all, list):
            data_extract_all = pd.concat(data_extract_all, ignore_index=True)

        return data_extract_all


    @abstractmethod
    def extract_data_regex(self, file, var_regex):
        """Subclasses should implement this method to extract data."""
        pass


    # noinspection PyMethodMayBeStatic
    def add_fixed_variables(self, extract_data, var_fix):
        """Adds fixed information (specified in <institution>_config.py) to each entry."""
        import logging
        logger = logging.getLogger(__name__)

        extract_data_add = extract_data
        for var in var_fix.items():
            # Add value to column of DataFrame. Special case for var_chrom_method if None
            if var[1]:
                extract_data_add[var[0]] = var[1]
            elif not var[1] and var[0] == 'var_chrom_method':
                options = DEFAULT_PAIRS_INST_CHROM.values()
                message = 'Select the chromatographic method for the experiments to be added'
                choice = get_user_choice(list(options), message)
                extract_data_add[var[0]] = choice
                logger.info(f"Chromatographic method: {choice}")
            elif not var[1] and var[0] == 'var_expg_csl':
                options = inst_code_csl_mapping()
                message = 'Select the default value for the experiment group for the experiments to be added'
                choice = get_user_choice(list(options.values()), message)
                extract_data_add[var[0]] = choice
                logger.info(f"Default experiment group: {choice}")
            elif not var[1] and var[0] == 'var_compg_csl':
                options = inst_code_csl_mapping()
                message = 'Select the default value for the compound group for the experiments to be added'
                choice = get_user_choice(list(options.values()), message)
                extract_data_add[var[0]] = choice
                logger.info(f"Default compound group: {choice}")
            else:
                logger.warning(f"No value for {var[0]}.")
                extract_data_add[var[0]] = var[1]
        return extract_data_add


    # noinspection PyMethodMayBeStatic
    def process_data(self, extract_data, inst_def, spec_adduct):
        """
        Formats the previously extracted and collected data based in institution-specific variables to match the
        required format for csl-matching/commits. For information on format requirements of txt files see:
        https://gitlab.lan.bafg.de/nts/ntsportal/-/wikis/Processing-new-files-for-the-CSL

        Data entries are checked for errors and marked with flags in DataFrame:
            form_err_flag (bool)  : True : Entry has format errors. Will not enter csl-matching process.
                                    False: Entry will enter csl-matching process.
            form_warn_flag (bool) : True : Entry will not be skipped, but user gets a warning before csl-commit.
                                    False: Entry will enter csl-matching process.

        Args:
            extract_data (DataFrame) : Extracted and collected data.
            inst_def (dict)          : Institution-specific defaults.
            spec_adduct (dict)       : Special cases in adduct formatting.

        Returns:
            form_data (DataFrame) : Extracted and collected data including the formatted data.
        """
        import pandas as pd
        import logging
        logger = logging.getLogger(__name__)

        form_data_entry_all = []  # List of dictionaries with formatted data

        for index, entry in extract_data.iterrows():  # Each entry in the DataFrame

            entry_err = False
            entry_warn = False

            logger.info(f'Compound: {entry['var_comp']}; CE: {entry['var_ce']}; File path: {entry['file_path']}')

            # Polarity
            pol_i = get_polarity(entry['var_ion_mode'], inst_def['def_pol_p'], inst_def['def_pol_n'])
            if not pol_i:
                logger.warning(f'Unexpected polarity type: {entry['var_ion_mode']}')
                entry_err = True

            # Compound and adduct name (adduct name only for <CompoundName_AdductName> notation)
            comp_i, adduct_name = get_compound_and_adduct_name(entry['var_comp'])
            if not comp_i or not adduct_name:
                logger.warning(
                    f'Unexpected or missing compound/adduct name: {entry['var_comp']}.')
                entry_err = True

            # Adduct format conversion
            if entry['var_adduct']:  # adduct name is replaced if entry exists
                adduct_name = entry['var_adduct']
            adduct_i = format_adduct(adduct_name, spec_adduct, inst_def['def_qf'], pol_i)
            if not adduct_i:
                logger.warning(f'Adduct name not detected. Check fields for compound name and ion mode.')
                entry_err = True
            else:
                logger.info(f'Adduct name: {adduct_name}; Formatted adduct name: {adduct_i}')

            # Collision energy (CE) and collision energy spread (CES)
            ce_i, ces_i, ces_warn = get_collision_energy(entry['var_ce'])
            if not ce_i or not ce_i and not ces_i:
                logger.warning(
                    f'No collision energy (CE) or unexpected number of CE or non-equal difference in CE spread. '
                    f'Check field for collision energy.')
                entry_err = True
            elif ces_warn:
                logger.warning(f'Unexpected collision energy spread. Verify field for collision energy. '
                               f'\n''Will NOT automatically skip file due to this warning.')
                entry_warn = True

            # Ionization type
            ionization_i = get_ionization_type(entry['var_ionization'])
            if not ionization_i:
                logger.warning('Ionization type not detected.')
                entry_err = True

            # Formula
            formula_i = get_formula(entry['var_formula'])
            if not formula_i:
                logger.warning('Formula not detected.')
                entry_err = True

            # InChIKey
            inchikey_i, inchikey_main_i = get_inchikey(entry['var_inchikey'])
            if not inchikey_i:
                logger.warning('InChiKey not detected.')
                entry_warn = True

            # CAS registry number
            cas_i = get_cas(entry['var_cas'])
            if not cas_i:
                logger.warning('CAS registry number not detected or malformed.')
                entry_warn = True

            # Set error flag to True if no InChIKey and no CAS registry number found
            if not inchikey_i and not cas_i:
                entry_err = True

            # SMILES
            smiles_i = get_smiles(entry['var_smiles'])
            if not smiles_i:
                logger.warning('Smiles not detected.')
                entry_err = True

            # InChI
            inchi_i = get_inchi_from_smiles(smiles_i)
            if not inchi_i:
                logger.warning('InChI not generated.')
                entry_err = True

            # Precursor mass
            mz_i = get_precursor_mz(entry['var_mz'])
            if not mz_i:
                logger.warning('Precursor mass not detected.')
                entry_err = True

            # Retention time
            rt_i = get_retention_time(entry['var_rt'])
            if not rt_i:
                logger.warning('Retention time not detected.')
                entry_err = True

            # Spectra / Peaks
            spec_i = get_peaks(entry['var_peak'])
            if spec_i.empty:
                logger.warning('No spectra detected.')
                entry_err = True

            # Compound group
            compgroup_i = get_compound_group(entry['var_compgroup'])

            # Collision type / Fragmentation mode
            col_type_i = get_collision_type(entry['var_col_type'])
            if not col_type_i:
                logger.warning('Collision type / Fragmentation mode not detected.')
                entry_err = True

            # Instrument
            instrument_i = get_instrument(entry['var_instrument'], entry['var_instrument_type'])

            # Experiment ID from accession string
            experiment_id_i = get_experiment_id(entry['var_accession'])

            # Organize formatted data from one entry in dictionary
            form_data_entry = {
                'pol_i': pol_i,
                'comp_i': comp_i,
                'adduct_i': adduct_i,
                'ce_i': ce_i,
                'ces_i': ces_i,
                'ionization_i': ionization_i,
                'formula_i': formula_i,
                'inchikey_i': inchikey_i,
                'inchikey_main_i': inchikey_main_i,
                'cas_i': cas_i,
                'smiles_i': smiles_i,
                'inchi_i': inchi_i,
                'mz_i': mz_i,
                'rt_i': rt_i,
                'spec_i': spec_i,
                'compgroup_i': compgroup_i,
                'col_type_i': col_type_i,
                'instrument_i': instrument_i,
                'experiment_id_i': experiment_id_i,
                'form_err_flag': entry_err,
                'form_warn_flag': entry_warn
            }
            form_data_entry_all.append(form_data_entry)

        # Convert all formatted data into DataFrame
        form_data_entry_df = pd.DataFrame(form_data_entry_all)

        # Merge DataFrames along columns
        form_data = pd.concat(objs=[extract_data, form_data_entry_df], axis='columns')

        return form_data


    def match_with_csl(self, form_data, inst_def):
        """
        Matches formatted data with the CSL to detect duplicates and add new experimental information.
        The function also sorts entries based on whether they can be added to the CSL or should be skipped.

        All data entries in the DataFrame will be marked with flags:
            csl_dupl_flag (bool) : True: Entry already in the CSL. Will not enter csl-commit process.
            csl_err_flag (bool)  : True: Entry has CSL matching errors. Will not enter csl-commit process.
            csl_add_flag (bool)  : True: Entry will enter csl-commit process.

        Args:
            form_data (DataFrame) : All data entries including formatted data.
            inst_def (dict)       : Institution-specific defaults.

        Returns:
            form_data_match (DataFrame) : Data updated with flags from CSL-matching
            session (obj)  : Session object with temporary changes (potential commits).
        """
        import pandas as pd
        import logging
        logger = logging.getLogger(__name__)

        # Create a session for CSL connection
        session = create_session(self.path_csl)

        flags_all = []

        # Check for duplicate entries; add experimental information to the session; collect files for CSL commitment
        for index, entry in form_data.iterrows():
            # Reset flags for categorizing entries based on CSL matching results
            entry_dupl = False  # Entries already in the CSL
            entry_err = False  # Entries with errors
            entry_add = False  # Entries passing the CSL matching process

            if not entry.form_err_flag:  # Go through matching-process if error flag is False, otherwise skip
                # Match experimental parameters with the CSL to detect potential duplicate entries
                res_count = check_duplicate(session, entry)  # Number of duplicate entries
                if res_count > 0:  # Duplicate found, skip the file
                    # logger.warning(f'Found {res_count} duplicate(s) in CSL \n Compound: {entry['var_comp']}; '
                    #                f'CE: {entry['var_ce']}; File path: {entry['file_path']}')
                    entry_dupl = True
                elif res_count < 0:  # Missing identifiers, skip the file
                    logger.warning('No InChIKey and no CAS registry number found. Provide at least one. Skipping file.')
                    entry_err = True
                else:
                    # Add new experimental information to the session and check relevant entries in the CSL
                    add_exp_to_session(session, entry, inst_def)
                    entry_add = True

            flags = {
                'csl_dupl_flag': entry_dupl,
                'csl_err_flag': entry_err,
                'csl_add_flag': entry_add
            }
            flags_all.append(flags)

        # Convert all flags into DataFrame
        flags_df = pd.DataFrame(flags_all)

        # Merge DataFrames along columns
        form_data_match = pd.concat(objs=[form_data, flags_df], axis='columns')

        return form_data_match, session


    def commit_to_csl(self, session, form_data_match):
        """
        Handles the final step of committing experimental data files to the CSL. The user is prompted to confirm the
        commit, and the session is closed afterward, regardless of the user's choice. The paths of committed files are
        recorded in a CSV file.

        Args:
            session (obj)               : Session object with temporary changes (potential commits).
            form_data_match (DataFrame) : Data including relevant flags
        """
        import logging
        logger = logging.getLogger(__name__)

        form_err_data = form_data_match[form_data_match['form_err_flag']]
        form_warn_data = form_data_match[(form_data_match['form_warn_flag']) & (~form_data_match['csl_dupl_flag'])]
        csl_dupl_data = form_data_match[form_data_match['csl_dupl_flag']]
        csl_err_data = form_data_match[form_data_match['csl_err_flag']]
        csl_add_data = form_data_match[form_data_match['csl_add_flag']]

        # Log information about entry states
        logger.info('Summary of information before CSL commit '
                    '\n (Check more details on individual errors and warnings in the log).')
        logger.info(f"Experiments eligible to be added: {len(csl_add_data)}")
        logger.warning(f"Experiments that are eligible to be added, but with warnings: {len(form_warn_data)}")
        logger.warning(f"Experiments that are already in the CSL (duplicates): {len(csl_dupl_data)}")
        logger.error(f"Experiments that are not eligible to be added due to matching errors: {len(csl_err_data)}")
        logger.error(f"Experiments that are not eligible for adding due to format errors: {len(form_err_data)}")

        if len(form_err_data) > 0:
            logger.error('The following data will not be added to the CSL due to format errors:')
            for index, entry in form_err_data.iterrows():
                logger.error(f'Compound: {entry['comp_i']}; CE: {entry['ce_i']}; File path: {entry['file_path']}')

        if len(form_warn_data) > 0:
            logger.warning('The following data will be added to the CSL with warnings:')
            for index, entry in form_warn_data.iterrows():
                logger.warning(f'Compound: {entry['comp_i']}; CE: {entry['ce_i']}; File path: {entry['file_path']}')

        if len(csl_err_data) > 0:
            logger.error('The following data will not be added to the CSL due to errors caused during CSL-matching:')
            for index, entry in csl_err_data.iterrows():
                logger.error(f'Compound: {entry['comp_i']}; CE: {entry['ce_i']}; File path: {entry['file_path']}')

        if len(csl_dupl_data) > 0:
            logger.warning('The following data already exists in the CSL and will not be added:')
            for index, entry in csl_dupl_data.iterrows():
                logger.warning(f'Compound: {entry['comp_i']}; CE: {entry['ce_i']}; File path: {entry['file_path']}')

        if len(csl_add_data) > 0:
            logger.info('The following data will be added to the CSL:')
            for index, entry in csl_add_data.iterrows():
                logger.info(f'Compound: {entry['comp_i']}; CE: {entry['ce_i']}; File path: {entry['file_path']}')

        # Collect data eligible for addition
        add_data_all = form_data_match[form_data_match.csl_add_flag]

        # User choice for committing changes to CSL
        if len(add_data_all) == 0:
            logger.info('No data to add to the CSL.')
        else:
            print(
                'Do you want to proceed committing these changes? \n  - Confirm by typing "yes" and pressing enter. \n'
                '  - Cancel with any other input.')
            choice = input()
            if choice == 'yes':
                # Commit all changes to the CSL
                session.commit()
                logger.info(f'Changes committed to CSL at {self.path_csl}.')
            else:
                logger.info('Operation canceled by user. No data added to CSL.')

        # End session
        session.close()
