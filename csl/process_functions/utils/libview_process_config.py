# Set configurations and constants for the process workflow in this file

# 1) Parameters that can be identified and extracted from the data files
#    → Define here in par_regex_<software>.
# 2) Parameters that can not be extracted from the data files, but do not change across data files or are calculated from another parameter.
#    → Add to par_fix in `add_fixed_variables`.
# 3) Defaults for identifying software-specific variables
#    → Define here in defaults_<software>.
# 4) Parameters that are not software-specific, are constant within one import process, and are not software-specific.
#    → Define in config.yaml file that needs to be provided. See tests/fixtures/import/test_config for examples.

def par_regex_libview():
    """
    Mapping of CSL-relevant parameters (keys) to LibrayView-specific identifiers (values) for data extraction.

    The identifiers should appear in every "chunk" of the data files. Define them as the shortest (but unique)
    common identifier (not case-sensitive).

    LibraryView-specific: InChIKey (par_inchikey), InChI (par_inchi) and SMILES (par_smiles) are calculated from
    the molblock and retention time (par_rt) is extracted from supplementary data.
    """
    libview_par_regex = {
        'par_molblock': 'V2000',                # Molblock
        'par_comp': 'NAME',                     # Compound Name
        'par_cas': 'CASNO',                     # CAS registry number
        'par_formula': 'FORMULA',               # Molecular formula
        'par_mz': 'PRECURSOR M/Z',              # Precursor m/z
        'par_ce': 'COLLISION ENERGY',           # Collision energy
        'par_ces': 'COLLISION ENERGY SPREAD',   # Collision energy spread
        'par_ion_mode': 'ION MODE',             # Type of operation mode
        'par_instrument': 'INSTRUMENT',         # Instrument name
        'par_peak': 'MASS SPECTRAL PEAKS',      # Mass spectral peaks
        'par_exact_mass': 'MONOISOTOPIC MASS',  # Exact mass
    }
    return libview_par_regex


def defaults_libview():
    """
    Mapping of LibrayView-specific default settings for data processing.
    These settings are expected to not change with the software version.
    """
    libview_defaults = {
        'def_pol_p': 'P',  # Default identifier for positive ion mode
        'def_pol_n': 'N',  # Default identifier for positive ion mode
        'def_qf': 'QF',    # Default identifier for precursor ions ("Quellfragmente")
    }
    return libview_defaults
