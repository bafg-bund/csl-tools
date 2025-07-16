from csl.config import DEFAULT_PAIRS_INST_CHROM
from csl.utils import *
from csl.rtscan_functions.operation_rtscan import OperationRtscan
from csl.rtscan_functions.utils.rtscan_utils import *
from csl.rtscan_functions.utils.rtscan_config import *


class CheckRtscan(OperationRtscan):
    def rtscan(self):
        """Workflow for checking retention time (RT) entries for errors and adding missing RTs in the CSL."""
        import logging
        import joblib
        import os
        import shutil
        from tqdm import tqdm
        import numpy as np

        logger = logging.getLogger(__name__)
        logger.info('Executing check rtscan workflow')

        # Functions for predicting RTs between data sources
        # Models need to be updated when other data sources are added, or when existing notations are modified.
        model_bl = joblib.load(DEFAULT_MODEL_BFG_TO_LANUK_PATH)  # Model for predicting LANUK RTs from BfG RTs
        model_lb = joblib.load(DEFAULT_MODEL_LANUK_TO_BFG_PATH)  # Model for predicting BfG RTs from LANUK RTs
        def pred_rt_bfg_uba(rt_bfg): return round((rt_bfg - 0.75) / 1.12, 3)
        def pred_rt_uba_bfg(rt_uba): return round(1.12 * rt_uba + 0.75, 3)
        def pred_rt_bfg_lanuk(rt_bfg): return round(model_bl(rt_bfg), 3)
        def pred_rt_lanuk_bfg(rt_lanuk): return round(model_lb(rt_lanuk), 3)
        def pred_rt_bfg_lfu(rt_bfg): return rt_bfg
        def pred_rt_lfu_bfg(rt_lfu): return rt_lfu
        models_from_bfg = {'uba': pred_rt_bfg_uba, 'lfuby': pred_rt_bfg_lfu,
                           'lanuk': pred_rt_bfg_lanuk}
        models_to_bfg = {'uba': pred_rt_uba_bfg, 'lfuby': pred_rt_lfu_bfg,
                         'lanuk': pred_rt_lanuk_bfg}

        # Get list of institutions in order of importance to predict BfG RT
        check_order = check_order_pred_bfg_rt()

        # Backup the database file with updated filename
        filename = os.path.basename(self.path_csl)
        release_type = 'minor'  # Fixed release type for rtscan operations
        updated_filename = update_version_filename(filename, release_type)
        new_path_csl = str(os.path.join(os.path.dirname(self.path_csl), updated_filename))
        shutil.copy(self.path_csl, new_path_csl)

        # Connect to the database
        session = create_session(new_path_csl)

        # Get list of all unique compound IDs
        comp_ids = session.query(RetentionTime.compound_id).all()
        comp_ids = [comp_id[0] for comp_id in comp_ids]  # Flatten list
        uq_comp_ids = np.unique(comp_ids).tolist()

        # Initialize empty lists
        (dupl_all, pred_to_false_all, no_exp_rt_all, pred_to_true_all, pred_from_bfg_all, pred_to_bfg_all,
         no_pred_rt_all) = [], [], [], [], [], [], []

        # Loop through compound IDs to check experimental and predicted RT data
        for uq_comp_id in tqdm(uq_comp_ids):
            # Get institutions linked to (any or experimental) retention time data in the CSL for each compound ID
            inst_rt, inst_exp_rt, inst_pred_rt = get_inst_rt_info(uq_comp_id, session, DEFAULT_PAIRS_INST_CHROM)

            # Check experimental RT data
            dupl, pred_to_false, no_exp_rt = check_experimental_data(uq_comp_id, inst_exp_rt, session, DEFAULT_PAIRS_INST_CHROM)
            dupl_all.append(dupl)
            pred_to_false_all.append(pred_to_false)
            no_exp_rt_all.append(no_exp_rt)

            # Check and correct "predicted" flags for predicted data entries
            pred_to_true = check_predicted_flags_pred_data(uq_comp_id, inst_pred_rt, session, DEFAULT_PAIRS_INST_CHROM)
            pred_to_true_all.append(pred_to_true)

            # Check predicted RT data and predict missing RTs
            if not 'bfg' in inst_rt:
                # Predict BfG RT if it doesn't exist yet and add entry to session
                rt_bfg_pred = predict_bfg_rt(uq_comp_id, session, models_to_bfg, check_order, inst_rt, DEFAULT_PAIRS_INST_CHROM)
                if rt_bfg_pred:
                    # Add BfG to the list of institutions with available RTs
                    inst_rt.append('bfg')
                    pred_to_bfg_all.append(uq_comp_id)

            inst_miss_rt = list(set(DEFAULT_PAIRS_INST_CHROM.keys()) - set(inst_rt))  # Get list of institutions without any RT
            for inst in inst_miss_rt:
                # Predict the RTs for all other institution without any RT
                rt_pred = predict_rt(uq_comp_id, session, models_from_bfg, inst, DEFAULT_PAIRS_INST_CHROM)
                if rt_pred:
                    pred_from_bfg_all.append(uq_comp_id)
                else:
                    no_pred_rt_all.append(uq_comp_id)

        # Summarize the result
        summarize_corrections_and_errors(uq_comp_ids, dupl_all, pred_to_false_all, no_exp_rt_all,
                                         pred_to_true_all, pred_from_bfg_all, pred_to_bfg_all,
                                         no_pred_rt_all)

        # Ask for user input and commit changes if confirmed. Ends the session.
        commit_changes_choice(new_path_csl, session)

        logger.info('End of check rtscan workflow')
