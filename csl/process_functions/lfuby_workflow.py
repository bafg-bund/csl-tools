from process_functions import InstitutionWorkflow
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
        retrieved.
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
                # Find all files in directory (also subdirectories)
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

