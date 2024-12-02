# Set configurations and constant for the lubw process workflow in this file

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

def var_regex_lubw():
    """
    Define variables for data extraction.
    Variables are not case-sensitive. Set to shortest (but unique) common variable across all lubw file types.
    """
    lubw_var_regex = {
        'var_comp': 'Name',            # Compound Name
        'var_mz': 'Selected Ion m/z',  # Precursor m/z
        'var_ce': 'Collision_energy',  # Collision energy
        'var_ion_mode': 'MS:1000130',  # Type of operation mode
        'var_rt': 'RetentionTime',     # Retention time
        'var_inchikey': 'InChiKey',    # InChIKey
        'var_formula': 'Formula',      # Molecular formula
        'var_cas': 'CASNo',            # CAS registry number
        'var_smiles': 'Smiles',        # Simplified Molecular Line Entry Specification (SMILES)
        'var_peak': 'MS:1009006',      # Mass spectral peaks
    }
    return lubw_var_regex


def var_fix_lubw():
    """
    Mapping of CSL-relevant variables (keys) to lubw-specific default/fixed information (values).
    The information is currently fixed for this institution or does not appear in the data files (can't be extracted).
    """
    from config import DEFAULT_PAIRS_INST_CHROM
    all_methods = DEFAULT_PAIRS_INST_CHROM

    lubw_var_fix = {
        'var_chrom_method': all_methods['lubw'],        # Chromatographic method
        'var_instrument': 'LC-ESI-Orbitrap QExactive',  # Instrument type
        'var_isotope': 'monoisotopic',                  # Type of molecular mass
        'var_col_type': 'HCD',                          # Collision type
        'var_ce_unit': 'V',                             # Unit for collision energy
        'var_ionization': 'ESI',                        # Ionization type
    }
    return lubw_var_fix


def defaults_lubw():
    """
    Mapping of lubw-specific default settings for data processing.
    These settings are expected to never have more than one state within each institutional workflow.
    """
    from utils.sql_utils import inst_code_csl_mapping
    inst_notation_pairs = inst_code_csl_mapping()

    lubw_defaults = {
        'def_pol_p': 'Positive scan',                  # Default identifier for positive ion mode
        'def_pol_n': 'Negative scan',                  # Default identifier for positive ion mode
        'def_qf': 'QF',                                # Default identifier for "Quellfragmente" (precursor ions)
        'def_expg_csl': inst_notation_pairs['lubw'],   # Default label for experimentGroup.name in CSL
        'def_compg_csl': inst_notation_pairs['lubw'],  # Default label for compoundGroup.name in CSL
    }
    return lubw_defaults


def adduct_notation_lubw():
    """
    Special cases for adduct notation
    Todo: No special adduct notation for lubw.
    """
    lubw_spec_adduct = {
    }
    return lubw_spec_adduct
