"""
Main function to export CSL data as various formats.

Export classes:
    thermo : Workflow for exporting the CSL as a txt file readable by mzVault.
    envi   : Workflow for exporting the CSL as a target list usable for enviMass.
    mbank  : Workflow for exporting the CSL as txt files for MassBank.
"""

import os.path
from datetime import datetime
from utils import validate_file_path, setup_logger
from export_functions import *
from config import ROOT_DIR

# Setup logs folder and set the root logger
fname = datetime.now().strftime('%Y%m%d_%H%M%S') + '_log'
log_dir = os.path.join(ROOT_DIR, 'logs')
os.makedirs(log_dir, exist_ok=True)
log_fpath = os.path.join(log_dir, fname)
setup_logger(log_fpath)  # Sets basic logger configuration and adds stream handlers

# Define workflow dictionary
WORKFLOWS = {
    "thermo": ThermoWorkflow,
    "envi": EnviWorkflow,
    "mbank": MbankWorkflow
}


def run_export_workflow(format, path_out, path_csl, subset):
    """
    Executes the appropriate workflow for exporting CSL data as various formats.

    Args:
        format (str)     : Export format.
        path_out (str)   : Path to export directory.
        path_csl (str)   : Path to the CSL file.
        subset (str)     : Data source (institution), used to subset the CSL data before exporting.
    """

    # Validate the provided file paths
    validate_file_path(path_csl)
    validate_file_path(path_out)

    # Select and execute the appropriate workflow based on the institution
    workflow_class = WORKFLOWS[format]
    workflow = workflow_class(path_out, path_csl, subset)
    workflow.export()
