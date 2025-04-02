# Set default configurations here

import os

# Python package version
pycsl_version = '0.1.0.dev1'

# Default paths
DEFAULT_CSL_PATH = "C:/Users/lessmann/Data/collective-spectral-library/csl/CSL_v25.0.db"
# Todo: Currently defaults to my local version. Should be handled differently later.
#  For now, please simply specify it in your commands (see Readme.md)

# Root directory of the project
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dictionary with pairs of institution and chromatographic method
# If institutions are added or modified, the respective mappings need to be changed here and in the following sections:
# + Mapping for RT models in rtscan_functions.update_rtscan.py
# + Mapping of institution code to institution notation in utils.sql_utils.py (inst_code_csl_mapping)
DEFAULT_PAIRS_INST_CHROM = {
    'bfg': 'dx.doi.org/10.1016/j.chroma.2015.11.014',
    'uba': 'uba_nts_rp1',
    'lfuby': 'lfu_nts_rp1',
    'lanuv': 'lanuv_nts',
    'lubw': 'lubw_nts_rp1'
}
