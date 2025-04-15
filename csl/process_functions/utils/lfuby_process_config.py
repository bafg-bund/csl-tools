# Set configurations and constant for the lfuby process workflow in this file

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

def var_regex_lfuby():
    """
    Mapping of CSL-relevant parameters (keys) to lfuby-specific identifiers (values) for data extraction.

    The identifiers should appear in every experiment of the data files. Define them as the shortest (but unique)
    common regular expression (not case-sensitive).
    """
    lfuby_var_regex = {
        'var_comp': 'Name',               # Compound name
        'var_mz': 'PrecursorMz',          # Precursor m/z
        'var_ce': 'Collision_energy',     # Collision energy
        'var_ionization': 'Ionization',   # Ionization type
        'var_ion_mode': 'IonMode',        # Type of operation mode
        'var_rt': 'RetentionTime',        # Retention time
        'var_inchikey': 'InChiKey',       # InChIKey
        'var_formula': 'Formula',         # Molecular formula
        'var_cas': 'CASNo',               # CAS registry number
        'var_smiles': 'Smiles',           # Simplified Molecular Line Entry Specification (SMILES)
        'var_peak': 'Peak',               # Mass spectral peaks
        'var_compgroup': 'CompoundClass', # Compound group
    }
    return lfuby_var_regex


def var_fix_lfuby():
    """
    Mapping of CSL-relevant variables (keys) to lfuby-specific default/fixed information (values).
    The information is currently fixed for this format or does not appear in the data files (can't be extracted).
    """
    from config import DEFAULT_PAIRS_INST_CHROM
    all_methods = DEFAULT_PAIRS_INST_CHROM

    lfuby_var_fix = {
        'var_chrom_method': all_methods['lfuby'],       # Chromatographic method
                                                        # Todo: chrom_method should be changed to lfuby in raw data
        'var_instrument': 'LC-ESI-Orbitrap QExactive',  # Instrument type
        'var_isotope': 'monoisotopic',                  # Type of molecular mass
        'var_col_type': 'HCD',                          # Collision type
        'var_ce_unit': 'V',                             # Unit for collision energy
    }
    return lfuby_var_fix


def defaults_lfuby():
    """
    Mapping of lfuby-specific default settings for data processing.
    These settings are expected to never have more than one state within each process workflow.
    """
    from utils.sql_utils import inst_code_csl_mapping
    inst_notation_pairs = inst_code_csl_mapping()

    lfuby_defaults = {
        'def_pol_p': 'positive',                        # Default identifier for positive ion mode
        'def_pol_n': 'negative',                        # Default identifier for positive ion mode
        'def_qf': 'QF',                                 # Default identifier for "Quellfragmente" (precursor ions)
        'def_expg_csl': inst_notation_pairs['lfuby'],   # Default label for experimentGroup.name in CSL
        'def_compg_csl': inst_notation_pairs['lfuby'],  # Default label for compoundGroup.name in CSL
    }
    return lfuby_defaults


def adduct_notation_lfuby():
    """
    Special cases for adduct notation
    Define special cases in the below dictionary if they deviate from standard adduct notation convention
    Standard adduct notation convention is: "[M+{adduct_name}]+" for positive ion mode
    and "[M-{adduct_name}]-" for negative ion mode. E.g.: "[M+NH4]+" for Desmedipham_NH4 for positive polarity.
    """
    lfuby_spec_adduct = {
        'cation': '[M]+',
        'Ethylamin': '[M+C2H7N+H]+',
        'FA': '[M+HCOO-]-',
        'NaFA': '[M+NaCOO-]-',
    }
    return lfuby_spec_adduct


# Todo: Whitelist for adducts
