from csl.process_functions import FormatProcess
from csl.process_functions.utils import *


class LanukProcess(FormatProcess):
    def process(self):
        """Workflow to process MS2 data files from the data source lanuk
        (Landesamt für Natur, Umwelt und Klima Nordrhein-Westfalen)."""
        import logging

        logger = logging.getLogger(__name__)
        logger.info('Executing lanuk workflow to process MS2 data files')
        logger.warning('LANUK workflow currently implemented for testing only.')

        # Load defaults and settings
        var_regex = var_regex_lanuk()
        var_fix = var_fix_lanuk()
        dsrc_def = defaults_lanuk()
        spec_adduct = adduct_notation_lanuk()

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

            # Todo: Lanuk workflow works until here for sure. The reading was modified (only extract_var_regex_lanuk)
            #  the processing runs perfectly without modification.
            #  As some data types are missing in the raw data, placehoders were inserted for testing purposes.
            #  This affects:
            #   - RT
            #   - InChiKey (Not needed if CAS exists)
            #   - SMILES
            #   - Compound Group (Default is added: LANUK)
            #  Furthermore, assumptions were made: ionization type 'ESI', collision type 'Q' (from existing csl data), and
            #  type of molecular mass 'monoisotopic'. They all need confirmation.

            # Match extracted data with CSL
            logger.info('Matching extracted experiments with CSL')
            form_data_match, session = self.match_with_csl(form_data)

            # Commit session to CSL
            logger.info('Preparing to commit session changes to CSL')
            self.commit_to_csl(session, form_data_match)

        logger.info('End of lanuk workflow')

    def extract_data_regex(self, file, var_regex):
        """lanuk-specific data extraction."""
        return extract_data_regex_lanuk(file, var_regex)
