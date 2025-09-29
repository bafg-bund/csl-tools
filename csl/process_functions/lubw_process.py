from csl.process_functions import FormatProcess
from csl.process_functions.utils import *


class LubwProcess(FormatProcess):
    def process(self):
        """Workflow to process MS2 data files from the data source lubw (Landesanstalt für Umwelt Baden-Württemberg)."""
        import logging

        logger = logging.getLogger(__name__)
        logger.info('Executing lubw workflow to process MS2 data files')

        # Load defaults and settings
        var_regex = var_regex_lubw()
        var_fix = var_fix_lubw()
        inst_def = defaults_lubw()
        spec_adduct = adduct_notation_lubw()

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

        logger.info('End of lubw workflow')

    def extract_data_regex(self, file, var_regex):
        """lubw-specific data extraction."""
        return extract_data_regex_lubw(file, var_regex)
