from csl.config import (WHITELIST_INSTR_NAME_TYPE, WHITELIST_IONIZATION_TYPE, WHITELIST_COLLISION_TYPE,
                        WHITELIST_ISOTOPE, WHITELIST_CE_UNIT, WHITELIST_EE_UNIT)

def get_file_paths(data_path):
    """
    Returns file paths in correct format.
    Handles different inputs:
        - Single file path (str) : Converted to a list.
        - Multiple file paths (list of str): No change.
        - Path to directory (str) : Returns all valid file paths in the directory and subdirectories.

    Args:
        data_path (str or list of str) : Path of data. Can be a directory or a list of file paths.

    Returns:
        file_paths (list of str) : List of file paths.

    """
    import os

    # Get file paths
    if isinstance(data_path, list):  # User selected file(s) are provided as list of str
        file_paths = data_path
    else:  # Otherwise check if provided path is a directory or a single file
        if os.path.isfile(data_path):
            file_paths = [data_path]
        else:  # If a directory is provided
            # Find all files in directory (also subdirectories)
            file_paths = match_file_paths(data_path, fstr_id=None)
    return file_paths


def match_file_paths(path_dir, fstr_id=None):
    """
    Collects files in a specified dictionary (including subfolders). Can filter filenames based on an identifier string.

    Args:
          path_dir (str)        : Path to file directory (files can be in subdirectories).
          fstr_id (str or None) : (Optional) Common identifier that is present only in the relevant filenames.

    Returns:
          files (list of str) : Full file paths of identified files.
    """
    import os
    import logging

    logger = logging.getLogger(__name__)

    files = []
    for folder, subfolders, filenames in os.walk(path_dir):
        if fstr_id:
            files.extend(os.path.join(folder, filename) for filename in filenames if fstr_id in filename)
        else:
            files.extend(os.path.join(folder, filename) for filename in filenames)

    logger.info(f'Found {len(files)} file(s) in total:')
    for file in files:
        logger.info(file)
    return files


def get_polarity(data_ionmode, pol_p_def, pol_n_def):
    """
    Determines polarity based on default identifier and formats polarity according to CSL requirements.

    Args:
        data_ionmode (str) : Polarity from data.
        pol_p_def (str)    : Default identifier for positive polarity.
        pol_n_def (str)    : Default identifier for negative polarity.

    Returns:
        pol_i (str) : Formatted polarity. Returns None, if the input is invalid.
    """
    if data_ionmode == pol_p_def:
        pol_i = 'pos'
    elif data_ionmode == pol_n_def:
        pol_i = 'neg'
    else:
        pol_i = None
    return pol_i


def get_compound_and_adduct_name(data_comp):
    """
    Extracts and formats compound name and adduct name from the provided character string according to CSL requirements.
    - The expected input format is `CompoundName` or `CompoundName_AdductName`.
    - If only `CompoundName` is provided, the default adduct name `H` is assigned.
    - If the input format is invalid or unexpected, both the compound name and adduct name will return None.

    Args:
        data_comp (str) : Compound name and optionally the adduct name from data. The expected format is `CompoundName`
                          or `CompoundName_AdductName`.

    Returns:
        comp_i (str)      : Formatted compound name. Returns None, if the input is invalid.
        adduct_name (str) : Formatted adduct name. Returns None, if the input is invalid.
    """
    if data_comp:
        data_comp = data_comp.replace("′", "'").replace("`", "'")
        parts = data_comp.split('_')
        if len(parts) == 1:
            comp_i = parts[0].strip()
            adduct_name = 'H'
        elif len(parts) == 2 and not any(len(part) == 0 for part in parts):
            comp_i = parts[0].strip()
            adduct_name = parts[1].strip()
        else:
            comp_i = None
            adduct_name = None
    else:
        comp_i = None
        adduct_name = None
    return comp_i, adduct_name


