from csl.utils.sql_utils import close_session_remove_file, RetentionTime, DataSource, Experiment
from csl.rtscan_functions.utils.rtscan_config import *

def load_rt_models():
    """
    Load and define retention time (RT) transformation models between data sources.

    Each data source in the CSL needs a model for the RT relationship between the external method and the BfG method.
    After updating models, run `csl rtscan recalc path/to/CSL.db` to recalculate predicted RTs.

    Returns:
        models_from_bfg_to_x (dict) : Functions that predict RT values in each external data source given an RT from BfG.
        models_from_x_to_bfg (dict) : Functions that predict BfG RT values given an RT from each external data source.
    """
    import joblib

    # UBA (linear regression)
    def pred_rt_bfg_uba(rt_bfg): return round((rt_bfg - 0.75) / 1.12, 3)
    def pred_rt_uba_bfg(rt_uba): return round(1.12 * rt_uba + 0.75, 3)

    # LANUK (spline regression)
    model_bla = joblib.load(DEFAULT_MODEL_BFG_TO_LANUK_PATH)  # Model for predicting LANUK RTs from BfG RTs
    model_lab = joblib.load(DEFAULT_MODEL_LANUK_TO_BFG_PATH)  # Model for predicting BfG RTs from LANUK RTs
    def pred_rt_bfg_lanuk(rt_bfg): return round(float(model_bla(rt_bfg)), 3)
    def pred_rt_lanuk_bfg(rt_lanuk): return round(float(model_lab(rt_lanuk)), 3)

    # LfU (same method)
    def pred_rt_bfg_lfu(rt_bfg): return rt_bfg
    def pred_rt_lfu_bfg(rt_lfu): return rt_lfu

    # LUBW (spline regression)
    model_blu = joblib.load(DEFAULT_MODEL_BFG_TO_LUBW_PATH)  # Model for predicting LUBW RTs from BfG RTs
    model_lub = joblib.load(DEFAULT_MODEL_LUBW_TO_BFG_PATH)  # Model for predicting BfG RTs from LUBW RTs
    def pred_rt_bfg_lubw(rt_bfg): return round(float(model_blu(rt_bfg)), 3)
    def pred_rt_lubw_bfg(rt_lubw): return round(float(model_lub(rt_lubw)), 3)

    # MONDE (spline regression)
    model_bm = joblib.load(DEFAULT_MODEL_BFG_TO_MONDE_PATH)  # Model for predicting Monde RTs from BfG RTs
    model_mb = joblib.load(DEFAULT_MODEL_MONDE_TO_BFG_PATH)  # Model for predicting BfG RTs from Monde RTs
    def pred_rt_bfg_monde(rt_bfg): return round(float(model_bm(rt_bfg)), 3)
    def pred_rt_monde_bfg(rt_monde): return round(float(model_mb(rt_monde)), 3)

    # LUX (spline regression)
    model_blux = joblib.load(DEFAULT_MODEL_BFG_TO_LUX_PATH)  # Model for predicting Lux RTs from BfG RTs
    model_luxb = joblib.load(DEFAULT_MODEL_LUX_TO_BFG_PATH)  # Model for predicting BfG RTs from Lux RTs
    def pred_rt_bfg_lux(rt_bfg): return round(float(model_blux(rt_bfg)), 3)
    def pred_rt_lux_bfg(rt_lux): return round(float(model_luxb(rt_lux)), 3)

    models_from_bfg_to_x = {'uba': pred_rt_bfg_uba, 'lfuby': pred_rt_bfg_lfu,
                            'lanuk': pred_rt_bfg_lanuk, 'lubw': pred_rt_bfg_lubw,
                            'monde': pred_rt_bfg_monde, 'lux': pred_rt_bfg_lux}
    models_from_x_to_bfg = {'uba': pred_rt_uba_bfg, 'lfuby': pred_rt_lfu_bfg,
                            'lanuk': pred_rt_lanuk_bfg, 'lubw': pred_rt_lubw_bfg,
                            'monde': pred_rt_monde_bfg, 'lux': pred_rt_lux_bfg}

    return models_from_bfg_to_x, models_from_x_to_bfg


