from rtscan_functions.operation_rtscan import OperationRtscan
from utils.file_utils import update_version_filename
from utils.sql_utils import inst_code_csl_mapping, create_session
from rtscan_functions.utils.rtscan_utils import *
from config import DEFAULT_PAIRS_INST_CHROM
from rtscan_functions.utils.rtscan_config import (DEFAULT_GAM_BFG_TO_LANUV_PATH, DEFAULT_GAM_LANUV_TO_BFG_PATH,
                                                  check_order_pred_bfg_rt)  # todo test model results


class UpdateRtscan(OperationRtscan):
    def rtscan(self):
        """Workflow for updating missing retention time (RT) data in the CSL."""

        import joblib
        import os
        import shutil
        from tqdm import tqdm
        import numpy as np
        import logging
        logger = logging.getLogger(__name__)
        logger.info('Executing update rtscan workflow')

        # Blend a new dictionary that maps of institution notation and method notation for CSL queries
        all_methods = DEFAULT_PAIRS_INST_CHROM
        inst_notation_pairs = inst_code_csl_mapping()
        inst_method_pairs = {inst_notation_pairs[key]: all_methods[key] for key in all_methods}

        # Functions for predicting RTs between institutions
        # Models need to be updated when institution are added, or when existing notations are modified.
        gam_bl = joblib.load(DEFAULT_GAM_BFG_TO_LANUV_PATH)  # GAM model for predicting LANUV RTs from BfG RTs
        gam_lb = joblib.load(DEFAULT_GAM_LANUV_TO_BFG_PATH)  # GAM model for predicting BfG RTs from LANUV RTs
        def pred_rt_bfg_uba(rt_bfg): return round((rt_bfg - 0.75) / 1.12, 3)
        def pred_rt_uba_bfg(rt_uba): return round(1.12 * rt_uba + 0.75, 3)
        def pred_rt_bfg_lanuv(rt_bfg): return round(gam_bl.predict(rt_bfg)[0], 3)
        def pred_rt_lanuv_bfg(rt_lanuv): return round(gam_lb.predict(rt_lanuv)[0], 3)
        def pred_rt_bfg_lfu(rt_bfg): return rt_bfg
        def pred_rt_lfu_bfg(rt_lfu): return rt_lfu
        models_from_bfg = {inst_notation_pairs['uba']: pred_rt_bfg_uba, inst_notation_pairs['lfuby']: pred_rt_bfg_lfu,
                           inst_notation_pairs['lanuv']: pred_rt_bfg_lanuv}
        models_to_bfg = {inst_notation_pairs['uba']: pred_rt_uba_bfg, inst_notation_pairs['lfuby']: pred_rt_lfu_bfg,
                         inst_notation_pairs['lanuv']: pred_rt_lanuv_bfg}

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

        import time
        # Initialize empty lists
        (dupl_all, pred_to_false_all, no_exp_rt_all, pred_to_true_all, pred_from_bfg_all, pred_to_bfg_all,
         no_pred_rt_all) = [], [], [], [], [], [], []

        start = time.time()

        # Loop through compound IDs to check experimental and predicted RT data
        for uq_comp_id in tqdm(uq_comp_ids):
            # Get institutions linked to (any or experimental) retention time data in the CSL for each compound ID
            inst_rt, inst_exp_rt, inst_pred_rt = get_inst_rt_info(uq_comp_id, session, inst_method_pairs)

            # Check experimental RT data
            dupl, pred_to_false, no_exp_rt = check_experimental_data(
                uq_comp_id, inst_exp_rt, session, inst_method_pairs)
            dupl_all.append(dupl)
            pred_to_false_all.append(pred_to_false)
            no_exp_rt_all.append(no_exp_rt)

            # Check and correct "predicted" flags for predicted data entries
            pred_to_true = check_predicted_flags_pred_data(uq_comp_id, inst_pred_rt, session, inst_method_pairs)
            pred_to_true_all.append(pred_to_true)

            # Check predicted RT data and predict missing RTs
            if not inst_notation_pairs['bfg'] in inst_rt:
                # Predict BfG RT if it doesn't exist yet and add entry to session
                rt_bfg_pred = predict_bfg_rt(uq_comp_id, session, models_to_bfg, check_order, inst_rt,
                                             inst_method_pairs, inst_notation_pairs)
                if rt_bfg_pred:
                    # Add BfG to the list of institutions with available RTs
                    inst_rt.append(inst_notation_pairs['bfg'])
                    pred_to_bfg_all.append(uq_comp_id)

            inst_miss_rt = list(set(inst_method_pairs.keys()) - set(inst_rt))  # Get list of institutions without any RT
            for inst in inst_miss_rt:
                # Predict the RTs for all other institution without any RT
                rt_pred = predict_rt(uq_comp_id, session, models_from_bfg, inst, inst_method_pairs, inst_notation_pairs)
                if rt_pred:
                    pred_from_bfg_all.append(uq_comp_id)
                else:
                    no_pred_rt_all.append(uq_comp_id)

        end = time.time()
        print(f'elapsed time: {end - start}')

        # Summarize the result
        summarize_corrections_and_errors(uq_comp_ids, dupl_all, pred_to_false_all, no_exp_rt_all,
                                         pred_to_true_all, pred_from_bfg_all, pred_to_bfg_all,
                                         no_pred_rt_all)

        # Ask for user input and commit changes if confirmed. Ends the session.
        commit_changes_choice(new_path_csl, session)

        logger.info('End of update rtscan workflow')
