"""
Main function to export CSL data as various formats.

Export classes:
    mzvault : Workflow for exporting the CSL as a file readable by mzVault (.msp).
    envi    : Workflow for exporting the CSL as a file usable for enviMass (.csv).
    mbank   : Workflow for exporting the CSL as Massbank documents (.txt).
    sqlite  : Workflow for exporting a subset of the CSL as SQLite file (.db).
"""
from csl.utils import validate_file_path, setup_logger
from csl.export_functions import *
from csl.config import ROOT_DIR

import os.path
from datetime import datetime

# Setup logs folder and set the root logger
fname = datetime.now().strftime('%Y%m%d_%H%M%S') + '_log'
log_dir = os.path.join(ROOT_DIR, 'logs')
os.makedirs(log_dir, exist_ok=True)
log_fpath = os.path.join(log_dir, fname)
setup_logger(log_fpath)  # Sets basic logger configuration and adds stream handlers

# Define export workflow dictionary
WORKFLOWS = {
    "mzvault": MzvaultExport,
    "envi": EnviExport,
    "mbank": MbankExport,
    "sqlite": SqliteExport
}


def export_data(format: str, path_csl: str, path_out: str, subset: str or list[str] = 'all'):
    """
    Executes the appropriate workflow for exporting CSL data as various formats.

    Args:
        format (str)   : Export format. Choose from:
            - 'mzvault' : File readable by mzVault (.msp).
            - 'envi'   : File usable for enviMass (.csv).
            - 'mbank'  : MassBank documents (.txt).
            - 'sqlite' : Subset of the CSL as SQLite file (.db).
        path_csl (str) : Path to the CSL file.
        path_out (str) : Path to export directory.
        subset (str or list[str]) : Data source(s), used to subset the CSL data before exporting. Choose from:
            - 'bfg'    : Files from data source 'bfg' (Federal Institute of Hydrology, Koblenz, Germany).
            - 'lfuby'  : Files from data source 'lfuby' (Bavarian Environment Agency, Augsburg, Germany).
            - 'uba'    : Files from data source 'uba' (German Environment Agency, Berlin, Germany).
            - 'all'    : No subsetting (Default).
    """
    # Validate the provided file paths
    validate_file_path(path_csl)
    validate_file_path(path_out)

    # Select and execute the appropriate workflow based on the data source
    workflow_class = WORKFLOWS[format]
    workflow = workflow_class(path_csl, path_out, subset)
    workflow.export()