def get_dsrc_rt_info(uq_comp_id, session, dsrc_method_pairs):
    """
    Get lists of data sources that are linked to retention time (RT) data in the CSL for a specific compound ID.

    Args:
        uq_comp_id (int)         : Compound ID used to query the CSL database
        session (obj)            : SQLAlchemy session object connected to the CSL database.
        dsrc_method_pairs (dict) : Dictionary mapping CSL data source notation to CSL method notation.

    Returns:
        dsrc_rt (list of str)      : Data sources with any RT entry for the compound ID.
        dsrc_exp_rt (list of str)  : Data sources with an experimental RT entry for the compound ID.
        dsrc_pred_rt (list of str) : Data sources with a predicted RT entry for the compound ID.
    """
    from sqlalchemy import select

    # Query methods with any RT entry for the compound
    methods = session.execute(
        select(RetentionTime.chrom_method).where(RetentionTime.compound_id == uq_comp_id)
    ).scalars().all()

    dsrc_rt = [dsrc for dsrc, method in dsrc_method_pairs.items() if method in methods]

    # Query data sources with experimental RT entry for the compound
    exp_data_sources = session.execute(
        select(DataSource.name)
        .join(Experiment, DataSource.data_source_id == Experiment.data_source_id)
        .where(Experiment.compound_id == uq_comp_id)
    ).scalars().all()

    # Sort data sources of experimental and predicted RT entries
    dsrc_exp_rt = [dsrc for dsrc in dsrc_method_pairs if dsrc in exp_data_sources]
    dsrc_pred_rt = list(set(dsrc_rt).difference(dsrc_exp_rt))

    return dsrc_rt, dsrc_exp_rt, dsrc_pred_rt


def check_experimental_data(uq_comp_id, dsrc_exp_rt, session, dsrc_method_pairs):
    """
    Checks and corrects "predicted" flags for experimental RTs and logs any issues
    such as missing RTs or duplicate entries for the same data source.

    Process:
    1. For each data source with experimental RT data, checks if there is a corresponding RT entry in the database.
    2. If the "predicted" flag is incorrectly set to 'TRUE', it is corrected to 'FALSE'.
    3. Logs warnings for duplicate RT entries and errors for missing RT data.

    Args:
        uq_comp_id (int)               : Compound ID used to query the CSL database
        dsrc_exp_rt (list of str)      : List of data sources with an experimental RT entry for the compound ID.
        session (obj)                  : SQLAlchemy session object connected to the CSL database.
        dsrc_method_pairs (dict)       : Dictionary mapping CSL data source notation to CSL method notation.

    Returns:
        entr_dupl (list of int)          : List of compound IDs with duplicate RT entries for the same data source.
        entr_pred_to_false (list of int) : List of compounds IDs where the "predicted" flag was corrected to 'FALSE'.
        entr_no_exp_rt (list of int)     : List of compounds IDs where no RT was found for the experimental data.
    """
    import logging

    logger = logging.getLogger(__name__)

    # Iterate over data sources with experimental RT
    entr_dupl, entr_pred_to_false, entr_no_exp_rt = [], [], []
    for dsrc_exp in dsrc_exp_rt:
        method = dsrc_method_pairs[dsrc_exp]

        rt_count = session.query(RetentionTime).filter_by(compound_id=uq_comp_id, chrom_method=method).count()
        if rt_count <= 1:
            rt_res = session.query(RetentionTime).filter_by(compound_id=uq_comp_id, chrom_method=method).one_or_none()
        else:
            logger.warning(f'Multiple entries for the same data source ({dsrc_exp}) detected for '
                           f'compound id: {uq_comp_id}. Skipping. Please check.')
            entr_dupl.append(uq_comp_id)
            continue

        if rt_res:
            if not rt_res.predicted or rt_res.predicted == 'TRUE':
                rt_res.predicted = 'FALSE'
                entr_pred_to_false.append(uq_comp_id)
                logger.debug(f'Corrected predicted flag to FALSE for compound {uq_comp_id} ({dsrc_exp})')
            else:
                logger.debug(f'Predicted flag already FALSE for compound {uq_comp_id} ({dsrc_exp})')
        else:
            entr_no_exp_rt.append(uq_comp_id)
            logger.error(f'No RT found for experimental data, compound {uq_comp_id} ({dsrc_exp})')

    return entr_dupl, entr_pred_to_false, entr_no_exp_rt


