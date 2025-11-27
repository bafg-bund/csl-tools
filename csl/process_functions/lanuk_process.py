from csl.process_functions import FormatProcess
from csl.process_functions.utils import *


class LanukProcess(FormatProcess):
    def process(self):
        """Workflow to process MS2 data files from the data source lanuk
        (Landesamt für Natur, Umwelt und Klima Nordrhein-Westfalen)."""
        import logging

        logger = logging.getLogger(__name__)
        logger.info('Executing lanuk workflow to process MS2 data files')

        # Load defaults and settings
        par_config, adduct_notation = self.load_config()
        var_regex = var_regex_lanuk()
        var_fix = var_fix_lanuk()
        dsrc_def = defaults_lanuk()
        fixed_par = par_config | var_fix

        # Read files
        logger.info('Reading file(s)')
        extract_data = self.read_files(var_regex)
        if not extract_data.empty:
            # Adding default information
            logger.info('Adding fixed information to extracted data')
            extract_data_add = self.add_fixed_variables(extract_data, fixed_par)

            # Processing files
            logger.info('Processing data')
            form_data = self.process_data(extract_data_add, dsrc_def, adduct_notation)

            # Match extracted data with CSL
            logger.info('Matching extracted experiments with CSL')
            form_data_match, session = self.match_with_csl(form_data)

            # Commit session to CSL
            logger.info('Preparing to commit session changes to CSL')
            self.commit_to_csl(session, form_data_match)

        logger.info('End of lanuk workflow')


    def extract_data_regex(self, file, var_regex, file_extra=None):
        """lanuk-specific data extraction."""
        return extract_data_regex_lanuk(file, var_regex, file_extra)
