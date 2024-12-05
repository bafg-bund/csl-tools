# Set configurations and constant for the lanuv process workflow in this file

# NOISE_THRESHOLD = 5000  # Todo: Add noise filtering for files in the future

# How to define institution-specific settings:
# Due to varying data formats we use institutional workflows. Each workflow involves reading data files and extracting
# relevant information. In addition to the extracted data, we need to provide supplemental information that is crucial
# for querying the Collective Spectral Library (CSL) but may not be directly available from the data file.
# To standardize the data across different workflows, two types of variables must be defined:
#
# 1) Identifier for extractable data:
# Use this when the necessary information can be extracted directly from the data files.
#   → Define in var_regex_<institution>.
#
# 2) Fixed variable for non-extractable data:
# Use this when necessary information cannot be extracted from the data files or is fixed (e.g. one instrument name).
#   → Define in var_fix_<institution>.

def var_regex_lanuv():
    """
    Mapping of CSL-relevant variables (keys) to lanuv-specific identifiers (values) for data extraction.

    The identifiers should appear in every "chunk" of the data files! Define them as the shortest (but unique)
    common regular expression (not case-sensitive).
    """
    lanuv_var_regex = {
        'var_comp': 'NAME',                 # Compound Name
        'var_cas': 'CASNO',                 # CAS registry number
        'var_formula': 'FORMULA',           # Molecular formula
        'var_mz': 'PRECURSOR M/Z',          # Precursor m/z
        'var_ce': 'COLLISION ENERGY',       # Collision energy
        'var_ion_mode': 'ION MODE',         # Type of operation mode
        'var_instrument': 'INSTRUMENT',     # Instrument type
        'var_peak': 'MASS SPECTRAL PEAKS',  # Mass spectral peaks
    }
    return lanuv_var_regex


def var_fix_lanuv():
    """
    Mapping of CSL-relevant variables (keys) to lanuv-specific default/fixed information (values).
    The information is currently fixed for this institution or does not appear in the data files (can't be extracted).
    """
    from config import DEFAULT_PAIRS_INST_CHROM
    all_methods = DEFAULT_PAIRS_INST_CHROM
    lanuv_var_fix = {
        'var_chrom_method': all_methods['lanuv'],   # Chromatographic method
        'var_isotope': 'monoisotopic',              # Type of molecular mass # todo: Placeholder. Assumed monoisotopic
        'var_ionization': 'ESI',                    # Ionization type # todo: Placeholder. Assumed 'ESI'
        'var_rt': '99',                             # Retention time # todo: Placeholder.
        'var_inchikey': 'inchikey_placeholder',     # InChIKey  # todo: Placeholder.
        'var_smiles': 'smiles_placeholder',         # Simplified Molecular Line Entry Specification (SMILES) todo: Placeholder.
        'var_col_type': 'Q',                        # Collision type  # todo: Assumed 'Q' based on existing CSL entries
        'var_ce_unit': 'V',                         # Unit for collision energy
    }
    return lanuv_var_fix

# Todo: Unique type of instruments found in testfile:
# ['3200 Q TRAP', '4000 Q TRAP', '5500 Q TRAP', 'Generic Single Quad',
#  'Q TRAP', 'Triple TOF 5600', 'Triple TOF 6600', 'TripleTOF 5600',
#  'TripleTOF 6600', 'ZenoTOF™ 7600 System']
# Todo: Instrument type in CSL: LC-ESI-QTOF TripleTOF 6600 SCIEX


def defaults_lanuv():
    """
    Mapping of lanuv-specific default settings for data processing.
    These settings are expected to never have more than one state within each institutional workflow.
    """
    from utils.sql_utils import inst_code_csl_mapping
    inst_notation_pairs = inst_code_csl_mapping()

    lanuv_defaults = {
        'def_pol_p': 'P',                               # Default identifier for positive ion mode
        'def_pol_n': 'N',                               # Default identifier for positive ion mode
        'def_qf': 'QF',                                 # Default identifier for "Quellfragmente" (precursor ions)
        'def_expg_csl': inst_notation_pairs['lanuv'],   # Default label for experimentGroup.name in CSL
        'def_compg_csl': inst_notation_pairs['lanuv'],  # Default label for compoundGroup.name in CSL
    }
    return lanuv_defaults


def adduct_notation_lanuv():
    """
    Special cases for adduct notation
    Todo: No special adduct notation for lanuv.
    """
    lanuv_spec_adduct = {
    }
    return lanuv_spec_adduct