def check_predicted_flags_pred_data(uq_comp_id, dsrc_pred_rt, session, dsrc_method_pairs):
    """
    Checks and corrects "predicted" flags for all predicted data entries.

    Args:
        uq_comp_id (int)               : Compound ID used to query the CSL database.
        dsrc_pred_rt (list of str)     : List of data sources with predicted RT data.
        session (obj)                  : SQLAlchemy session object connected to the database.
        dsrc_method_pairs (dict)       : Mapping of data sources to chromatographic methods.

    Returns:
        pred_to_true (list of int) : List of compounds IDs where the "predicted" flag was corrected to 'TRUE'.
    """
    import logging

    logger = logging.getLogger(__name__)

    pred_to_true = []
    for dsrc in dsrc_pred_rt:
        method = dsrc_method_pairs[dsrc]
        rt_res = session.query(RetentionTime).filter_by(compound_id=uq_comp_id, chrom_method=method).one_or_none()

        if not rt_res.predicted or rt_res.predicted == 'FALSE':
            rt_res.predicted = 'TRUE'
            pred_to_true.append(uq_comp_id)
            logger.debug(f'Corrected predicted flag to TRUE for compound {uq_comp_id} ({dsrc})')

    return pred_to_true


def predict_bfg_rt(uq_comp_id, session, models_to_bfg, check_order, dsrc_rt, dsrc_method_pairs):
    """
    Predicts missing BfG retention time (RT) for a given compound ID based on available data from other data sources
    (following an order of importance).

    Args:
        uq_comp_id (int)           : Compound ID used to query the CSL database.
        session (obj)              : SQLAlchemy session object connected to the database.
        models_to_bfg (dict)       : Mapping of data sources to models for predicting BfG RTs.
        check_order (list of str)  : List of data sources in order of importance to predict BfG RTs.
        dsrc_rt (list of str)      : List of data sources with available RT data (both experimental and predicted).
        dsrc_method_pairs (dict)   : Mapping of data sources to chromatographic methods.

    Returns:
        float or None: The predicted BfG RT, or None if no prediction could be made.
    """
    from sqlalchemy import func
    import logging

    logger = logging.getLogger(__name__)

    bfg_str = 'bfg'  # BfG string
    rt_bfg_pred = None  # Initialize predicted BfG RT variable

    # Predict missing BfG RT based on available data (in order of importance)
    for check_dsrc in check_order:
        dsrc_str = check_dsrc
        if dsrc_str in dsrc_rt:
            rt_dsrc = session.query(RetentionTime.rt).filter_by(
                compound_id=uq_comp_id, chrom_method=dsrc_method_pairs[dsrc_str]).one_or_none()
            if rt_dsrc:
                rt_bfg_pred = models_to_bfg[dsrc_str](rt_dsrc[0])
                logger.debug(f'Predicted BfG RT using experimental {dsrc_str} RT for compound {uq_comp_id}')
                break

    # Check if BfG RT was successfully predicted
    if rt_bfg_pred:
        # Add predicted BfG RT to the session
        max_rt_id = session.query(func.max(RetentionTime.retention_time_id)).scalar()
        rt_db = RetentionTime(retention_time_id=max_rt_id + 1, rt=rt_bfg_pred, chrom_method=dsrc_method_pairs[bfg_str],
                              compound_id=uq_comp_id, predicted='TRUE')
        session.add(rt_db)
    else:
        logger.error(f'No experimental RT found to predict BfG RT for compound {uq_comp_id}')

    return rt_bfg_pred


