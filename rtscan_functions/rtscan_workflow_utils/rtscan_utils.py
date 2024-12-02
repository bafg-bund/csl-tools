from utils.sql_utils import close_session_remove_file, RetentionTime, ExperimentGroup, expGroupExp, Experiment


def get_inst_rt_info(uq_comp_id, session, inst_method_pairs):
    """
    Get lists of institutions that are linked to retention time (RT) data in the CSL for a specific compound ID.

    Args:
        uq_comp_id (int)         : Compound ID used to query the CSL database
        session (obj)            : SQLAlchemy session object connected to the CSL database.
        inst_method_pairs (dict) : Dictionary mapping CSL institution notation to CSL method notation.

    Returns:
        inst_rt (list os str)      : Institutions with any RT entry for the compound ID.
        inst_exp_rt (list of str)  : Institution with an experimental RT entry for the compound ID.
        inst_pred_rt (list of str) : Institution with a predicted RT entry for the compound ID.
    """
    # Get institutions with any RT entry for the compound ID
    results = session.query(RetentionTime.chrom_method).filter_by(compound_id=uq_comp_id).all()
    results_flat = [result[0] for result in results]  # Flatten list
    inst_rt = [inst for inst, method in inst_method_pairs.items() if method in results_flat]

    # Get institutions with an experimental RT entry for the compound ID
    results = session.query(ExperimentGroup).join(
        expGroupExp, ExperimentGroup.experimentGroup_id == expGroupExp.c.experimentGroup_id
    ).join(
        Experiment, Experiment.experiment_id == expGroupExp.c.experiment_id
    ).filter(
        Experiment.compound_id == uq_comp_id
    ).all()
    results_string = ''.join([str(result) for result in results])  # Concatenate to one string
    inst_exp_rt = [inst for inst in inst_method_pairs if inst in results_string]

    # Get institutions with a predicted RT entry for the compound ID
    inst_pred_rt = list(set(inst_rt) - set(inst_exp_rt))

    return inst_rt, inst_exp_rt, inst_pred_rt


def check_experimental_data(uq_comp_id, inst_exp_rt, session, inst_method_pairs):
    """
    Checks and corrects "predicted" flags for experimental RTs and logs any issues
    such as missing RTs or duplicate entries for the same institution.

    Process:
    1. For each institution with experimental RT data, checks if there is a corresponding RT entry in the database.
    2. If the "predicted" flag is incorrectly set to 'TRUE', it is corrected to 'FALSE'.
    3. Logs warnings for duplicate RT entries and errors for missing RT data.

    Args:
        uq_comp_id (int)               : Compound ID used to query the CSL database
        inst_exp_rt (list of str) : List of institutions with an experimental RT entry for the compound ID.
        session (obj)                  : SQLAlchemy session object connected to the CSL database.
        inst_method_pairs (dict)       : Dictionary mapping CSL institution notation to CSL method notation.

    Returns:
        entr_dupl (list of int)          : List of compound IDs with duplicate RT entries for the same institution.
        entr_pred_to_false (list of int) : List of compounds IDs where the "predicted" flag was corrected to 'FALSE'.
        entr_no_exp_rt (list of int)     : List of compounds IDs where no RT was found for the experimental data.
    """
    import logging
    logger = logging.getLogger(__name__)

    entr_dupl, entr_pred_to_false, entr_no_exp_rt = [], [], []

    # Iterate over institutions with experimental RT
    for inst_exp in inst_exp_rt:
        method = inst_method_pairs[inst_exp]

        rt_count = session.query(RetentionTime).filter_by(compound_id=uq_comp_id, chrom_method=method).count()
        if rt_count <= 1:
            rt_res = session.query(RetentionTime).filter_by(compound_id=uq_comp_id, chrom_method=method).one_or_none()
        else:
            logger.warning(f'Multiple entries for the same institution ({inst_exp}) detected for '
                           f'compound id: {uq_comp_id}. Skipping. Please check.')
            entr_dupl.append(uq_comp_id)
            continue

        if rt_res:
            if not rt_res.predicted or rt_res.predicted == 'TRUE':
                rt_res.predicted = 'FALSE'
                entr_pred_to_false.append(uq_comp_id)
                logger.debug(f'Corrected predicted flag to FALSE for compound {uq_comp_id} ({inst_exp})')
            else:
                logger.debug(f'Predicted flag already FALSE for compound {uq_comp_id} ({inst_exp})')
        else:
            entr_no_exp_rt.append(uq_comp_id)
            logger.error(f'No RT found for experimental data, compound {uq_comp_id} ({inst_exp})')

    return entr_dupl, entr_pred_to_false, entr_no_exp_rt


