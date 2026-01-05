# Set configurations and constants for the process workflow in this file

# 1) Parameters that can be identified and extracted from the data files
#    → Define here in par_regex_<software>.
# 2) Parameters that can not be extracted from the data files, but do not change across data files.
#    → Define here in par_fix_<software>.
# 3) Defaults for identifying software-specific variables
#    → Define here in defaults_<software>.
# 4) Parameters that are not software-specific, are constant within one import process, and are not software-specific.
#    → Define in config.yaml file that needs to be provided. See tests/fixtures/import/test_config for examples.

def par_regex_mbank():
    """
    Mapping of CSL-relevant parameters (keys) to MassBank-specific identifiers (values) for data extraction.

    The identifiers should appear in every experiment of the data files. Define them as the shortest (but unique)
    common identifier (not case-sensitive).
    """
    mbank_par_regex = {
        # Relevant in CSL and mandatory in MassBank
        'par_comp': 'CH\\$NAME:',                                      # Compound name
        'par_compgroup': 'CH\\$COMPOUND_CLASS:',                       # Compound group
        'par_formula': 'CH\\$FORMULA:',                                # Molecular formula
        'par_smiles': 'CH\\$SMILES:',                                  # SMILES code
        'par_inchi': 'CH\\$IUPAC:',                                    # InChI
        'par_instrument': 'AC\\$INSTRUMENT:',                          # Instrument name
        'par_instrument_type': 'AC\\$INSTRUMENT_TYPE:',                # Instrument type
        'par_ion_mode': 'AC\\$MASS_SPECTROMETRY: ION_MODE',            # Type of operation mode
        'par_peak': 'PK\\$PEAK:',                                      # Mass spectral peaks

        # Relevant in CSL but not mandatory in MassBank
        'par_inchikey': 'CH\\$LINK: INCHIKEY',                         # InChIKey
        'par_cas': 'CH\\$LINK: CAS',                                   # CAS registry number
        'par_ce': 'AC\\$MASS_SPECTROMETRY: COLLISION_ENERGY',          # Collision energy
        'par_col_type': 'AC\\$MASS_SPECTROMETRY: FRAGMENTATION_MODE',  # Collision type / Fragmentation mode
        'par_ionization': 'AC\\$MASS_SPECTROMETRY: IONIZATION',        # Ionization type
        'par_rt': 'AC\\$CHROMATOGRAPHY: RETENTION_TIME',               # Retention time
        'par_mz': 'MS\\$FOCUSED_ION: PRECURSOR_M/Z',                   # Precursor m/z
        'par_adduct': 'MS\\$FOCUSED_ION: PRECURSOR_TYPE',              # Adduct

        # Optional in CSL but mandatory in MassBank
        'par_accession': 'ACCESSION:',                                 # MassBank accession string

        # Other
        'par_exact_mass': 'CH\\$EXACT_MASS:'                           # Exact mass
    }
    return mbank_par_regex


def par_fix_mbank():
    """
    Mapping of CSL-relevant parameters (keys) to MassBank-specific default/fixed information (values).
    These parameters are non-extractable and do not change across data files (software-specific).
    """
    mbank_par_fix = {
        'par_ces': None  # Collision energy spread
    }
    return mbank_par_fix


def defaults_mbank():
    """
    Mapping of MassBank-specific default settings for data processing.
    These settings are expected to not change with the software version.
    """
    mbank_defaults = {
        'def_pol_p': 'POSITIVE',  # Default identifier for positive ion mode
        'def_pol_n': 'NEGATIVE',  # Default identifier for positive ion mode
        'def_qf': None,           # Default identifier for precursor ions ("Quellfragmente")
    }
    return mbank_defaults
