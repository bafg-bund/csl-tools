"""
Main function to process MS2 data files from various formats.

Process Classes:
    mbank   : Workflow for MassBank documents.
    mzVault : Workflow for mzVault-based documents.
    libview : Workflow for LibraryView-based documents.
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
    "mbank": MbankProcess,
    "mzvault": MzvaultProcess,
    "libview": LibviewProcess,
}


def process_data(format: str, path_csl: str, path_data: str | list[str], path_config: str, path_extra: str | None = None):
    """
    Executes the appropriate workflow for processing MS2 data files based on the data source type.

    Args:
        format (str)    : Format of files to be processed. Choose from:
            - 'mbank'   : MassBank documents.
            - 'mzVault' : mzVault-based documents.
            - 'libview' : LibraryView-based documents.

        path_csl (str)               : Path to the CSL file.
        path_data (str or list[str]) : File path(s) or directory path containing the MS2 data files to process.
        path_config (str)            : Path to configuration file.
        path_extra (str or None)     : File path to supplementary data (only for format 'libview')
    """
    # Validate all provided file paths
    if isinstance(path_data, (list, tuple)):  # If user selected multiple files
        for fpath in path_data:
            validate_file_path(fpath)
    else:
        validate_file_path(path_data)
    if path_extra:
        validate_file_path(path_extra)
    validate_file_path(path_csl)
    validate_file_path(path_config)

    # Select and execute the appropriate process workflow based on the format
    workflow_class = WORKFLOWS[format]
    workflow = workflow_class(path_csl, path_data, path_config, path_extra)
    workflow.process()
