# Set configurations and constants for the process workflow in this file

# 1) Parameters that can be identified and extracted from the data files
#    → Define here in par_regex_<software>.
# 2) Parameters that can not be extracted from the data files, but do not change across data files.
#    → Add to par_fix in `add_fixed_variables`.
# 3) Defaults for identifying software-specific variables
#    → Define here in defaults_<software>.
# 4) Parameters that are not software-specific, are constant within one import process, and are not software-specific.
#    → Define in config.yaml file that needs to be provided. See tests/fixtures/import/test_config for examples.

def par_regex_gcdata():
    """
    Mapping of CSL-relevant parameters (keys) to specific identifiers (values) for GC data extraction.

    The identifiers should appear in every experiment of the data files. Define them as the shortest (but unique)
    common identifier (not case-sensitive).

    """
    gcdata_par_regex = {
        'par_comp': 'Name',                  # Compound name
        'par_mz': 'PrecursorMz',             # Precursor m/z
        'par_ion_mode': 'IonMode',           # Type of operation mode
        'par_rt': 'RetentionTime',           # Retention time
        'par_inchikey': 'InChiKey',          # InChIKey
        'par_formula': 'Formula',            # Molecular formula
        'par_cas': 'CASNo',                  # CAS registry number
        'par_smiles': 'Smiles',              # Simplified Molecular Line Entry Specification (SMILES)
        'par_peak': 'Peak',                  # Mass spectral peaks
        'par_compgroup': 'CompoundClass',    # Compound group
        'par_ee': 'ElectronEnergy',          # Electron Energy
        'par_ee_unit': 'ElectronEnergyUnit', # Electron Energy Unit
        'par_pc_id': 'PC_ID',                # PubChem Identifier
        'par_rt_ind': 'RetentionIndex',      # Retention time index
    }
    return gcdata_par_regex


def defaults_gcdata():
    """
    Mapping of specific default settings for GC data processing.
    These settings are expected to not change with the software version.

    """
    gcdata_defaults = {
        'def_pol_p': 'positive',  # Default identifier for positive ion mode
        'def_pol_n': 'negative',  # Default identifier for positive ion mode
        'def_qf': 'QF',           # Default identifier for precursor ions ("Quellfragmente")
    }
    return gcdata_defaults
