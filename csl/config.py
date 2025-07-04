# Set default configurations here

import os

# Python package version
CSLTOOLS_VERSION = '0.1.0.dev1'

# Root directory of the project
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dictionary with pairs of institution and chromatographic method
# If institutions are added or modified, the respective mappings need to be changed here and in the following sections:
# + Mapping for RT models in rtscan_functions.update_rtscan.py
# + Mapping of institution code to institution notation in utils.sql_utils.py (inst_code_csl_mapping)
# Todo: Change chrom. method names in CSL, then update here (see below)
DEFAULT_PAIRS_INST_CHROM = {
    'bfg': 'dx.doi.org/10.1016/j.chroma.2015.11.014',  # Todo: Change to bfg_nts_rp1
    'uba': 'uba_nts_rp1',
    'lfuby': 'lfu_nts_rp1', # Todo: Change to lfuby_nts_rp1
    'lanuk': 'lanuv_nts',  # Todo: Change to lanuk_nts
    'lubw': 'lubw_nts_rp1'
}
