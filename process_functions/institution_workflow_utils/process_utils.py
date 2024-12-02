
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


# def collect_file_content(file_paths):
#     """
#     Collects file content from all files and merges it into one list of strings.
#     # Todo: Check if it works for all data types
#     Args:
#         file_paths (list of str) : List of file paths to read.
#
#     Returns:
#         file_content_all (list of str) : Collected data from all files.
#     """
#
#     # Reading the files and save content in a list
#     # Each element in the list contains content of one file (each line = separate string)
#     file_content_all = []
#     for file in file_paths:  # file = files[0]
#         with open(file) as filex:
#             file_content = filex.readlines()
#
#         # with open(file, 'r') as filex:
#             # file_content = filex.read()
#         # file_content_all = file_content_all + '\n' + file_content
#         file_content_all = file_content_all + ['\n'] + file_content
#     return file_content_all


# def extract_data_regex(file_paths, var_regex):
#     """
#     Extracts data from files based on a list of regular expressions.
#
#     Args:
#         file_paths (list of str) : List of file paths to read.
#         var_regex (dict)         : Regular expressions for data extraction. Input as dictionary with fixed variable
#                                    names (keys) and the respective regular expression (values), to keep it consistent
#                                    across institutional workflows. See <inst>_config.py.
#
#     Returns:
#         extract_data_all (dict)  : Extracted data from all files saved as a list of dictionaries with variable names
#                                    (keys) and extracted data (values).
#     """
#     import re
#     import logging
#
#     logger = logging.getLogger(__name__)
#     logger.info('Extracting data from files')
#
#     # Reading the files and save content in a list
#     # Each element in the list contains content of one file (each line = separate string)
#     file_content_all = []
#     for file in file_paths:  # file = files[0]
#         with open(file) as filex:
#             file_content = filex.readlines()
#         file_content_all.append(file_content)
#
#     # Extract data for the defined variables
#     # - Creates a dictionary for each file and appends it to a list.
#     # - Each dictionary contains the variable names (keys) and the respective extracted data (values).
#     # - The values are found by matching the variables strings line by line through the file content.
#     # - If no match is found or the line is malformed, then the value will be [].
#     data_extract_all = []
#     for file_content in file_content_all:
#         data_extract_dict = {}
#         peak_extract = []
#         peak_start = False  # Initialize peak_start
#         for variable in var_regex.values():
#             regex = re.compile(variable, re.IGNORECASE)
#             if variable != var_regex['var_peak']:
#                 for line in file_content:
#                     match = regex.search(line)
#                     if match:
#                         parts = line.split(':')
#                         if len(parts) == 2:
#                             data_extract_dict[variable] = parts[1].strip()
#                         else:  # If line is malformed
#                             data_extract_dict[variable] = []
#                         break
#                 else:  # If no match was detected in file_content (line was deleted or variable renamed)
#                     data_extract_dict[variable] = []
#             else:  # Only for detecting peaks (var_peak)
#                 for line in file_content:
#                     match = regex.search(line)
#                     if match:
#                         peak_start = True
#                     elif peak_start and line.strip():  # Only if var_peak was found and the line is not empty
#                         peak_extract.append(line.strip())
#                 data_extract_dict[variable] = peak_extract
#         data_extract_all.append(data_extract_dict)
#
#     # Check if there are any empty values. Gives only a warning, but won't stop the program.
#     for idx, data_extract in enumerate(data_extract_all):
#         for variable in var_regex.values():
#             if not bool(data_extract.get(variable)):
#                 logger.warning('No value for key: "{}" in file {}'.format(variable, file_paths[idx]))
#
#     return data_extract_all