def format_adduct(adduct_name, spec_adduct, qf_def, pol_i):
    """
    Determines the adduct notation based on the adduct name and polarity according to CSL requirements.
    - For standard cases, the adduct notation follows the format: `[M+{adduct_name}]+` for positive ion mode
      and `[M-{adduct_name}]-` for negative ion mode.
    - If the adduct name corresponds to a precursor ion number (identified by `qf_def`), the notation is:
      `[QF{qfno}]+` or `[QF{qfno}]-`, where `qfno` is the numeric part of the adduct name.
    - Special adduct notations defined in `spec_adduct` override the standard format.

    Args:
        adduct_name (str)  : Adduct name determined by `get_compound_and_adduct_name`.
        spec_adduct (dict) : Dictionary specifying special cases for adduct notations based on certain adduct names.
        qf_def (str)       : Default identifier for precursor ion number ("Quellfragmente").
        pol_i (str)        : Ion polarity, determined by `get_polarity`; Either 'pos' (positive) or 'neg' (negative).

    Returns:
        adduct_i (str) : Formatted adduct notation. Returns None, if the input is invalid.
    """
    import re

    # Adduct name conversion
    adduct_i = None  # Initialize variable
    if not adduct_name or not pol_i:
        adduct_i = None
    else:
        if adduct_name in spec_adduct:
            # Special cases
            adduct_i = spec_adduct[adduct_name]
        elif bool(re.search(r'\[.*]', adduct_name)):  # If adduct name contains brackets
            adduct_i = adduct_name
        elif qf_def and qf_def in adduct_name:
            qf_no = ''.join(char for char in adduct_name if char.isdigit())
            if pol_i == 'pos':
                adduct_i = f"[QF{qf_no}]+"
            elif pol_i == 'neg':
                adduct_i = f"[QF{qf_no}]-"
        else:
            # Standard conversion
            if pol_i == 'pos':
                adduct_i = f"[M+{adduct_name}]+"
            elif pol_i == 'neg':
                adduct_i = f"[M-{adduct_name}]-"
    return adduct_i


def get_collision_energy(data_ce, data_ces, data_ce_unit):
    """
    Formats collision energy (CE) and collision energy spread (CES) values according to CSL requirements.
    - In case of a single CE value: CES is formatted or set to 0 if input is empty.
    - In case of three CE values: CES is calculated and middle CE value is selected.
    - Checks for MassBank-specific format.
    - Negative CE/CES value inputs are converted to positive values.
    - CE unit is matched with whitelist.

    Args:
        data_ce (str or None)  : One or more collision energy values from the data.
        data_ces (str or None) : Collision energy spread from the data.
        data_ce_unit (str or None) : Collision energy unit from the data.

    Returns:
        ce_i (int)      : Primary collision energy (CE) value. If three CE values are provided, `ce_i` will be the
                          value from the middle position.
        ces_i (int)     : Collision energy spread (CES). CES is calculated if multiple CE values are provided.
        ce_unit_i (str) : Collision energy unit.
    """
    import re
    import numpy as np

    if data_ce and data_ce_unit.strip() in WHITELIST_CE_UNIT:
        ce_unit_i = data_ce_unit.strip()
        # Format CE
        str_nrs = re.findall(r'\d+', data_ce)  # Find numbers in string
        int_nrs = list(map(int, str_nrs))  # Convert to list of int
        int_nrs_real = [int_nr for int_nr in int_nrs if int_nr > 0]  # Remove zero

        # In case of a single CE value: formats CES or set to 0 if input is None
        if len(int_nrs_real) == 1:  # One CE
            ce_i = int_nrs_real[0]
            if data_ces:
                ces_i = abs(int(data_ces))
            else:
                ces_i = 0

        # In case of three CE values: calculate CES and select representative CE value
        elif len(int_nrs_real) == 3:  # Three CE
            int_nrs_real.sort()
            ce_i = int_nrs_real[1]  # Middle CE
            # Calculate CES. Check for equal difference in CES.
            ce_diff = np.diff(int_nrs_real)
            ce_diff_unique = np.unique(ce_diff)
            if len(ce_diff_unique) == 1:
                ces_i = abs(int(ce_diff_unique[0]))
            else:  # Non-equal difference in CES
                ce_i = None  # Set to `None` even though CE might be ok.
                ces_i = None
                ce_unit_i = None
        else:  # Unexpected number of CE or MassBank format
            if 'V +/-' in data_ce and len(int_nrs_real) == 2:  # MassBank format
                ce_i = int_nrs_real[0]
                ces_i = int_nrs_real[1]
            else:
                ce_i = None
                ces_i = None
                ce_unit_i = None
    else:  # No ce data or ce unit not on whitelist
        ce_i = None
        ces_i = None
        ce_unit_i = None

    return ce_i, ces_i, ce_unit_i


