"""
Main function to operate on retention time data saved in the CSL.

Rtscan Classes:
    update : Workflow for adding missing non-experimental retention times (RT) and correcting errors in associated entries in the CSL.
    recalc : Workflow for recalculating and replacing all non-experimental RTs in the CSL.
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
    "update": UpdateRtscan,
    "recalc": RecalcRtscan
}


def scan_rt(operation: str, path_csl: str):
    """
    Executes the appropriate workflow for exporting CSL data as various formats.

    Args:
        operation (str) : Type of operation. Choose from:
            - 'update'  : Adds missing non-experimental retention times using available experimental data and corrects errors in associated entries in the CSL.
            - 'recalc'  : Recalculates and replaces all non-experimental retention times using available experimental data in the CSL.
        path_csl (str)  : Path to the CSL file.
    """
    # Validate the provided file paths
    validate_file_path(path_csl)

    # Select and execute the appropriate workflow based on the data source
    workflow_class = WORKFLOWS[operation]
    workflow = workflow_class(path_csl)
    workflow.rtscan()
