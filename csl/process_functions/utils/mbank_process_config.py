def var_regex_mbank():
    """
    Mapping of CSL-relevant parameters (keys) to mbank-specific identifiers (values) for data extraction.

    The identifiers should appear in every experiment of the data files. Define them as the shortest (but unique)
    common identifier (not case-sensitive).
    """
    mbank_var_regex = {
        # Relevant in CSL and mandatory in MassBank
        'var_comp': 'CH\\$NAME:',                                      # Compound name
        'var_compgroup': 'CH\\$COMPOUND_CLASS:',                       # Compound group
        'var_formula': 'CH\\$FORMULA:',                                # Molecular formula
        'var_smiles': 'CH\\$SMILES:',                                  # SMILES code
        'var_inchi': 'CH\\$IUPAC:',                                    # InChI
        'var_instrument': 'AC\\$INSTRUMENT:',                          # Instrument name
        'var_instrument_type': 'AC\\$INSTRUMENT_TYPE:',                # Instrument type
        'var_ion_mode': 'AC\\$MASS_SPECTROMETRY: ION_MODE',            # Type of operation mode
        'var_peak': 'PK\\$PEAK:',                                      # Mass spectral peaks

        # Relevant in CSL but not mandatory in MassBank
        'var_inchikey': 'CH\\$LINK: INCHIKEY',                         # InChIKey
        'var_cas': 'CH\\$LINK: CAS',                                   # CAS registry number
        'var_ce': 'AC\\$MASS_SPECTROMETRY: COLLISION_ENERGY',          # Collision energy
        'var_col_type': 'AC\\$MASS_SPECTROMETRY: FRAGMENTATION_MODE',  # Collision type / Fragmentation mode
        'var_ionization': 'AC\\$MASS_SPECTROMETRY: IONIZATION',        # Ionization type
        'var_rt': 'AC\\$CHROMATOGRAPHY: RETENTION_TIME',               # Retention time
        'var_mz': 'MS\\$FOCUSED_ION: PRECURSOR_M/Z',                   # Precursor m/z
        'var_adduct': 'MS\\$FOCUSED_ION: PRECURSOR_TYPE',              # Adduct

        # Optional in CSL but mandatory in MassBank
        'var_accession': 'ACCESSION:',                                 # MassBank accession string
    }
    return mbank_var_regex


def var_fix_mbank():
    """
    Mapping of CSL-relevant variables (keys) to mbank-specific default/fixed information (values).
    The information is currently fixed for this format or does not appear in the data files (can't be extracted).
    """
    mbank_var_fix = {
        'var_ces': None                 # Collision energy spread
    }
    return mbank_var_fix


def defaults_mbank():
    """
    Mapping of mbank-specific default settings for data processing.
    These settings are expected to never have more than one state within each process workflow.
    """
    mbank_defaults = {
        'def_pol_p': 'POSITIVE',  # Default identifier for positive ion mode
        'def_pol_n': 'NEGATIVE',  # Default identifier for positive ion mode
        'def_qf': None,           # Default identifier for precursor ions ("Quellfragmente")
    }
    return mbank_defaults
