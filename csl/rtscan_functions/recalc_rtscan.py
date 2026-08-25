from csl.config import DEFAULT_PAIRS_DSOURCE_CHROM
from csl.utils import *
from csl.rtscan_functions.operation_rtscan import OperationRtscan
from csl.rtscan_functions.utils.rtscan_utils import *


class RecalcRtscan(OperationRtscan):
    def rtscan(self):
        """Workflow for recalculating and replacing all non-experimental RTs in the CSL."""
        import logging
        import os
        import shutil
        from tqdm import tqdm

        logger = logging.getLogger(__name__)
        logger.info('Executing recalc rtscan workflow')

        # Backup the database file with updated filename
        filename = os.path.basename(self.path_csl)
        release_type = 'minor'  # Fixed release type for rtscan operations
        updated_filename = update_version_filename(filename, release_type)
        new_path_csl = str(os.path.join(os.path.dirname(self.path_csl), updated_filename))
        shutil.copy(self.path_csl, new_path_csl)

        # Connect to the database
        session = create_session(new_path_csl)

        # Get list of all (non-GC) unique compound IDs
        uq_comp_ids = get_unique_non_gc_comp_ids(session)

        # Filter data source dictionary for non-GC data sources
        DEFAULT_PAIRS_DSOURCE_CHROM_filtered = {
            key: value
            for key, value in DEFAULT_PAIRS_DSOURCE_CHROM.items()
            if "_gc" not in key and "_gc" not in value
        }

        # Initialize empty list
        recalc_comp_id_all = []

        # Loop through compound IDs to recalculate and replace predicted RT data
        with session.no_autoflush:
            for uq_comp_id in tqdm(uq_comp_ids):

                # Get data sources linked to predicted retention time data in the CSL for each compound ID
                _, dsrc_exp_rt, dsrc_pred_rt = get_dsrc_rt_info(uq_comp_id, session, DEFAULT_PAIRS_DSOURCE_CHROM_filtered)

                # Recalculate the RTs for all data sources with predicted RT
                recalc_comp_id = recalculate_pred_rt(uq_comp_id, session, dsrc_exp_rt, dsrc_pred_rt, DEFAULT_PAIRS_DSOURCE_CHROM_filtered)
                recalc_comp_id_all.append(recalc_comp_id)

            # Summarize the result
            logger.info('### Summary')
            logger.info(f'Total unique compound IDs checked: {len(uq_comp_ids)}')
            logger.info(f'Number of recalculated and updated predicted RTs: {len(recalc_comp_id_all)}')

            # Ask for user input and commit changes if confirmed. Ends the session.
            if len(recalc_comp_id_all) > 0:
                commit_changes_choice(new_path_csl, session)
            else:
                close_session_remove_file(new_path_csl, session)
                logger.info('No changes in current session detected.')

        logger.info('End of recalc rtscan workflow')
