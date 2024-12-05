"""
Main function to process MS2 data files from various institutions.

Workflow Classes:
    LfubyWorkflow : Workflow for 'lfuby' (Bayerisches Landesamt für Umwelt).
    BfgWorkflow   : Workflow for 'bfg' (Bundesanstalt für Gewässerkunde).
    LanuvWorkflow : Workflow for 'lanuv' (Landesamt für Natur, Umwelt und Verbraucherschutz Nordrhein-Westfalen).
    LubwWorkflow  : Workflow for 'lubw' (Landesanstalt für Umwelt Baden-Württemberg).
    UbaWorkflow   : Workflow for 'uba' (Umweltbundesamt).
"""

import os.path
from datetime import datetime
from utils import validate_file_path, setup_logger
from process_functions import *
from config import ROOT_DIR

# Setup logs folder and set the root logger
fname = datetime.now().strftime('%Y%m%d_%H%M%S') + '_log'
log_dir = os.path.join(ROOT_DIR, 'logs')
os.makedirs(log_dir, exist_ok=True)
log_fpath = os.path.join(log_dir, fname)
setup_logger(log_fpath)  # Sets basic logger configuration and adds stream handlers

# Define workflow dictionary
WORKFLOWS = {
    "lfuby": LfubyWorkflow,
    "bfg": BfgWorkflow,
    "lanuv": LanuvWorkflow,
    "lubw": LubwWorkflow,
    "uba": UbaWorkflow
}


def run_process_workflow(inst, path_data, path_csl):
    """
    Executes the appropriate workflow for processing MS2 data files based on the institution type.

    Args:
        inst (str)                      : Institution type, used to select the appropriate workflow.
        path_data (str or list of str)  : File path(s) or directory path containing the MS2 data files to process.
        path_csl (str)                  : Path to the CSL file.
    """

    # Validate the provided file path(s)
    if isinstance(path_data, (list, tuple)):  # If user selected multiple files
        for fpath in path_data:
            validate_file_path(fpath)
    else:
        validate_file_path(path_data)

    validate_file_path(path_csl)

    # Select and execute the appropriate workflow based on the institution
    workflow_class = WORKFLOWS[inst]
    workflow = workflow_class(path_data, path_csl)
    workflow.process()