def check_predicted_flags_pred_data(uq_comp_id, inst_pred_rt, session, inst_method_pairs):
    """
    Checks and corrects "predicted" flags for all predicted data entries.

    Args:
        uq_comp_id (int)               : Compound ID used to query the CSL database.
        inst_pred_rt (list of str)     : List of institutions with predicted RT data.
        session (obj)                  : SQLAlchemy session object connected to the database.
        inst_method_pairs (dict)       : Mapping of institutions to chromatographic methods.

    Returns:
        pred_to_true (list of int) : List of compounds IDs where the "predicted" flag was corrected to 'TRUE'.
    """
    import logging
    logger = logging.getLogger(__name__)

    pred_to_true = []
    for inst in inst_pred_rt:
        method = inst_method_pairs[inst]
        rt_res = session.query(RetentionTime).filter_by(compound_id=uq_comp_id, chrom_method=method).one_or_none()

        if not rt_res.predicted or rt_res.predicted == 'FALSE':
            rt_res.predicted = 'TRUE'
            pred_to_true.append(uq_comp_id)
            logger.debug(f'Corrected predicted flag to TRUE for compound {uq_comp_id} ({inst})')

    return pred_to_true


def predict_bfg_rt(uq_comp_id, session, models_to_bfg, check_order, inst_rt, inst_method_pairs, inst_notation_pairs):
    """
    Predicts missing BfG retention time (RT) for a given compound ID based on available data from other institutions
    (following an order of importance).

    Args:
        uq_comp_id (int)           : Compound ID used to query the CSL database.
        session (obj)              : SQLAlchemy session object connected to the database.
        models_to_bfg (dict)       : Mapping of institutions to models for predicting BfG RTs.
        check_order (list of str)  : List of institutions in order of importance to predict BfG RTs.
        inst_rt (list of str)      : List of institutions with available RT data (both experimental and predicted).
        inst_method_pairs (dict)   : Mapping of institutions to chromatographic methods.
        inst_notation_pairs (dict) : Mapping of institution codes to CSL institution notation.

    Returns:
        float or None: The predicted BfG RT, or None if no prediction could be made.
    """
    from sqlalchemy import func
    import logging
    logger = logging.getLogger(__name__)

    bfg_str = inst_notation_pairs['bfg']  # Prepare BfG institution string
    rt_bfg_pred = None  # Initialize predicted BfG RT variable

    # Predict missing BfG RT based on available data (in order of importance)
    for check_inst in check_order:
        inst_str = inst_notation_pairs[check_inst]
        if inst_str in inst_rt:
            rt_inst = session.query(RetentionTime.rt).filter_by(
                compound_id=uq_comp_id, chrom_method=inst_method_pairs[inst_str]).one_or_none()
            if rt_inst:
                rt_bfg_pred = models_to_bfg[inst_str](rt_inst[0])
                logger.debug(f'Predicted BfG RT using experimental {inst_str} RT for compound {uq_comp_id}')
                break

    # Check if BfG RT was successfully predicted
    if rt_bfg_pred:
        # Add predicted BfG RT to the session
        max_rt_id = session.query(func.max(RetentionTime.ret_time_id)).scalar()
        rt_db = RetentionTime(ret_time_id=max_rt_id + 1, rt=rt_bfg_pred, chrom_method=inst_method_pairs[bfg_str],
                              compound_id=uq_comp_id, predicted='TRUE')
        session.add(rt_db)
    else:
        logger.error(f'No experimental RT found to predict BfG RT for compound {uq_comp_id}')

    return rt_bfg_pred


def predict_rt(uq_comp_id, session, models_from_bfg, inst_str, inst_method_pairs, inst_notation_pairs):
    """
    Predicts missing retention time (RT) for a given compound ID based on an available experimental or predicted BfG RT.

    Args:
        uq_comp_id (int)           : Compound ID used to query the CSL database.
        session (obj)              : SQLAlchemy session object connected to the database.
        models_from_bfg (dict)     : Mapping of institutions to models for predicting RTs from BfG data.
        inst_str (str)             : Institution that needs RT prediction.
        inst_method_pairs (dict)   : Mapping of institutions to chromatographic methods.
        inst_notation_pairs (dict) : Mapping of institution codes to CSL institution notation.

    Returns:
        float or None: The predicted RT, or None if no prediction could be made.
    """
    from sqlalchemy import func
    import logging
    logger = logging.getLogger(__name__)

    bfg_str = inst_notation_pairs['bfg']  # Prepare BfG institution string
    rt_pred = None

    # Predict missing RT based on BfG RT
    rt_bfg = session.query(RetentionTime.rt).filter_by(
        compound_id=uq_comp_id, chrom_method=inst_method_pairs[bfg_str]).one_or_none()

    if rt_bfg:
        rt_pred = models_from_bfg[inst_str](rt_bfg[0])
        logger.debug(f'Predicted {inst_str} RT using {bfg_str} RT for compound {uq_comp_id}')

        # Add predicted BfG RT to the session
        max_rt_id = session.query(func.max(RetentionTime.ret_time_id)).scalar()
        rt_db = RetentionTime(ret_time_id=max_rt_id + 1, rt=rt_pred, chrom_method=inst_method_pairs[inst_str],
                              compound_id=uq_comp_id, predicted='TRUE')
        session.add(rt_db)

    return rt_pred