def predict_rt(uq_comp_id, session, models_from_bfg, dsrc_str, dsrc_method_pairs):
    """
    Predicts missing retention time (RT) for a given compound ID based on an available experimental or predicted BfG RT.

    Args:
        uq_comp_id (int)           : Compound ID used to query the CSL database.
        session (obj)              : SQLAlchemy session object connected to the database.
        models_from_bfg (dict)     : Mapping of data sources to models for predicting RTs from BfG data.
        dsrc_str (str)             : Data source that needs RT prediction.
        dsrc_method_pairs (dict)   : Mapping of data sources to chromatographic methods.

    Returns:
        float or None: The predicted RT, or None if no prediction could be made.
    """
    from sqlalchemy import func
    import logging

    logger = logging.getLogger(__name__)

    bfg_str = 'bfg'  # BfG string
    rt_pred = None

    # Predict missing RT based on BfG RT
    rt_bfg = session.query(RetentionTime.rt).filter_by(
        compound_id=uq_comp_id, chrom_method=dsrc_method_pairs[bfg_str]).one_or_none()

    if rt_bfg:
        rt_pred = models_from_bfg[dsrc_str](rt_bfg[0])
        logger.debug(f'Predicted {dsrc_str} RT using {bfg_str} RT for compound {uq_comp_id}')

        # Add predicted BfG RT to the session
        max_rt_id = session.query(func.max(RetentionTime.retention_time_id)).scalar()
        rt_db = RetentionTime(retention_time_id=max_rt_id + 1, rt=rt_pred, chrom_method=dsrc_method_pairs[dsrc_str],
                              compound_id=uq_comp_id, predicted='TRUE')
        session.add(rt_db)

    return rt_pred


