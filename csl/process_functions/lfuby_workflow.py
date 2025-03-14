from process_functions import InstitutionWorkflow
from utils.sql_utils import create_session
from process_functions.institution_workflow_utils import *


class LfubyWorkflow(InstitutionWorkflow):
    def process(self):
        """Workflow to process MS2 data files from the institution lfuby (Bayerisches Landesamt für Umwelt)."""

        import logging
        logger = logging.getLogger(__name__)
        logger.info('Executing lfuby workflow to process MS2 data files')

        # Load institution defaults and settings
        var_regex = var_regex_lfuby()
        var_fix = var_fix_lfuby()
        inst_def = defaults_lfuby()
        spec_adduct = adduct_notation_lfuby()

        # Read files
        logger.info('Reading file(s)')
        extract_data = self.read_files(var_regex)
        if not extract_data.empty:
            # Adding default information
            logger.info('Adding fixed information to extracted data')
            extract_data_add = self.add_fixed_variables(extract_data, var_fix)

            # Processing files
            logger.info('Processing data')
            form_data = self.process_data(extract_data_add, inst_def, spec_adduct)

            # Match extracted data with CSL
            logger.info('Matching extracted experiments with CSL')
            form_data_match, session = self.match_with_csl(form_data, inst_def)

            # Commit session to CSL
            logger.info('Preparing to commit session changes to CSL')
            self.commit_to_csl(session, form_data_match)

        logger.info('End of lfuby workflow')

    def read_files(self, var_regex):
        """
        Collects and processes files and extracts data using specific regular expressions.

        1. If self.path_files is a directory path then all files in that directory (including sub-directories) are
        retrieved. Todo: Option to filter files based on identifier string still exists, but likely will be removed.
        2. Extracts data from the files using a list of regular expressions specific to the lfuby context.
        3. Adds file path information and append extracted data of each file.

        Returns:
                data_extract_all (DataFrame) : Extracted data from all files based on regular expressions.
        """
        import os
        import pandas as pd

        # Get file paths
        if isinstance(self.path_data, list):  # User selected file(s) are provided as list of str
            file_paths = self.path_data
        else:  # Otherwise check if provided path is a directory or a single file
            if os.path.isfile(self.path_data):
                file_paths = [self.path_data]
            else:  # If a directory is provided
                # Filter files based on identifier string
                # Todo: Identifier string (fstr_id) for files is not an option for user input (needed?).
                #  Set to None (= retrieves all files).
                file_paths = match_file_paths(self.path_data, fstr_id=None)

        # Data extraction based on lfuby specific regular expressions
        data_extract_all = []
        for file in file_paths:
            data_extract_file = extract_data_regex_lfuby(file, var_regex)
            data_extract_file['file_path'] = file  # Add current file path for every entry
            data_extract_all.append(data_extract_file)

        # Merge into one pandas DataFrame and reset index
        if len(data_extract_all) > 0 and isinstance(data_extract_all, list):
            data_extract_all = pd.concat(data_extract_all, ignore_index=True)

        return data_extract_all

    # noinspection PyMethodMayBeStatic
    def add_fixed_variables(self, extract_data, var_fix):
        """Adds fixed information (specified in <institution>_config.py) to each entry."""
        extract_data_add = extract_data
        for var in var_fix.items():
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

        entry_err = False
        entry_warn = False
        form_data_entry_all = []  # List of dictionaries with formatted data

        for index, entry in extract_data.iterrows():  # Each entry in the DataFrame

            logger.info(f'Compound: {entry['var_comp']}; CE: {entry['var_ce']}; File path: {entry['file_path']}')

            # Polarity
            pol_i = get_polarity(entry['var_ion_mode'], inst_def['def_pol_p'], inst_def['def_pol_n'])
            if not pol_i:
                logger.warning(f'Unexpected polarity type: {entry['var_ion_mode']}')
                entry_err = True

            # Compound and adduct name
            comp_i, adduct_name = get_compound_and_adduct_name(entry['var_comp'])
            if not comp_i or not adduct_name:
                logger.warning(
                    f'Unexpected or missing compound/adduct name: {entry['var_comp']}.')
                entry_err = True

            # Adduct format conversion
            adduct_i = format_adduct(adduct_name, spec_adduct, inst_def['def_qf'], pol_i)
            if not adduct_i:
                logger.warning(f'Adduct name not detected. Check fields for compound name and ion mode')
                entry_err = True
            else:
                logger.info(f'Adduct name: {adduct_name}; Formatted adduct name: {adduct_i}')

            # Collision energy (CE) and collision energy spread (CES)
            ce_i, ces_i, ces_warn = get_collision_energy(entry['var_ce'])
            if not ce_i or not ce_i and not ces_i:
                logger.warning(
                    f'No collision energy (CE) or unexpected number of CE or non-equal difference in CE spread. '
                    f'Check field for collision energy')
                entry_err = True
            elif ces_warn:
                logger.warning(f'Unexpected collision energy spread. Verify field for collision energy. '
                               f'\n''Will NOT automatically skip file due to this warning')
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
                logger.warning('CAS registry number not detected or malformed')
                entry_warn = True

            # Set error flag to True if no InChIKey and no CAS registry number found
            if not inchikey_i and not cas_i:
                entry_err = True

            # SMILES
            smiles_i = get_smiles(entry['var_smiles'])
            if not smiles_i:
                logger.warning('Smiles not detected')
                entry_err = True

            # Precursor mass
            mz_i = get_precursor_mz(entry['var_mz'])
            if not mz_i:
                logger.warning('Precursor mass not detected')
                entry_err = True

            # Retention time
            rt_i = get_retention_time(entry['var_rt'])
            if not rt_i:
                logger.warning('Retention time not detected')
                entry_err = True

            # Spectra / Peaks
            spec_i = get_peaks(entry['var_peak'])
            if spec_i.empty:
                logger.warning('No spectra detected')
                entry_err = True

            # Compound group
            compgroup_i = get_compound_group(entry['var_compgroup'])

            # Temporary save formatted data from one entry in dictionary
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
                'mz_i': mz_i,
                'rt_i': rt_i,
                'spec_i': spec_i,
                'compgroup_i': compgroup_i,
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
                    logger.warning(f'Found {res_count} duplicate(s) in CSL \n Compound: {entry['var_comp']}; '
                                   f'CE: {entry['var_ce']}; File path: {entry['file_path']}')
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

    # noinspection PyMethodMayBeStatic
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

        form_err_data = form_data_match[form_data_match.form_err_flag]
        form_warn_data = form_data_match[form_data_match.form_warn_flag]
        csl_dupl_data = form_data_match[form_data_match.csl_dupl_flag]
        csl_err_data = form_data_match[form_data_match.csl_err_flag]
        csl_add_data = form_data_match[form_data_match.csl_add_flag]

        # Log information about entry states
        logger.info('Summary of information before CSL commit '
                    '\n (Check more details on individual errors and warnings in the log)')
        if len(form_err_data) > 0:
            logger.error('The following data will not be added to the CSL due to format errors:')
            for index, entry in form_err_data.iterrows():
                logger.error(f'Compound: {entry['var_comp']}; CE: {entry['var_ce']}; File path: {entry['file_path']}')

        if len(form_warn_data) > 0:
            logger.warning('The following data will be added to the CSL with warnings:')
            for index, entry in form_warn_data.iterrows():
                logger.warning(f'Compound: {entry['var_comp']}; CE: {entry['var_ce']}; File path: {entry['file_path']}')

        if len(csl_err_data) > 0:
            logger.error('The following data will not be added to the CSL due to errors caused during CSL-matching:')
            for index, entry in csl_err_data.iterrows():
                logger.error(f'Compound: {entry['var_comp']}; CE: {entry['var_ce']}; File path: {entry['file_path']}')

        if len(csl_dupl_data) > 0:
            logger.warning('The following data already exists in the CSL and will not be added:')
            for index, entry in csl_dupl_data.iterrows():
                logger.warning(f'Compound: {entry['var_comp']}; CE: {entry['var_ce']}; File path: {entry['file_path']}')

        if len(csl_add_data) > 0:
            logger.info('The following data will be added to the CSL:')
            for index, entry in csl_add_data.iterrows():
                logger.info(f'Compound: {entry['var_comp']}; CE: {entry['var_ce']}; File path: {entry['file_path']}')

        # Collect data eligible for addition
        add_data_all = form_data_match[form_data_match.csl_add_flag]

        # User choice for committing changes to CSL
        if len(add_data_all) == 0:
            logger.info('No data to add to the CSL')
        else:
            print(
                'Do you want to proceed committing these changes? \n  - Confirm by typing "yes" and pressing enter \n'
                '  - Cancel with any other input')
            choice = input()
            if choice == 'yes':
                # Commit all changes to the CSL
                session.commit()
                logger.info(f'Changes committed to CSL at {self.path_csl}')
            else:
                logger.info('Operation canceled by user. No data added to CSL.')

        # End session
        session.close()