def summarize_corrections_and_errors(uq_comp_ids, dupl_all, pred_to_false_all, no_exp_rt_all,
                                     pred_to_true_all, rt_pred_from_bfg_all, rt_pred_to_bfg_all,
                                     no_pred_rt_all):
    """
    Logs summary of errors and potential corrections that were collected in previous checks.

    Args:
        uq_comp_ids (list of int)          : All unique compound IDs
        dupl_all (list of int)             : List of compound IDs with duplicate RT entries for the same institution.
        pred_to_false_all (list of int)    : List of compounds IDs where the "predicted" flag was corrected to 'FALSE'.
        no_exp_rt_all (list of int)        : List of compounds IDs where no RT was found for the experimental data.
        pred_to_true_all (list of int)     : List of compounds IDs where the "predicted" flag was corrected to 'TRUE'.
        rt_pred_from_bfg_all (list of int) : List of compounds where RT was predicted from BfG.
        rt_pred_to_bfg_all (list of int)   : List of compounds where RT was predicted to BfG.
        no_pred_rt_all (list of int)       : List of compounds IDs where no RT was found for the predicted data of at
                                             least one institution.
    """
    import logging
    logger = logging.getLogger(__name__)

    # Flatten some lists
    dupl_all = sum(dupl_all, [])
    pred_to_false_all = sum(pred_to_false_all, [])
    no_exp_rt_all = sum(no_exp_rt_all, [])
    pred_to_true_all = sum(pred_to_true_all, [])

    # Log summary
    logger.info('### Summary of errors and potential corrections')
    logger.info(f'Total unique compound IDs checked: {len(uq_comp_ids)}')
    logger.info('# Experimental data entries')
    if len(dupl_all) > 0:
        logger.warning(f'Duplicate entries detected: {len(dupl_all)} compound IDs: {dupl_all}')
    logger.info(f'Corrected "predicted" flag to FALSE: {len(pred_to_false_all)}')
    if len(no_exp_rt_all) > 0:
        logger.error(f'No RT found for experimental data: {len(no_exp_rt_all)} compound IDs: {no_exp_rt_all}')
    logger.info('Predicted data entries')
    logger.info(f'Corrected "predicted" flag to TRUE: {len(pred_to_true_all)}')
    if len(no_pred_rt_all) > 0:
        logger.error(f'No RT found for experimental data: {len(no_pred_rt_all)} compound IDs: {no_pred_rt_all}')
    logger.info(f'Predicted RT based on BfG RT: {len(rt_pred_from_bfg_all)}')
    logger.info(f'Predicted BfG RT from other institutions: {len(rt_pred_to_bfg_all)}')


def commit_changes_choice(path_csl, session):
    """
    Checks potential session changes and asks user for confirmation. Typing 'yes' commits session changes to the
    database file. Any other input will cancel the program. If no changes were made to the session or the user cancels
    the program, the session will be closes, and the previously created database (backup) file will be deleted.

    Args:
        path_csl (str) : Path to the CSL file.
        session (obj)  : SQLAlchemy session object connected to the database.
    """
    import logging
    logger = logging.getLogger(__name__)

    # Check if session was modified
    session_change = session.new or session.dirty
    if not session_change:
        close_session_remove_file(path_csl, session)
        logger.info('No changes in current session detected.')
    # Ask for user input for committing session changes
    else:
        print('Commit changes to the CSL? \n  - Confirm by typing "yes" and press enter '
              '\n  - Cancel with any other input')
        choice = input()
        if choice == 'yes':
            session.commit()
            session.close()
            logger.info('Changes committed to the CSL.\nCSL path: {}'.format(path_csl))
        else:
            close_session_remove_file(path_csl, session)
            logger.info('Canceled by user. No changes to the CSL committed.')
