# Set configurations and constant for the lanuk process workflow in this file

# How to define institution-specific settings:
# Todo: Note: Will be updated to software-specific processing in the future
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

def var_regex_lanuk():
    """
    Mapping of CSL-relevant variables (keys) to lanuk-specific identifiers (values) for data extraction.

    The identifiers should appear in every "chunk" of the data files! Define them as the shortest (but unique)
    common identifier (not case-sensitive).

    Note: InChIKey (var_inchikey), InChI (var_inchi) and SMILES (var_smiles) are calculated from the molblock and
    retention time (var_rt) is extracted from supplementary data.
    """
    lanuk_var_regex = {
        'var_molblock': 'V2000',               # Molblock
        'var_comp': 'NAME',                    # Compound Name
        'var_cas': 'CASNO',                    # CAS registry number
        'var_formula': 'FORMULA',              # Molecular formula
        'var_mz': 'PRECURSOR M/Z',             # Precursor m/z
        'var_ce': 'COLLISION ENERGY',          # Collision energy
        'var_ces': 'COLLISION ENERGY SPREAD',  # Collision energy spread
        'var_ion_mode': 'ION MODE',            # Type of operation mode
        'var_instrument': 'INSTRUMENT',        # Instrument name
        'var_peak': 'MASS SPECTRAL PEAKS',     # Mass spectral peaks
    }
    return lanuk_var_regex


def var_fix_lanuk():
    """
    Mapping of CSL-relevant variables (keys) to lanuk-specific default/fixed information (values).
    The information is currently fixed for this format or does not appear in the data files (can't be extracted).
    """
    lanuk_var_fix = {
        'var_compgroup': None,                         # Compound group
        'var_adduct': None,                            # Adduct
        'var_accession': None,                         # Accession string (used in MassBank)
    }
    return lanuk_var_fix


def defaults_lanuk():
    """
    Mapping of lanuk-specific default settings for data processing.
    These settings are expected to never have more than one state within each process workflow.
    """
    lanuk_defaults = {
        'def_pol_p': 'P',  # Default identifier for positive ion mode
        'def_pol_n': 'N',  # Default identifier for positive ion mode
        'def_qf': 'QF',    # Default identifier for precursor ions ("Quellfragmente")
    }
    return lanuk_defaults