def get_electron_energy(data_ee, data_ee_unit):
    """
    Formats electron energy (EE) value according to CSL requirements.
    - Only single values allowed
    - Negative CE/CES value inputs are converted to positive values
    - EE unit is matched with whitelist

    Args:
        data_ee (str or None)      : One electron energy value from the data.
        data_ee_unit (str or None) : Electron energy unit from the data.

    Returns:
        ee_i (int)      : Electron energy (EE) value.
        ee_unit_i (str) : Electron energy unit.
    """
    import re

    # Check EE data and EE unit whitelist
    if not data_ee or not data_ee_unit.strip() in WHITELIST_EE_UNIT:
        ee_i = None
        ee_unit_i = None
        return ee_i, ee_unit_i
    else:  # Format EE
        str_nrs = re.findall(r'\d+', data_ee)  # Find numbers in string
        int_nrs = list(map(int, str_nrs))  # Convert to list of int
        int_nrs_real = [int_nr for int_nr in int_nrs if int_nr > 0]  # Remove zero

        # Expect a single EE value
        if len(int_nrs_real) == 1:
            ee_i = int_nrs_real[0]
            ee_unit_i = data_ee_unit.strip()
        else:  # Unexpected number of EE values
            ee_i = None
            ee_unit_i = None

    return ee_i, ee_unit_i


def get_ionization_type(data_ionization):
    """
    Retrieves and returns the ionization type from the provided data.
    - Needs to match the whitelist

    Args:
        data_ionization (str) : Ionization type from the data.

    Returns:
        ionization_i (str) : Ionization type. Returns None, if the input is invalid.
    """
    if data_ionization and data_ionization.strip() in WHITELIST_IONIZATION_TYPE:
        ionization_i = data_ionization.strip()
    else:
        ionization_i = None
    return ionization_i


def get_formula(data_formula):
    """
    Retrieves and returns the formula from the provided data.

    Args:
        data_formula (str) : Formula from the data.

    Returns:
        form_i (str) : Formula. Returns None, if the input is invalid.
    """
    import re
    if data_formula:
        match = re.search(r'\[(.*?)\][+-]?', data_formula)
        if match:
            form_i = match.group(1)
        else:
            form_i = data_formula
    else:
        form_i = None
    return form_i


def get_inchikey(data_inchikey):
    """
    Extracts and returns the full InChIKey and its main component from the provided data.
    Todo: Quality control of InChIKey; e.g. `is.inchikey()`
    Args:
        data_inchikey (str) : InChIKey from the data.

    Returns:
        inchikey_i (str)      : Full InChIKey. Returns None, if the input is invalid.
        inchikey_main_i (str) : Main component of the InChIKey (first segment before the hyphen).
                                Returns None, if the input is invalid.
    """
    if data_inchikey:
        inchikey_i = data_inchikey
        parts = inchikey_i.split('-')
        inchikey_main_i = parts[0].strip()
    else:
        inchikey_i = None
        inchikey_main_i = None
    return inchikey_i, inchikey_main_i


def get_cas(data_cas):
    """
    Checks and returns the CAS (Chemical Abstracts Service) registry number (CAS RN) from the provided data.
    Todo: Quality control of CAS RN; e.g. `is.cas()`
    Args:
        data_cas (str): CAS registry number. It should only contain digits and hyphens.

    Returns:
        cas_i (str): CAS registry number. Returns None, if the input is invalid.
    """
    if data_cas and not any(char.isalpha() for char in data_cas):
        cas_i = data_cas
    else:
        cas_i = None
    return cas_i


