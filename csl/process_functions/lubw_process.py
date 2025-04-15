from process_functions import FormatProcess
from process_functions.utils import *


class LubwProcess(FormatProcess):
    def process(self):
        """Workflow to process MS2 data files from the institution lubw (Landesanstalt für Umwelt Baden-Württemberg)."""

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
        # todo: Reading function (extract_data_regex_lubw) adjustments:
        #       - splitting identifier such as "=" and "[|]" for LUBW (could be set in config)
        #         wait for LANUV workflow to see if its worth it to combine
        #         line: delim = '=' if '=' in line else '[|]'
        #       - chunk_identifier differs (e.g. 'MS:1009003|Name' for lubw and 'Name :' for lfuby)
        #         could be also set in config file
        #       -  some strings in docstring
        if not extract_data.empty:
            # Adding default information
            logger.info('Adding fixed information to extracted data')
            extract_data_add = self.add_fixed_variables(extract_data, var_fix)  # todo worked without mod

            # Processing files
            logger.info('Processing data')
            form_data = self.process_data(extract_data_add, inst_def, spec_adduct)
            # todo worked without mod
            #  (but needs "QF" in adduct_name as well as an empty special adduct dict in <inst>_config,
            #  even though adduct recognition is not applied)

            # Match extracted data with CSL
            logger.info('Matching extracted experiments with CSL')
            form_data_match, session = self.match_with_csl(form_data, inst_def)  # todo worked without modification

            # Commit session to CSL
            logger.info('Preparing to commit session changes to CSL')
            self.commit_to_csl(session, form_data_match)  # todo worked without modification

        logger.info('End of lubw workflow')

    def extract_data_regex(self, file, var_regex):
        """lubw-specific data extraction."""
        return extract_data_regex_lubw(file, var_regex)
