# Set configurations and constant for the rtscan workflow in this file
from csl.config import ROOT_DIR
import os

# Path to retention time models
DEFAULT_MODEL_BFG_TO_LANUK_PATH = os.path.join(ROOT_DIR, 'csl', 'rtscan_functions', 'utils', 'spline_bfg_to_lanuk.pkl')
DEFAULT_MODEL_LANUK_TO_BFG_PATH = os.path.join(ROOT_DIR, 'csl', 'rtscan_functions', 'utils', 'spline_lanuk_to_bfg.pkl')
DEFAULT_MODEL_BFG_TO_LUBW_PATH = os.path.join(ROOT_DIR, 'csl', 'rtscan_functions', 'utils', 'spline_bfg_to_lubw.pkl')
DEFAULT_MODEL_LUBW_TO_BFG_PATH = os.path.join(ROOT_DIR, 'csl', 'rtscan_functions', 'utils', 'spline_lubw_to_bfg.pkl')
DEFAULT_MODEL_BFG_TO_ICPR_PATH = os.path.join(ROOT_DIR, 'csl', 'rtscan_functions', 'utils', 'spline_bfg_to_icpr.pkl')
DEFAULT_MODEL_ICPR_TO_BFG_PATH = os.path.join(ROOT_DIR, 'csl', 'rtscan_functions', 'utils', 'spline_icpr_to_bfg.pkl')

def check_order_pred_bfg_rt():
    """
    Provides a list of data sources in order of importance to predict bfg retention times.
    The first entry is used first if available, then the second one, etc.

    Returns:
        list : List of data sources in order of importance to predict bfg retention times.
    """
    return ['lfuby', 'uba', 'lubw', 'lanuk', 'icpr']
