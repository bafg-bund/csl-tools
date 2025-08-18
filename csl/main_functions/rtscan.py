"""
Main function to operate on retention time data saved in the CSL.

Rtscan Classes:
    check   : Workflow for checking mistakes in retention time (RT) entries and adding missing RT in the CSL.
    update  : Workflow for recalculating all retention time entries in the CSL.
"""

from csl.utils import validate_file_path, setup_logger
from csl.rtscan_functions import *
from csl.config import ROOT_DIR

import os.path
from datetime import datetime

# Setup logs folder and set the root logger
fname = datetime.now().strftime('%Y%m%d_%H%M%S') + '_log'
log_dir = os.path.join(ROOT_DIR, 'logs')
os.makedirs(log_dir, exist_ok=True)
log_fpath = os.path.join(log_dir, fname)
setup_logger(log_fpath)  # Sets basic logger configuration and adds stream handlers

# Define workflow dictionary
WORKFLOWS = {
    "check": CheckRtscan,
    "update": UpdateRtscan
}


def scan_rt(operation: str, path_csl: str):
    """
    Executes the appropriate workflow for exporting CSL data as various formats.

    Args:
        operation (str) : Type of operation. Choose from:
            - 'check'   : Checks for mistakes in RT entries and adds missing RT values in the CSL.
            - 'update'  : Recalculates all RT entries in the CSL.
        path_csl (str)  : Path to the CSL file.
    """

    # Validate the provided file paths
    validate_file_path(path_csl)

    # Select and execute the appropriate workflow based on the institution
    workflow_class = WORKFLOWS[operation]
    workflow = workflow_class(path_csl)
    workflow.rtscan()
