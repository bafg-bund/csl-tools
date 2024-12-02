# Set configurations and constant for the rtscan workflow in this file

# Path to retention time models
DEFAULT_GAM_BFG_TO_LANUV_PATH = 'C:/Users/lessmann/C_Daten/PycharmProjects/collective-spec-lib/tests/testdata/rt_scan/ressources/GAM/gam_bfg_to_lanuv.pkl'
DEFAULT_GAM_LANUV_TO_BFG_PATH = 'C:/Users/lessmann/C_Daten/PycharmProjects/collective-spec-lib/tests/testdata/rt_scan/ressources/GAM/gam_lanuv_to_bfg.pkl'


def check_order_pred_bfg_rt():
    """
    Provides a list of institutions in order of importance to predict bfg retention times.
    The first entry is used first if available, then the second one, etc.
    Can be updates when new institution notations are added.
    Check possible institution codes in config.py.

    Returns:
        list : List of institutions in order of importance to predict bfg retention times.
    """
    return ['lfuby', 'uba', 'lanuv']