def get_smiles(data_smiles):
    """
    Retrieves, validates, and returns the SMILES-string (Simplified Molecular Input Line Entry System) from the
    provided data.

    Args:
        data_smiles (str): SMILES-string from the data.

    Returns:
        smiles_i (str): SMILES-string. Returns None, if the input is invalid.
    """
    from rdkit import Chem

    if not data_smiles:
        return None

    mol = Chem.MolFromSmiles(data_smiles)
    if mol is None:
        return None

    smiles_i = data_smiles
    return smiles_i


def get_inchi_from_smiles(smiles_i):
    """
    Get the InChi from the SMILES code.

    Args:
        smiles_i (str) : SMILES-string

    Returns:
        inchi_i (str) : InChI-string. Returns None, if the input is invalid.
    """
    from rdkit import Chem

    if smiles_i:
        mol = Chem.MolFromSmiles(smiles_i)  # Convert SMILES to RDKit molecule object
        if mol:
            inchi_i = Chem.MolToInchi(mol)  # Convert to InChI
        else:
            inchi_i = None
    else:
        inchi_i = None
    return inchi_i


def get_precursor_mz(data_mz):
    """
    Retrieves the precursor mass-to-charge ratio (m/z) and returns it as a float.

    Args:
        data_mz (str): Precursor mass-to-charge ratio (m/z) as a string from the data.

    Returns:
        mz_i (float): Precursor mass-to-charge ratio (m/z) as a float. Returns None, if the input is invalid.
    """
    try:
        mz_i = float(data_mz)
    except (TypeError, ValueError):
        mz_i = None
    return mz_i


def get_retention_time(data_rt):
    """
    Retrieves and returns the retention time as a float.

    Args:
        data_rt (str, float, int): Retention time from the data.

    Returns:
        rt_i (float): Retention time as a float. Returns None, if the input is empty.
    """
    if data_rt:
        if isinstance(data_rt, str):
            rt_i = float(data_rt.split()[0])
        else:
            rt_i = float(data_rt)
    else:
        rt_i = None

    return rt_i


def  get_retention_time_index(data_rt_ind):
    """
    Retrieves and returns the retention time index as a float.

    Args:
        data_rt_ind (str, float, int): Retention time index from the data.

    Returns:
        rt_ind_i (float): Retention time index as a float. Returns None, if the input is empty.
    """
    try:
        rt_ind_i = float(data_rt_ind)
    except (TypeError, ValueError):
        rt_ind_i = None
    return rt_ind_i


def get_peaks(data_peak):
    """
    Parses and returns peak data as a pandas DataFrame with columns for m/z and intensity.

    Args:
        data_peak (list of str): List of strings, each containing m/z and intensity values separated by spaces.

    Returns:
        spec_i (pd.DataFrame): DataFrame with two columns: 'mz' (mass-to-charge ratio) and 'int' (intensity).
                               Returns an empty DataFrame if no data is provided.
    """
    import pandas as pd

    if not isinstance(data_peak, list):
        data_peak = [data_peak]
    if data_peak and not all(item == '' for item in data_peak):
        split_strings = [s.split()[0:2] for s in data_peak]
        spec_i = pd.DataFrame(split_strings, columns=['mz', 'int'])
    else:
        spec_i = pd.DataFrame()
    return spec_i


def get_compound_group(data_compgroup):
    """
    Extracts the compound groups. Assumes separation of multiple compound groups with ';' or ','.

    Args:
        data_compgroup (str) : Compound group(s) separated by ';' or ','.

    Returns:
        compgroup_i (str)    : Formatted compound group name(s). Returns None, if the input is invalid or empty.
    """
    import re

    if not data_compgroup:
        return None

    parts = re.split(r"[;,]", data_compgroup)
    compgroup_i = [p.strip() for p in parts if p.strip()]

    return compgroup_i or None


