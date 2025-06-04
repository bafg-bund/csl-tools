# Set configurations and constant for the rtscan workflow in this file
import os
from config import ROOT_DIR

# Path to retention time models
DEFAULT_GAM_BFG_TO_LANUK_PATH = os.path.join(ROOT_DIR, 'csl', 'rtscan_functions', 'utils', 'gam_bfg_to_lanuk.pkl')
DEFAULT_GAM_LANUK_TO_BFG_PATH = os.path.join(ROOT_DIR, 'csl', 'rtscan_functions', 'utils', 'gam_lanuk_to_bfg.pkl')


def check_order_pred_bfg_rt():
    """
    Provides a list of institutions in order of importance to predict bfg retention times.
    The first entry is used first if available, then the second one, etc.
    Can be updates when new institution notations are added.
    Check possible institution codes in config.py.

    Returns:
        list : List of institutions in order of importance to predict bfg retention times.
    """
    return ['lfuby', 'uba', 'lanuk']