def recalculate_pred_rt(uq_comp_id, session, dsrc_pred_rt, dsrc_method_pairs):
    """
    Predicts missing retention time (RT) for a given compound ID based on an available experimental or predicted BfG RT.

    Args:
        uq_comp_id (int)         : Compound ID used to query the CSL database.
        session (obj)            : SQLAlchemy session object connected to the database.
        dsrc_pred_rt (str)       : Data sources with predicted RT entry.
        dsrc_method_pairs (dict) : Mapping of data sources to chromatographic methods.

    Returns:
        recalc_comp_id (list of int): List of uq_comp_id that were recalculated.
    """
    from sqlalchemy import func

    # Load RT models
    models_from_bfg_to_x, models_from_x_to_bfg = load_rt_models()

    # Get list of data sources in order of importance to predict BfG RT
    check_order = check_order_pred_bfg_rt()

    bfg_str = 'bfg'  # BfG string
    rt_bfg_pred = None
    recalc_comp_id = []

    if bfg_str in dsrc_pred_rt:
        # Recalculate bfg RT first based on available data (in order of importance), then predict all other non-experimental RTs.
        for check_dsrc in check_order:
                rt_dsrc = session.query(RetentionTime.rt).filter_by(
                    compound_id=uq_comp_id, chrom_method=dsrc_method_pairs[check_dsrc]).one_or_none()
                if rt_dsrc:
                    rt_bfg_pred = models_from_x_to_bfg[check_dsrc](rt_dsrc[0])
                    break

        # Replace predicted bfg RT in session by overwriting at RT ID
        if rt_bfg_pred:
            rt_id = session.query(RetentionTime.retention_time_id).filter_by(
                compound_id=uq_comp_id, chrom_method=dsrc_method_pairs[bfg_str]).one_or_none()[0]

            # Check if the new predicted RT is different from the current one
            current_rt = session.query(RetentionTime.rt).filter_by(retention_time_id=rt_id).scalar()
            if current_rt != rt_bfg_pred:
                rt_obj = session.query(RetentionTime).filter_by(retention_time_id=rt_id).one()
                rt_obj.rt = rt_bfg_pred
                recalc_comp_id.append(uq_comp_id)

        else:
            raise ValueError(f'No experimental RT found to predict BfG RT. '
                             f'Try to run <csl rtscan check path/to/CSL.db> first.')

        # Then recalculate all other predicted RTs
        for dsrc in list(set(dsrc_pred_rt) - {bfg_str}):
            # Predict missing RT based on bfg RT
            rt_pred = models_from_bfg_to_x[dsrc](rt_bfg_pred)
            # Replace predicted RT in session by overwriting at RT ID
            rt_id = session.query(RetentionTime.retention_time_id).filter_by(
                compound_id=uq_comp_id, chrom_method=dsrc_method_pairs[dsrc]).one_or_none()[0]

            # Check if the new predicted RT is different from the current one
            current_rt = session.query(RetentionTime.rt).filter_by(retention_time_id=rt_id).scalar()
            if current_rt != rt_pred:
                rt_obj = session.query(RetentionTime).filter_by(retention_time_id=rt_id).one()
                rt_obj.rt = rt_pred
                recalc_comp_id.append(uq_comp_id)

    else:
        # Predict all existing predicted RTs using the existing experimental bfg RT (We assume it exists).
        for dsrc in dsrc_pred_rt:
            # Get bfg RT
            rt_bfg = session.query(RetentionTime.rt).filter_by(
                compound_id=uq_comp_id, chrom_method=dsrc_method_pairs[bfg_str]).one_or_none()
            if rt_bfg:
                # Predict missing RT based on bfg RT
                rt_pred = models_from_bfg_to_x[dsrc](rt_bfg[0])
                # Replace predicted RT in session by overwriting at RT ID
                rt_id = session.query(RetentionTime.retention_time_id).filter_by(
                    compound_id=uq_comp_id, chrom_method=dsrc_method_pairs[dsrc]).one_or_none()[0]

                # Check if the new predicted RT is different from the current one
                current_rt = session.query(RetentionTime.rt).filter_by(retention_time_id=rt_id).scalar()
                if current_rt != rt_pred:
                    rt_obj = session.query(RetentionTime).filter_by(retention_time_id=rt_id).one()
                    rt_obj.rt = rt_pred
                    recalc_comp_id.append(uq_comp_id)

    return recalc_comp_id


def summarize_corrections_and_errors(uq_comp_ids, dupl_all, pred_to_false_all, no_exp_rt_all,
                                     pred_to_true_all, rt_pred_from_bfg_all, rt_pred_to_bfg_all,
                                     no_pred_rt_all):
    """
    Logs summary of errors and potential corrections that were collected in previous checks.

    Args:
        uq_comp_ids (list of int)          : All unique compound IDs
        dupl_all (list of int)             : List of compound IDs with duplicate RT entries for the same data source.
        pred_to_false_all (list of int)    : List of compounds IDs where the "predicted" flag was corrected to 'FALSE'.
        no_exp_rt_all (list of int)        : List of compounds IDs where no RT was found for the experimental data.
        pred_to_true_all (list of int)     : List of compounds IDs where the "predicted" flag was corrected to 'TRUE'.
        rt_pred_from_bfg_all (list of int) : List of compounds where RT was predicted from BfG.
        rt_pred_to_bfg_all (list of int)   : List of compounds where RT was predicted to BfG.
        no_pred_rt_all (list of int)       : List of compounds IDs where no RT was found for the predicted data of at
                                             least one data source.
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
    logger.info(f'Predicted BfG RT from other data sources: {len(rt_pred_to_bfg_all)}')


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
