# Set configurations and constant for the lanuk process workflow in this file

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

from csl.config import DEFAULT_PAIRS_INST_CHROM
from csl.utils.sql_utils import inst_code_csl_mapping

def var_regex_lanuk():
    """
    Mapping of CSL-relevant variables (keys) to lanuk-specific identifiers (values) for data extraction.

    The identifiers should appear in every "chunk" of the data files! Define them as the shortest (but unique)
    common regular expression (not case-sensitive).
    """
    lanuk_var_regex = {
        'var_comp': 'NAME',                 # Compound Name
        'var_cas': 'CASNO',                 # CAS registry number
        'var_formula': 'FORMULA',           # Molecular formula
        'var_mz': 'PRECURSOR M/Z',          # Precursor m/z
        'var_ce': 'COLLISION ENERGY',       # Collision energy
        'var_ion_mode': 'ION MODE',         # Type of operation mode
        'var_instrument': 'INSTRUMENT',     # Instrument name
        'var_peak': 'MASS SPECTRAL PEAKS',  # Mass spectral peaks
    }
    return lanuk_var_regex


def var_fix_lanuk():
    """
    Mapping of CSL-relevant variables (keys) to lanuk-specific default/fixed information (values).
    The information is currently fixed for this format or does not appear in the data files (can't be extracted).
    """
    all_methods = DEFAULT_PAIRS_INST_CHROM
    inst_notation_pairs = inst_code_csl_mapping()

    lanuk_var_fix = {
        'var_chrom_method': all_methods['lanuk'],      # Chromatographic method
        'var_isotope': 'monoisotopic',                 # Type of molecular mass # todo: Placeholder. Assumed monoisotopic
        'var_ionization': 'ESI',                       # Ionization type # todo: Placeholder. Assumed 'ESI'
        'var_rt': '99',                                # Retention time # todo: Placeholder.
        'var_inchikey': 'inchikey_placeholder',        # InChIKey  # todo: Placeholder.
        'var_smiles': 'smiles_placeholder',            # Simplified Molecular Line Entry Specification (SMILES) todo: Placeholder.
        'var_col_type': 'Q',                           # Collision type  # todo: Assumed 'Q' based on existing CSL entries
        'var_ce_unit': 'V',                            # Unit for collision energy
        'var_compgroup': 'compgroup_placeholder',      # Compound group # todo: Placeholder.
        'var_adduct': None,                            # Adduct
        'var_inchi': None,                             # InChI
        'var_instrument_type': None,                   # Instrument type # todo: see below
        'var_accession': None,                         # Accession string (used in MassBank)
        'var_expg_csl': inst_notation_pairs['lanuk'],  # Default label for experimentGroup.name in CSL
        'var_compg_csl': inst_notation_pairs['lanuk'], # Default label for compoundGroup.name in CSL
    }
    return lanuk_var_fix

# Todo: Unique type of instruments found in testfile:
# ['3200 Q TRAP', '4000 Q TRAP', '5500 Q TRAP', 'Generic Single Quad',
#  'Q TRAP', 'Triple TOF 5600', 'Triple TOF 6600', 'TripleTOF 5600',
#  'TripleTOF 6600', 'ZenoTOF™ 7600 System']
# Todo: Instrument type in CSL: LC-ESI-QTOF TripleTOF 6600 SCIEX


def defaults_lanuk():
    """
    Mapping of lanuk-specific default settings for data processing.
    These settings are expected to never have more than one state within each process workflow.
    """
    lanuk_defaults = {
        'def_pol_p': 'P',                               # Default identifier for positive ion mode
        'def_pol_n': 'N',                               # Default identifier for positive ion mode
        'def_qf': 'QF',                                 # Default identifier for "Quellfragmente" (precursor ions)
    }
    return lanuk_defaults


def adduct_notation_lanuk():
    """
    Special cases for adduct notation
    Todo: No special adduct notation for lanuk.
    """
    lanuk_spec_adduct = {
    }
    return lanuk_spec_adduct
