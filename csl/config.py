# Set default configurations here

import os

# Python package version
CSLTOOLS_VERSION = '0.1.0.dev1'

# Root directory of the project
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dictionary with pairs of institution and chromatographic method
# If institutions are added or modified, the respective mappings need to be changed here and in the following sections:
# + Mapping for RT models in rtscan_functions.check_rtscan.py
DEFAULT_PAIRS_INST_CHROM = {
    'bfg': 'bfg_nts_rp1',
    'uba': 'uba_nts_rp1',
    'lfuby': 'lfuby_nts_rp1',
    'lanuk': 'lanuk_nts',
    # 'lubw': 'lubw_nts_rp1'  # Todo: activate once we have the data model
}
