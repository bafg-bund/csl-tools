from csl.process_functions import FormatProcess
from csl.process_functions.utils import *


class MzvaultProcess(FormatProcess):
    def process(self):
        """Workflow to process mzVault-based MS2 data files."""
        import logging

        logger = logging.getLogger(__name__)
        logger.info('Executing mzvault workflow to process MS2 data files')

        # Load defaults and settings
        par_config, adduct_notation = self.load_config()
        if par_config['par_data_source'] == 'lubw':  # mzVault version 2.3.45.15
            par_regex = par_regex_mzvault_old()
            defaults = defaults_mzvault_old()
        else:  # mzVault version 2.3.64.0
            par_regex = par_regex_mzvault()
            defaults = defaults_mzvault()

        # Read files
        logger.info('Reading file(s)')
        extract_data = self.read_files(par_regex)
        if not extract_data.empty:
            # Adding default information
            logger.info('Adding fixed information to extracted data')
            extract_data_add = self.add_fixed_variables(extract_data, par_config)

            # Processing files
            logger.info('Processing data')
            form_data = self.process_data(extract_data_add, defaults, adduct_notation)

            # Match extracted data with CSL
            logger.info('Matching extracted experiments with CSL')
            form_data_match, session = self.match_with_csl(form_data)

            # Commit session to CSL
            logger.info('Preparing to commit session changes to CSL')
            self.commit_to_csl(session, form_data_match)

        logger.info('End of mzvault workflow')

    def extract_data_regex(self, file, par_regex, file_extra=None):
        """mzvault-specific data extraction."""
        return extract_data_regex_mzvault(file, par_regex)
