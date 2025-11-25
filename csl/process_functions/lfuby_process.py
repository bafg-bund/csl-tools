from csl.process_functions import FormatProcess
from csl.process_functions.utils import *


class LfubyProcess(FormatProcess):
    def process(self):
        """Workflow to process MS2 data files from the data source lfuby (Bayerisches Landesamt für Umwelt)."""
        import logging

        logger = logging.getLogger(__name__)
        logger.info('Executing lfuby workflow to process MS2 data files')

        # Load defaults and settings
        var_regex = var_regex_lfuby()
        var_fix = var_fix_lfuby()
        dsrc_def = defaults_lfuby()
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
            form_data = self.process_data(extract_data_add, dsrc_def, spec_adduct)

            # Match extracted data with CSL
            logger.info('Matching extracted experiments with CSL')
            form_data_match, session = self.match_with_csl(form_data)

            # Commit session to CSL
            logger.info('Preparing to commit session changes to CSL')
            self.commit_to_csl(session, form_data_match)

        logger.info('End of lfuby workflow')

    def extract_data_regex(self, file, var_regex, file_extra=None):
        """lfuby-specific data extraction."""
        return extract_data_regex_lfuby(file, var_regex)