# def process_one_file(extract_data, var_regex, inst_def, spec_adduct):
#     """
#     Formats the previously extracted data of one file to match the required format for csl-matching/commits.
#     See information on format requirements of txt-files here:
#     https://gitlab.lan.bafg.de/nts/ntsportal/-/wikis/Processing-new-files-for-the-CSL
#     Checks the data and determines the state of the file (e.g. if it should be skipped later on due to missing data).
#     For formatting and quality control institute specific, and global defaults are loaded from a config file.
#     Todo: It needs to be seen if the function(s) can be used for other institution workflows as well.
#     Todo: If not, they should be moved out of `process_utils.py` into e.g. `lfuby_utils.py`
#
#     Args:
#         extract_data (dict) : Extracted data of the file.
#         var_regex (dict)    : Institution-specific regular expressions used as keywords to find correct values in data.
#         inst_def (dict)     : Institution-specific defaults used for keeping format, and csl-matching/commits.
#         spec_adduct (dict)  : Special cases in adduct formatting.
#
#     Returns:
#         form_data (dict) : Formatted data of the file
#         file_skip (bool) : True: File will be skipped before entering csl-matching/commit process.
#                            False: File will enter csl-matching/commit process.
#         file_warn (bool) : True: File will not be skipped, but user gets a warning before csl-commit.
#                            False: File will enter csl-matching/commit process.
#     """
#     import logging
#     logger = logging.getLogger(__name__)
#     file_skip = False
#     file_warn = False
#
#     # Calculate and check all variables that are needed for the CSL entry / matching
#     # Set file_skip to determine under which conditions the file should be skipped.
#
#     # Polarity
#     pol_i = get_polarity(extract_data[var_regex['var_ionmode']], inst_def['pol_p_def'], inst_def['pol_n_def'])
#     if not pol_i:
#         logger.warning(f'Unexpected polarity type: {extract_data[var_regex['var_ionmode']]}')
#         file_skip = True
#
#     # Compound and adduct name
#     comp_i, adduct_name = get_compound_and_adduct_name(extract_data[var_regex['var_comp']])
#     if not comp_i or not adduct_name:
#         logger.warning(f'Unexpected or missing compound/adduct name: {extract_data[var_regex['var_comp']]}.')
#         file_skip = True
#
#     # Adduct format conversion
#     adduct_i = format_adduct(adduct_name, spec_adduct, inst_def['qf_def'], pol_i)
#     if not adduct_i:
#         logger.warning(f'Adduct name not detected. Check fields "{var_regex['var_comp']}" '
#                        f'and "{var_regex['var_ionmode']}"')
#         file_skip = True
#     else:
#         logger.info(f'Adduct name: {adduct_name}; Formatted adduct name: {adduct_i}')
#
#     # Collision energy (CE) and collision energy spread (CES)
#     ce_i, ces_i, ces_warn = get_collision_energy(extract_data[var_regex['var_ce']])
#     if not ce_i or not ce_i and not ces_i:
#         logger.warning(f'No collision energy (CE) or unexpected number of CE or non-equal difference in CE spread. '
#                        f'Check field {var_regex['var_ce']}')
#         file_skip = True
#     elif ces_warn:
#         logger.warning(f'Unexpected collision energy spread. '
#                        f'Check field {var_regex['var_ce']}. \n''Will NOT automatically skip file due to this warning')
#         file_warn = True
#
#     # Ionization type
#     ionization_i = get_ionization_type(extract_data[var_regex['var_ionization']])
#     if not ionization_i:
#         logger.warning('Ionization type not detected')
#         file_skip = True
#
#     # Formula
#     formula_i = get_formula(extract_data[var_regex['var_formula']])
#     if not formula_i:
#         logger.warning('Formula not detected')
#         file_skip = True
#
#     # InChIKey
#     inchikey_i, inchikey_main_i = get_inchikey(extract_data[var_regex['var_inchikey']])
#     if not inchikey_i:
#         logger.warning('InChiKey not detected')
#         file_warn = True
#
#     # CAS registry number
#     cas_i = get_cas(extract_data[var_regex['var_cas']])
#     if not cas_i:
#         logger.warning('CAS registry number not detected or malformed')
#         file_warn = True
#
#     # Skip if no InChIKey and no CAS registry number found
#     if not inchikey_i and not cas_i:
#         file_skip = True
#
#     # SMILES
#     smiles_i = get_smiles(extract_data[var_regex['var_smiles']])
#     if not smiles_i:
#         logger.warning('Smiles not detected')
#         file_skip = True
#
#     # Precursor mass
#     mz_i = get_precursor_mz(extract_data[var_regex['var_mz']])
#     if not mz_i:
#         logger.warning('Precursor mass not detected')
#         file_skip = True
#
#     # Retention time
#     rt_i = get_retention_time(extract_data[var_regex['var_rt']])
#     if not rt_i:
#         logger.warning('Retention time not detected')
#         file_skip = True
#
#     # Spectra / Peaks
#     spec_i = get_peaks(extract_data[var_regex['var_peak']])
#     if spec_i.empty:
#         logger.warning('No spectra detected')
#         file_skip = True
#
#     # Prepare dictionary from all extracted variables
#     form_data = {
#         'pol_i': pol_i,
#         'comp_i': comp_i,
#         'adduct_i': adduct_i,
#         'ce_i': ce_i,
#         'ces_i': ces_i,
#         'ionization_i': ionization_i,
#         'formula_i': formula_i,
#         'inchikey_i': inchikey_i,
#         'inchikey_main_i': inchikey_main_i,
#         'cas_i': cas_i,
#         'smiles_i': smiles_i,
#         'mz_i': mz_i,
#         'rt_i': rt_i,
#         'spec_i': spec_i
#     }
#
#     return form_data, file_skip, file_warn


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
    - If `CompoundName` is provided, the default adduct name `H` is assigned.
    - If the input format is invalid or unexpected, both the compound name and adduct name will return None.
    Todo: Lfuby format (CompoundName_AdductName) compatible with other workflows? -> TBD

    Args:
        data_comp (str) : Compound name and optionally the adduct name from data. The expected format is `CompoundName`
                          or `CompoundName_AdductName`.

    Returns:
        comp_i (str)      : Formatted compound name. Returns None, if the input is invalid.
        adduct_name (str) : Formatted adduct name. Returns None, if the input is invalid.
    """
    if data_comp:
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
    Todo: Add whitelist of all pairs of adduct name + adduct notations

    Args:
        adduct_name (str)  : Adduct name determined by `get_compound_and_adduct_name`.
        spec_adduct (dict) : Dictionary specifying special cases for adduct notations based on certain adduct names.
        qf_def (str)       : Default identifier for precursor ion number ("Quellfragmente").
        pol_i (str)        : Ion polarity, determined by `get_polarity`; Either 'pos' (positive) or 'neg' (negative).

    Returns:
        adduct_i (str) : Formatted adduct notation. Returns None, if the input is invalid.
    """
    # Adduct name conversion
    adduct_i = None  # Initialize variable
    if not adduct_name or not pol_i:
        adduct_i = None
    else:
        if adduct_name in spec_adduct:
            # Special cases
            adduct_i = spec_adduct[adduct_name]
        elif qf_def in adduct_name:
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