def get_collision_type(data_col_type):
    """
    Retrieves and returns the collision type from the provided data.
    - MassBank notation is converted
    - Needs to match the whitelist

    Args:
        data_col_type (str) : Collision type.

    Returns:
        col_type_i (str) : Formatted collision type.
    """
    if data_col_type and data_col_type.strip() in WHITELIST_COLLISION_TYPE:
        if data_col_type == 'CID':  # MassBank notation
            col_type_i = 'Q'
        else:
            col_type_i = data_col_type.strip()
    else:
        col_type_i = None
    return col_type_i


def get_instrument(data_instrument=None, data_instrument_type=None):
    """
    Returns a string representing the instrument identifier.

    Args:
        data_instrument (str) : Instrument name or instrument type + name.
        data_instrument_type (str) : Instrument type.

    Returns:
        instrument_i (str) : Formatted instrument identifier.
    """
    # Normalize inputs
    instr = data_instrument or ""
    instr_type = data_instrument_type or ""
    instr = instr.strip()
    instr_type = instr_type.strip()

    # Check if instrument name contains type
    detected_type = None
    for t in set(WHITELIST_INSTR_NAME_TYPE.values()):
        if instr.startswith(t+" "):
            detected_type = t
            instr = instr[len(t):].strip()

    # Set instrument name
    instr_name = instr if instr in WHITELIST_INSTR_NAME_TYPE.keys() else None

    # Set instrument type
    if detected_type:
        instr_type_final = detected_type
    else:
        instr_type_final = instr_type if instr_type else None
    instr_type_final = instr_type_final if instr_type_final in WHITELIST_INSTR_NAME_TYPE.values() else None

    # Construct full instrument identifier
    if instr_name and instr_type_final:
        instrument_i = f"{instr_type_final} {instr_name}"
    elif instr_name:
        instrument_i = f"{WHITELIST_INSTR_NAME_TYPE[instr_name]} {instr_name}"
    else:
        instrument_i =  None
    return instrument_i


def get_experiment_id(data_accession):
    """
    Extract experiment ID from accession string (MassBank format).

    Args:
        data_accession (str) : Accession string (MassBank format).

    Returns:
        experiment_id_i (str) : Experiment ID
    """
    import re
    if data_accession:
        match = re.search(r'(?<=\d{6})\d+', data_accession)
        if match:
            experiment_id_i = match.group()
        else:
            experiment_id_i = None
    else:
        experiment_id_i = None
    return experiment_id_i


def get_isotope(data_isotope):
    """
    Retrieves and returns the isotope / type of molecular mass from the provided data.
    - Needs to match the whitelist

    Args:
        data_isotope (str) : Type of molecular mass.

    Returns:
        isotope_i (str) : Formatted string.
    """
    if data_isotope and data_isotope.strip() in WHITELIST_ISOTOPE:
        isotope_i = data_isotope.strip()
    else:
        isotope_i = None
    return isotope_i


def get_pubchem_id(data_pc_id):
    """
    Retrieves and returns the PubChem ID as integer.

    Args:
        data_pc_id (str): PubChem ID from the data.

    Returns:
        pc_id_i (int): PubChem ID as integer. Returns None, if the input is empty.
    """
    # Convert PubChem ID to integer if possible
    try:
        pc_id_i = int(data_pc_id)

        # Reject floats and negative IDs
        if isinstance(data_pc_id, float):
            pc_id_i = None
        elif pc_id_i < 0:
            pc_id_i = None

    except (TypeError, ValueError):
        pc_id_i = None

    return pc_id_i


def get_exact_mass_adduct_mass(data_exact_mass, smiles_i, mz_i):
    """Returns exact mass and adduct mass. Calculates exact mass from SMILES if necessary."""
    from rdkit import Chem
    from rdkit.Chem import Descriptors

    # Get exact mass from extracted data or calculate via smiles
    try:
        exact_mass = float(data_exact_mass)
    except (TypeError, ValueError):
        exact_mass = None

    if not exact_mass and smiles_i:
        mol = Chem.MolFromSmiles(smiles_i)
        exact_mass = Descriptors.ExactMolWt(mol)

    # Calculate adduct mass
    if exact_mass and mz_i:
        adduct_mass = mz_i - exact_mass
    else:
        adduct_mass = None

    return exact_mass, adduct_mass
