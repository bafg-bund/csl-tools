"""
Main function to export CSL data as various formats.

Export Classes:
    txt   : Workflow for exporting the CSL as a merged txt file.
    envi  : Workflow for exporting the CSL as a target list usable for envimass.
    mbank : Workflow for exporting the CSL for massbank.

    MassBank: 

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


def run_export_workflow(format_out, path_out, path_csl):
    """
    Executes the appropriate workflow for exporting CSL data as various formats.

    Args:
        format_out (str) : Export format.
        path_out (str)   : Path to export directory.
        path_csl (str)   : Path to the CSL file.
    """

    # Validate the provided file paths
    validate_file_path(path_csl)
    validate_file_path(path_out)

    # Select and execute the appropriate workflow based on the institution
    workflow_class = WORKFLOWS[format_out]
    workflow = workflow_class(path_out, path_csl)
    workflow.export()
