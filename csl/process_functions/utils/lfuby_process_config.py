# Set configurations and constant for the lfuby process workflow in this file

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

def var_regex_lfuby():
    """
    Mapping of CSL-relevant parameters (keys) to lfuby-specific identifiers (values) for data extraction.

    The identifiers should appear in every experiment of the data files. Define them as the shortest (but unique)
    common identifier (not case-sensitive).
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


def var_regex_mzvault_old():
    """
    Mapping of CSL-relevant parameters (keys) to mzVault-specific identifiers (values) for data extraction.
    Older mzVault version.

    The identifiers should appear in every experiment of the data files. Define them as the shortest (but unique)
    common identifier (not case-sensitive).
    """
    mzvault_var_regex = {
        'var_comp': 'Name',                # Compound Name
        'var_mz': 'Selected Ion m/z',      # Precursor m/z
        'var_ce': 'Collision_energy',      # Collision energy
        'var_ion_mode': 'MS:1000130',      # Type of operation mode
        'var_rt': 'RetentionTime',         # Retention time
        'var_inchikey': 'InChiKey',        # InChIKey
        'var_formula': 'Formula',          # Molecular formula
        'var_cas': 'CASNo',                # CAS registry number
        'var_smiles': 'Smiles',            # Simplified Molecular Line Entry Specification (SMILES)
        'var_peak': 'MS:1009006',          # Mass spectral peaks
        'var_compgroup': 'CompoundClass',  # Compound group
    }
    return mzvault_var_regex


def var_fix_lfuby():
    """
    Mapping of CSL-relevant variables (keys) to lfuby-specific default/fixed information (values).
    The information is currently fixed for this format or does not appear in the data files (can't be extracted).
    """
    lfuby_var_fix = {
        'var_adduct': None,                        # Adduct
        'var_inchi': None,                         # InChI
        'var_accession': None,                     # Accession string (used in MassBank)
        'var_ces': None                            # Collision energy spread
    }
    return lfuby_var_fix


def defaults_lfuby():
    """
    Mapping of lfuby-specific default settings for data processing.
    These settings are expected to never have more than one state within each process workflow.
    """
    lfuby_defaults = {
        'def_pol_p': 'positive',  # Default identifier for positive ion mode
        'def_pol_n': 'negative',  # Default identifier for positive ion mode
        'def_qf': 'QF',           # Default identifier for precursor ions ("Quellfragmente")
    }
    return lfuby_defaults


def defaults_mzvault_old():
    """
    Mapping of mzVault-specific default settings for data processing.
    Older mzVault version.
    These settings are expected to never have more than one state within each process workflow.
    """
    mzvault_old_defaults = {
        'def_pol_p': 'Positive scan',  # Default identifier for positive ion mode
        'def_pol_n': 'Negative scan',  # Default identifier for positive ion mode
        'def_qf': 'QF',                # Default identifier for precursor ions ("Quellfragmente")
    }
    return mzvault_old_defaults
