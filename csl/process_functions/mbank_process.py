from process_functions import FormatProcess
from process_functions.utils import *


class MbankProcess(FormatProcess):
    def process(self):
        """Workflow to process MS2 data files from MassBank documents."""

        import logging
        logger = logging.getLogger(__name__)
        logger.info('Executing mbank workflow to process MS2 data files')

        # Load defaults and settings
        var_regex = var_regex_mbank()
        var_fix = var_fix_mbank()
        inst_def = defaults_mbank()
        spec_adduct = adduct_notation_mbank()

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

        logger.info('End of mbank workflow')


    def extract_data_regex(self, file, var_regex):
        """mbank-specific data extraction."""
        return extract_data_regex_mbank(file, var_regex)
