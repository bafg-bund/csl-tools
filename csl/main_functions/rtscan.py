"""
Main function to operate on retention time data saved in the CSL.

Rtscan Classes:
    check   : Workflow for checking the status of the retention time data in the CSL, without making any changes.
    update  : Workflow for updating missing retention time data in the CSL.
    replace : Workflow for recalculating all retention time data in the CSL.
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


def run_rtscan_workflow(operation, path_csl):
    """
    Executes the appropriate workflow for exporting CSL data as various formats.

    Args:
        operation (str) : Type of operation. todo explain here? do same for other main functions
        path_csl (str)  : Path to the CSL file.
    """

    # Validate the provided file paths
    validate_file_path(path_csl)

    # Select and execute the appropriate workflow based on the institution
    workflow_class = WORKFLOWS[operation]
    workflow = workflow_class(path_csl)
    workflow.rtscan()
