# Set configurations and constants for the process workflow in this file

# 1) Parameters that can be identified and extracted from the data files
#    → Define here in par_regex_<software>.
# 2) Parameters that can not be extracted from the data files, but do not change across data files.
#    → Define here in par_fix_<software>.
# 3) Defaults for identifying software-specific variables
#    → Define here in defaults_<software>.
# 4) Parameters that are not software-specific, are constant within one import process, and are not software-specific.
#    → Define in config.yaml file that needs to be provided. See tests/fixtures/import/test_config for examples.

def par_regex_mzvault():
    """
    Mapping of CSL-relevant parameters (keys) to mzVault-specific identifiers (values) for data extraction.

    The identifiers should appear in every experiment of the data files. Define them as the shortest (but unique)
    common identifier (not case-sensitive).

    mzVault version 2.3.64.0
    """
    mzvault_par_regex = {
        'par_comp': 'Name',                # Compound name
        'par_mz': 'PrecursorMz',           # Precursor m/z
        'par_ce': 'Collision_energy',      # Collision energy
        'par_ionization': 'Ionization',    # Ionization type
        'par_ion_mode': 'IonMode',         # Type of operation mode
        'par_rt': 'RetentionTime',         # Retention time
        'par_inchikey': 'InChiKey',        # InChIKey
        'par_formula': 'Formula',          # Molecular formula
        'par_cas': 'CASNo',                # CAS registry number
        'par_smiles': 'Smiles',            # Simplified Molecular Line Entry Specification (SMILES)
        'par_peak': 'Peak',                # Mass spectral peaks
        'par_compgroup': 'CompoundClass',  # Compound group
    }
    return mzvault_par_regex


def par_regex_mzvault_old():
    """
    Mapping of CSL-relevant parameters (keys) to mzVault-specific identifiers (values) for data extraction.

    The identifiers should appear in every experiment of the data files. Define them as the shortest (but unique)
    common identifier (not case-sensitive).

    mzVault version 2.3.45.15
    """
    mzvault_par_regex = {
        'par_comp': 'Name',                # Compound Name
        'par_mz': 'Selected Ion m/z',      # Precursor m/z
        'par_ce': 'Collision_energy',      # Collision energy
        'par_ion_mode': 'MS:1000130',      # Type of operation mode
        'par_rt': 'RetentionTime',         # Retention time
        'par_inchikey': 'InChiKey',        # InChIKey
        'par_formula': 'Formula',          # Molecular formula
        'par_cas': 'CASNo',                # CAS registry number
        'par_smiles': 'Smiles',            # Simplified Molecular Line Entry Specification (SMILES)
        'par_peak': 'MS:1009006',          # Mass spectral peaks
        'par_compgroup': 'CompoundClass',  # Compound group
    }
    return mzvault_par_regex


def par_fix_mzvault():
    """
    Mapping of CSL-relevant parameters (keys) to mzVault-specific default/fixed information (values).
    These parameters are non-extractable and do not change across data files (software-specific).
    """
    mzvault_par_fix = {
        'par_adduct': None,     # Adduct
        'par_inchi': None,      # InChI
        'par_accession': None,  # Accession string (used in MassBank)
        'par_ces': None         # Collision energy spread
    }
    return mzvault_par_fix


def defaults_mzvault():
    """
    Mapping of mzVault-specific default settings for data processing.
    These settings are expected to not change with the software version.

    mzVault version 2.3.64.0
    """
    mzvault_defaults = {
        'def_pol_p': 'positive',  # Default identifier for positive ion mode
        'def_pol_n': 'negative',  # Default identifier for positive ion mode
        'def_qf': 'QF',           # Default identifier for precursor ions ("Quellfragmente")
    }
    return mzvault_defaults


def defaults_mzvault_old():
    """
    Mapping of mzVault-specific default settings for data processing.
    These settings are expected to not change with the software version.

    mzVault version 2.3.45.15
    """
    mzvault_old_defaults = {
        'def_pol_p': 'Positive scan',  # Default identifier for positive ion mode
        'def_pol_n': 'Negative scan',  # Default identifier for positive ion mode
        'def_qf': 'QF',                # Default identifier for precursor ions ("Quellfragmente")
    }
    return mzvault_old_defaults
