# Set default configurations here
import os

# Python package version
CSLTOOLS_VERSION = '1.1.0'

# Root directory of the project
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dictionary with pairs of data source and chromatographic method
# If data sources are added or modified, the respective mappings need to be changed here and in rtscan_functions
DEFAULT_PAIRS_DSOURCE_CHROM = {
    'bfg': 'bfg_nts_rp1',
    'uba': 'uba_nts_rp1',
    'lfuby': 'lfuby_nts_rp1',
    'lanuk': 'lanuk_nts_rp1',
    'lubw': 'lubw_nts_rp1',
    'icpr': 'icpr_nts_rp1',
    'bfg_gc': 'bfg_nts_gc1',  # GC data method is identified by '_gc' substring and filtered accordingly downstream
    # (e.g., excluded from rtscan functions; or different metadata rules)
}

# Dictionary with pairs of instrument name and instrument type as they should appear in the CSL
# Functions as whitelist when importing data
WHITELIST_INSTR_NAME_TYPE = {
    'TripleTOF 5600 SCIEX': 'LC-ESI-QTOF',
    'TripleTOF 6600 SCIEX': 'LC-ESI-QTOF',
    'QExactive Thermo': 'LC-ESI-Orbitrap',
    'Agilent 6500 Series Q-TOF': 'LC-ESI-QTOF',
    'TripleTOF X500R SCIEX': 'LC-ESI-QTOF',
    'ZenoTOF 7600 SCIEX': 'LC-ESI-QTOF',
    'Exploris 240 Thermo': 'LC-ESI-Orbitrap',
    'Exploris 60K Thermo': 'GC-EI-Orbitrap',
}

# Whitelists for various parameters (simple quality assurance)
WHITELIST_IONIZATION_TYPE = ['ESI', 'EI']
WHITELIST_COLLISION_TYPE = ['HCD', 'Q', 'CID', 'in-source']
WHITELIST_ISOTOPE = ['monoisotopic', 'polyisotopic']
WHITELIST_CE_UNIT = ['V']
WHITELIST_EE_UNIT = ['eV']
