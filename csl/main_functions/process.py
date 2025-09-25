"""
Main function to process MS2 data files from various formats.

Process Classes:
    lfuby : Workflow for 'lfuby' (Bayerisches Landesamt für Umwelt).
    lanuk : Workflow for 'lanuk' (Landesamt für Natur, Umwelt und Klima Nordrhein-Westfalen).
    lubw  : Workflow for 'lubw' (Landesanstalt für Umwelt Baden-Württemberg).
    mbank : Workflow for MassBank documents.
    Todo: In the future import/processing will be changed to software-specific workflows only
"""
from csl.utils import validate_file_path, setup_logger
from csl.process_functions import *
from csl.config import ROOT_DIR

import os.path
from datetime import datetime

# Setup logs folder and set the root logger
fname = datetime.now().strftime('%Y%m%d_%H%M%S') + '_log'
log_dir = os.path.join(ROOT_DIR, 'logs')
os.makedirs(log_dir, exist_ok=True)
log_fpath = os.path.join(log_dir, fname)
setup_logger(log_fpath)  # Sets basic logger configuration and adds stream handlers

# Define process workflow dictionary
WORKFLOWS = {
    "lfuby": LfubyProcess,
    "lanuk": LanukProcess,
    "lubw": LubwProcess,
    "mbank": MbankProcess,
}


def process_data(format: str, path_csl: str, path_data: str or list[str]):
    """
    Executes the appropriate workflow for processing MS2 data files based on the data source type.

    Args:
        format (str)    : Format of files to be processed. Choose from:
            - 'lfuby'   : Files from data source 'lfuby' (Bavarian Environment Agency).
            - 'lanuk'   : Files from data source 'lanuk' (North Rhine-Westphalia Office of Nature, Environment and Climate).
            - 'lubw'    : Files from data source 'lubw' (Baden-Württemberg State Institute for the Environment).
            - 'mbank'   : MassBank documents.
        path_csl (str)  : Path to the CSL file.
        path_data (str or list[str]) : File path(s) or directory path containing the MS2 data files to process.
    """
    # Validate the provided file path(s)
    if isinstance(path_data, (list, tuple)):  # If user selected multiple files
        for fpath in path_data:
            validate_file_path(fpath)
    else:
        validate_file_path(path_data)

    validate_file_path(path_csl)

    # Select and execute the appropriate process workflow based on the format
    workflow_class = WORKFLOWS[format]
    workflow = workflow_class(path_csl, path_data)
    workflow.process()
