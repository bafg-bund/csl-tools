from csl.process_functions import FormatProcess
from csl.process_functions.utils import *


class LibviewProcess(FormatProcess):
    def process(self):
        """Workflow to process libview-based MS2 data files."""
        import logging

        logger = logging.getLogger(__name__)
        logger.info('Executing libview workflow to process MS2 data files')

        # Load defaults and settings
        par_config, adduct_notation = self.load_config()
        par_regex = par_regex_libview()
        defaults = defaults_libview()

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
            self.summarize_and_commit_to_csl(session, extract_data_add, form_data_match)

        logger.info('End of libview workflow')


    def extract_data_regex(self, file, par_regex, file_extra=None):
        """libview-specific data extraction."""
        return extract_data_regex_libview(file, par_regex, file_extra)
