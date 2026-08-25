from csl.config import DEFAULT_PAIRS_DSOURCE_CHROM
from csl.utils import *
from csl.rtscan_functions.operation_rtscan import OperationRtscan
from csl.rtscan_functions.utils.rtscan_utils import *
from csl.rtscan_functions.utils.rtscan_config import *


class UpdateRtscan(OperationRtscan):
    def rtscan(self):
        """Workflow for adding missing non-experimental retention times (RT) and correcting errors in associated entries in the CSL."""
        import logging
        import os
        import shutil
        from tqdm import tqdm

        logger = logging.getLogger(__name__)
        logger.info('Executing update rtscan workflow')

        # Load RT models
        models_from_bfg_to_x, models_from_x_to_bfg = load_rt_models()

        # Get list of data sources in order of importance to predict BfG RT
        check_order = check_order_pred_bfg_rt()

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

        # Initialize empty lists
        (dupl_all, pred_to_false_all, no_exp_rt_all, pred_to_true_all, pred_from_bfg_all, pred_to_bfg_all,
         no_pred_rt_all) = [], [], [], [], [], [], []

        # Loop through compound IDs to check experimental and predicted RT data
        for uq_comp_id in tqdm(uq_comp_ids):
            # Get data sources linked to (any or experimental) retention time data in the CSL for each compound ID
            dsrc_rt, dsrc_exp_rt, dsrc_pred_rt = get_dsrc_rt_info(uq_comp_id, session, DEFAULT_PAIRS_DSOURCE_CHROM_filtered)

            # Check experimental RT data
            dupl, pred_to_false, no_exp_rt = check_experimental_data(uq_comp_id, dsrc_exp_rt, session, DEFAULT_PAIRS_DSOURCE_CHROM_filtered)
            dupl_all.append(dupl)
            pred_to_false_all.append(pred_to_false)
            no_exp_rt_all.append(no_exp_rt)

            # Check and correct "predicted" flags for predicted data entries
            pred_to_true = check_predicted_flags_pred_data(uq_comp_id, dsrc_pred_rt, session, DEFAULT_PAIRS_DSOURCE_CHROM_filtered)
            pred_to_true_all.append(pred_to_true)

            # Check predicted RT data and predict missing RTs
            if not 'bfg' in dsrc_rt:
                # Predict BfG RT if it doesn't exist yet and add entry to session
                rt_bfg_pred = predict_bfg_rt(uq_comp_id, session, models_from_x_to_bfg, check_order, dsrc_rt, DEFAULT_PAIRS_DSOURCE_CHROM_filtered)
                if rt_bfg_pred:
                    # Add BfG to the list of data sources with available RTs
                    dsrc_rt.append('bfg')
                    pred_to_bfg_all.append(uq_comp_id)

            dsrc_miss_rt = list(set(DEFAULT_PAIRS_DSOURCE_CHROM_filtered.keys()) - set(dsrc_rt))  # Get list of data sources without any RT
            for dsrc in dsrc_miss_rt:
                # Predict the RTs for all other data sources without any RT
                rt_pred = predict_rt(uq_comp_id, session, models_from_bfg_to_x, dsrc, DEFAULT_PAIRS_DSOURCE_CHROM_filtered)
                if rt_pred:
                    pred_from_bfg_all.append(uq_comp_id)
                else:
                    no_pred_rt_all.append(uq_comp_id)

        # Summarize the result
        summarize_corrections_and_errors(uq_comp_ids, dupl_all, pred_to_false_all, no_exp_rt_all,
                                         pred_to_true_all, pred_from_bfg_all, pred_to_bfg_all,
                                         no_pred_rt_all)

        # Check if the session was modified
        def has_data(x):
            return any(map(has_data, x)) if isinstance(x, list) else True

        if any(map(has_data, [pred_to_false_all, pred_to_true_all, pred_to_bfg_all, pred_from_bfg_all])):
            # Ask for user input and commit changes if confirmed. Ends the session.
            commit_changes_choice(new_path_csl, session)
        else:
            close_session_remove_file(new_path_csl, session)
            logger.info('No changes in current session detected.')

        logger.info('End of update rtscan workflow')
