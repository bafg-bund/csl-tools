# Set default configurations here
import os

# Python package version
CSLTOOLS_VERSION = '1.0.0'

# Root directory of the project
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dictionary with pairs of data source and chromatographic method
# If data sources are added or modified, the respective mappings need to be changed here and in rtscan_functions.
DEFAULT_PAIRS_INST_CHROM = {
    'bfg': 'bfg_nts_rp1',
    'uba': 'uba_nts_rp1',
    'lfuby': 'lfuby_nts_rp1',
    'lanuk': 'lanuk_nts',
    # 'lubw': 'lubw_nts_rp1'  # Todo: activate once RT model is implemented
}
