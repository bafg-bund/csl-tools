from csl.process_functions.utils import *
from csl.utils.sql_utils import create_session
from csl.config import DEFAULT_PAIRS_DSOURCE_CHROM

from abc import ABC, abstractmethod

class FormatProcess(ABC):
    def __init__(self, path_csl, path_data, path_config, path_extra):
        self.path_csl = path_csl
        self.path_data = path_data
        self.path_config = path_config
        self.path_extra = path_extra

    def process(self):
        raise NotImplementedError("Subclasses should implement this!")

    def load_config(self):
        """Loads and returns configuration for data processing from YAML file."""
        import yaml

        with open(self.path_config) as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise ValueError(exc)

        par_config = config.get("par_config", {})
        adduct_notation = config.get("adduct_notation", {})

        return par_config, adduct_notation

    def read_files(self, par_regex):
        """
        Collects file paths and extracts data using format-specific regular expressions.

        Args:
            par_regex (dict) : Mapping of parameters (keys) to format-specific identifiers (values) for data extraction.

        Returns:
            data_extract_all (DataFrame) : Extracted data from all files based on regular expressions.
        """
        import pandas as pd

        # Collect valid file paths
        file_paths = get_file_paths(self.path_data)

        # Data extraction based on the subclass-specific method and regular expressions
        data_extract_all = []
        for file in file_paths:
            data_extract_file = self.extract_data_regex(file, par_regex, self.path_extra)
            data_extract_file['file_path'] = file  # Add current file path for every entry
            data_extract_all.append(data_extract_file)

        # Merge into one pandas DataFrame and reset index
        if len(data_extract_all) > 0 and isinstance(data_extract_all, list):
            data_extract_all = pd.concat(data_extract_all, ignore_index=True)

        return data_extract_all


    @abstractmethod
    def extract_data_regex(self, file, par_regex, file_extra):
        """Subclasses should implement this method to extract data."""
        pass


    # noinspection PyMethodMayBeStatic
    def add_fixed_variables(self, extract_data, par_fix):
        """Adds fixed information (specified in <software>_process_config.py and config.yaml) to each entry."""
        import logging

        logger = logging.getLogger(__name__)

        extract_data_add = extract_data

        # Add chromatographic method based on data source
        dsrc = par_fix.get('par_data_source')
        if not dsrc:
            raise ValueError("Data source is empty or missing (check your config.yaml).")
        try:
            extract_data_add['par_chrom_method'] = DEFAULT_PAIRS_DSOURCE_CHROM[dsrc]
        except KeyError:
            raise ValueError(f"Chromatographic method for data source '{dsrc}' is not defined (check config.py).")

        # Add each parameter and its value.
        for par in par_fix.items():
            if par[1]:
                extract_data_add[par[0]] = par[1]
            else:
                logger.warning(f"No value for {par[0]}.")
                extract_data_add[par[0]] = par[1]

        return extract_data_add


    # noinspection PyMethodMayBeStatic
    def process_data(self, extract_data, defaults, spec_adduct):
        """
        Formats the previously extracted and collected data to match the required format for csl-matching/commits.

        Data entries are checked for errors and marked with flags in DataFrame:
            form_err_flag (bool)  : True : Entry has format errors. Will not enter csl-matching process.
                                    False: Entry will enter csl-matching process.
            form_warn_flag (bool) : True : Entry will not be skipped, but user gets a warning before csl-commit.
                                    False: Entry will enter csl-matching process.

        Args:
            extract_data (DataFrame) : Extracted and collected data.
            defaults (dict)          : Software-specific defaults.
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

            logger.info(f'Compound: {entry['par_comp']}; CE: {entry['par_ce']}; File path: {entry['file_path']}')

            # Instrument
            instrument_i = get_instrument(entry['par_instrument'], entry['par_instrument_type'])
            if not instrument_i:
                logger.error(f"Instrument (name: {entry['par_instrument']}, type: {entry['par_instrument_type']}) not on whitelist. Skipping entry.")
                extract_data = extract_data.drop(index)
                continue

            # Polarity
            pol_i = get_polarity(entry['par_ion_mode'], defaults['def_pol_p'], defaults['def_pol_n'])
            if not pol_i:
                logger.warning(f'Unexpected polarity type: {entry['par_ion_mode']}')
                entry_err = True

            # Compound and adduct name (adduct name only for <CompoundName_AdductName> notation)
            comp_i, adduct_name = get_compound_and_adduct_name(entry['par_comp'])
            if not comp_i or not adduct_name:
                logger.warning(
                    f'Unexpected or missing compound/adduct name: {entry['par_comp']}.')
                entry_err = True

            # Adduct format conversion
            if entry['par_adduct']:  # adduct name is replaced if entry exists
                adduct_name = entry['par_adduct']
            adduct_i = format_adduct(adduct_name, spec_adduct, defaults['def_qf'], pol_i)
            if not adduct_i:
                logger.warning(f'Adduct name not detected. Check fields for compound name and ion mode.')
                entry_err = True
            else:
                logger.info(f'Adduct name: {adduct_name}; Formatted adduct name: {adduct_i}')

            # Collision energy (CE) and collision energy spread (CES)
            ce_i, ces_i = get_collision_energy(entry['par_ce'], entry['par_ces'])
            if not ce_i:
                logger.warning(
                    f'No collision energy (CE) or unexpected number of CE or non-equal difference in CE spread. '
                    f'Check field for collision energy.')
                entry_err = True


            # Ionization type
            ionization_i = get_ionization_type(entry['par_ionization'])
            if not ionization_i:
                logger.warning('Ionization type not detected.')
                entry_err = True

            # Formula
            formula_i = get_formula(entry['par_formula'])
            if not formula_i:
                logger.warning('Formula not detected.')
                entry_err = True

            # InChIKey
            inchikey_i, inchikey_main_i = get_inchikey(entry['par_inchikey'])
            if not inchikey_i:
                logger.warning('InChiKey not detected.')
                entry_warn = True

            # CAS registry number
            cas_i = get_cas(entry['par_cas'])
            if not cas_i:
                logger.warning('CAS registry number not detected or malformed.')
                entry_warn = True

            # Set error flag to True if no InChIKey and no CAS registry number found
            if not inchikey_i and not cas_i:
                entry_err = True

            # SMILES
            smiles_i = get_smiles(entry['par_smiles'])
            if not smiles_i:
                logger.warning('Smiles not detected.')
                entry_err = True

            # InChI
            inchi_i = get_inchi_from_smiles(smiles_i)
            if not inchi_i:
                logger.warning('InChI not generated.')
                entry_err = True

            # Precursor mass
            mz_i = get_precursor_mz(entry['par_mz'])
            if not mz_i:
                logger.warning('Precursor mass not detected.')
                entry_err = True

            # Retention time
            rt_i = get_retention_time(entry['par_rt'])
            if not rt_i:
                logger.warning('Retention time not detected.')
                entry_err = True

            # Spectra / Peaks
            spec_i = get_peaks(entry['par_peak'])
            if spec_i.empty:
                logger.warning('No spectra detected.')
                entry_err = True

            # Compound group
            compgroup_i = get_compound_group(entry['par_compgroup'])

            # Collision type / Fragmentation mode
            col_type_i = get_collision_type(entry['par_col_type'])
            if not col_type_i:
                logger.warning('Collision type / Fragmentation mode not detected.')
                entry_err = True

            # Experiment ID from accession string
            experiment_id_i = get_experiment_id(entry['par_accession'])

            # Get exact mass and adduct mass (not for CSL, but for checking)
            exact_mass, adduct_mass = get_exact_mass_adduct_mass(entry['par_exact_mass'], smiles_i, entry['par_mz'])

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
                'exact_mass': exact_mass,
                'adduct_mass': adduct_mass,
                'form_err_flag': entry_err,
                'form_warn_flag': entry_warn
            }
            form_data_entry_all.append(form_data_entry)

        # Convert all formatted data into DataFrame
        form_data_entry_df = pd.DataFrame(form_data_entry_all)

        # Merge DataFrames along columns
        form_data = pd.concat(objs=[extract_data.reset_index(drop=True), form_data_entry_df.reset_index(drop=True)], axis='columns')

        return form_data


    def match_with_csl(self, form_data):
        """
        Matches formatted data with the CSL to detect duplicates and add new experimental information.
        The function also sorts entries based on whether they can be added to the CSL or should be skipped.

        All data entries in the DataFrame will be marked with flags:
            csl_dupl_flag (bool) : True: Entry already in the CSL. Will not enter csl-commit process.
            csl_err_flag (bool)  : True: Entry has CSL matching errors. Will not enter csl-commit process.
            csl_add_flag (bool)  : True: Entry will enter csl-commit process.

        Args:
            form_data (DataFrame) : All data entries including formatted data.

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
                    entry_dupl = True
                elif res_count < 0:  # Missing identifiers, skip the file
                    logger.warning('No InChIKey and no CAS registry number found. Provide at least one. Skipping file.')
                    entry_err = True
                else:
                    # Add new experimental information to the session and check relevant entries in the CSL
                    exp_added = add_exp_to_session(session, entry)
                    if exp_added:
                        entry_add = True
                    else:
                        entry_err = True

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
        form_warn_data = form_data_match[(form_data_match['form_warn_flag']) & (~form_data_match['csl_dupl_flag'])
                                         & (~form_data_match['form_err_flag'])]
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
                'Do you want to proceed committing these changes? \n'
                '  - Confirm by typing "yes" and pressing enter. \n'
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