def get_collision_energy(data_ce):
    """
    Determines the collision energy (CE) and collision energy spread (CES) according to CSL requirements.
    - For a single CE input value, the function returns that value as `ce_i` and sets `ces_i` to None (no spread).
    - For multiple CE input values, the function calculates the CES and identifies the middle CE value as `ce_i`.
    - If the CES calculation is unexpected or non-standard, a warning is issued by setting `ces_warn` to True.
    - Negative CE value inputs are converted to positive values

    Args:
        data_ce (str) : One or more collision energy values from the data.

    Returns:
        ce_i (int)      : Primary collision energy (CE) value. If multiple CE values are provided, `ce_i` will be the
                          value from the middle position. Returns None, if the input is invalid.
        ces_i (int)     : Collision energy spread (CES). CES is calculated only if multiple CE values are provided.
                          Returns None, if the input is invalid or unexpected.
        ces_warn (bool) : A flag indicating whether a warning should be issued due to unexpected CES calculations.
                          True if a warning is issued, False otherwise.
    """
    import re
    import numpy as np

    ces_warn = False
    if data_ce:
        str_nrs = re.findall(r'\d+', data_ce)  # Find numbers in string
        int_nrs = list(map(int, str_nrs))  # Convert to list of int
        int_nrs_real = [int_nr for int_nr in int_nrs if int_nr > 0]  # Remove zeros
        if len(int_nrs_real) == 1:  # One CE
            ce_i = int_nrs_real[0]
            ces_i = 0  # Spread
        elif len(int_nrs_real) == 3:  # Three CE
            ce_i = int_nrs_real[1]  # Assuming correct positions!
            # Calculating CES. Checking for equal difference in CES.
            ce_diff = np.diff(int_nrs_real)
            ce_diff_unique = np.unique(ce_diff)
            if len(ce_diff_unique) == 1:
                ces_i = abs(int(ce_diff_unique[0]))  # Assuming correct positions!
                if ces_i != 20:  # Equal difference in CES, but value not expected
                    ces_warn = True
            else:  # Non-equal difference in CES
                ce_i = None  # Setting to `None` even though CE might be ok.
                ces_i = None
        else:  # Unexpected number of CE
            ce_i = None
            ces_i = None
    else:  # No data found
        ce_i = None
        ces_i = None
    return ce_i, ces_i, ces_warn


def get_ionization_type(data_ionization):
    """
    Retrieves and returns the ionization type from the provided data.

    Args:
        data_ionization (str) : Ionization type from the data.

    Returns:
        ionization_i (str) : Ionization type. Returns None, if the input is invalid.
    """
    if data_ionization:
        ionization_i = data_ionization
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
    if data_formula:
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
    Retrieves and returns the SMILES-string (Simplified Molecular Input Line Entry System) from the provided data.

    Args:
        data_smiles (str): SMILES-string from the data.

    Returns:
        smiles_i (str): SMILES-string. Returns None, if the input is invalid.
    """
    if data_smiles:
        smiles_i = data_smiles
    else:
        smiles_i = None
    return smiles_i


def get_precursor_mz(data_mz):
    """
    Retrieves and returns the precursor mass-to-charge ratio (m/z) as a float.

    Args:
        data_mz (str): Precursor mass-to-charge ratio (m/z) as a string from the data.

    Returns:
        mz_i (float): Precursor mass-to-charge ratio (m/z) as a float. Returns None, if the input is invalid.
    """
    if data_mz:
        mz_i = float(data_mz)
    else:
        mz_i = None
    return mz_i


def get_retention_time(data_rt):
    """
    Retrieves and returns the retention time as a float.

    Args:
        data_rt (str): Retention time from the data.

    Returns:
        rt_i (float): Retention time as a float. Returns None, if the input is invalid.
    """
    if data_rt:
        rt_i = float(data_rt)
    else:
        rt_i = None
    return rt_i


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

    if data_peak:
        split_strings = [s.split() for s in data_peak]
        spec_i = pd.DataFrame(split_strings, columns=['mz', 'int'])
    else:
        spec_i = pd.DataFrame()
    return spec_i
