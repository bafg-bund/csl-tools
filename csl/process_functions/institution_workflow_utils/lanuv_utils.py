
def extract_data_regex_lanuv(file_path, var_regex):
    """
    Splits file content into chunks by identifying the first line of a chunk and extracts relevant data based on
    regular expressions.

    Args:
        file_path (str)  : Path of file.
        var_regex (dict) : Regular expressions for data extraction. Input as dictionary with fixed variable
                           names (keys) and the respective regular expression (values), to keep it consistent
                           across institutional workflows. See <inst>_config.py.

    Returns:
        df (DataFrame) : DataFrame with extracted data for each chunk.
    """
    import re
    import pandas as pd

    def extract_data_in_chunk(chunk, var_regex):
        """
        Extract data of a single chunk based on regular expressions.
        """
        data_extract_dict = {}
        for variable in var_regex.items():
            start = False  # Reset start variable
            extract = []  # Reset extracted data
            var_key = variable[0]
            var_value = variable[1]
            regex = re.compile(var_value, re.IGNORECASE)
            for line in chunk.strip().split('\n'):
                match = regex.search(line)
                if match:
                    start = True
                # If the line was found, save every non-empty line as data
                # until the next empty line (assumes no empty lines in between).
                elif start and line.strip():
                    extract.append(line.strip())
                elif start and not line.strip():
                    break
            else:  # If no match was detected in file_content (line was deleted or variable renamed)
                data_extract_dict[var_key] = []
            if len(extract) == 1:
                data_extract_dict[var_key] = extract[0]  # Unpack list.
            else:
                data_extract_dict[var_key] = extract  # Only applies to var_peak. Peaks will be saved as list.
        return data_extract_dict

    # Main function logic
    with open(file_path, 'r') as file:
        content = file.read()

    # Split content into chunks based on the "Name: " identifier
    chunk_identifier = '>  <NAME>'  # todo: differs from other workflows
    chunks = content.split(chunk_identifier)[1:]
    # Parse each chunk into a dictionary
    records = []
    for chunk in chunks:
        record = extract_data_in_chunk(chunk_identifier + chunk, var_regex)
        records.append(record)

    # Create a DataFrame
    df = pd.DataFrame(records)
    return df












# from .process_utils import *
# def extract_data_regex_lanuv(file_path, var_regex):
#     """Extracts data from one lanuv .sdf-file based on a dictionary of regular expressions and saves it as DataFrame."""
#     import re
#     from tqdm import tqdm
#
#     def parse_chunk(chunk, var_regex):
#         """
#         Parse a single chunk of text to extract key-value pairs.
#         """
#         data = {}
#         lines = chunk.strip().split('\n')
#         i = 0
#         while i < len(lines):
#             line = lines[i].strip()
#             # Check if line contains a key
#             if line.startswith('>'):
#                 # Extract key
#                 key_match = re.match(r'>\s*<(.*?)>', line)
#                 if key_match:
#                     key = key_match.group(1)
#                     # Handle the special case of MASS SPECTRAL PEAKS
#                     if key == var_regex['var_peak']:
#                         i += 1
#                         peak_lines = []
#                         while i < len(lines) and lines[i].strip():
#                             peak_lines.append(lines[i].strip())
#                             i += 1
#                         data[key] = peak_lines  # Concatenate all peak lines into a single string
#                     else:
#                         # Regular key-value pair
#                         i += 1
#                         if i < len(lines):
#                             data[key] = lines[i].strip()
#             i += 1
#         return data
#
#     def parse_file(filename, var_regex):
#         """
#         Parse the entire file and return a DataFrame.
#         """
#         with open(filename, 'r') as file:
#             content = file.read()
#
#         # Split content into chunks based on the "$$$$" separator
#         chunks = content.split('$$$$')
#
#         # Parse each chunk into a dictionary
#         records = []
#         for chunk in tqdm(chunks):
#             chunk = chunk.strip()
#             if chunk:  # Avoid parsing empty chunks
#                 record = parse_chunk(chunk, var_regex)
#                 records.append(record)
#         return records
#
#     # Main
#     extract_data = parse_file(file_path, var_regex)
#     return extract_data
#
#
# def process_one_entry(data_extract_entry, var_regex, inst_def, spec_adduct):
#     """Processes one entry. Todo"""
#     print(data_extract_entry)
#     # Code to apply to this row
#     import logging
#     logger = logging.getLogger(__name__)
#     file_skip = False  # todo: file skipping etc different format? e.g. entry in df, or append list
#     file_warn = False
#
#     # Calculate and check all variables that are needed for the CSL entry / matching
#     # Set file_skip to determine under which conditions the file should be skipped.
#
#     # Polarity
#     pol_i = get_polarity(data_extract_entry[var_regex['var_ionmode']], inst_def['pol_p_def'], inst_def['pol_n_def'])
#     if not pol_i:
#         logger.warning(f'Unexpected polarity type: {data_extract_entry[var_regex['var_ionmode']]}')
#         file_skip = True
#
#     # Compound and adduct name
#     comp_i, adduct_name = get_compound_and_adduct_name(data_extract_entry[var_regex['var_comp']])
#     if not comp_i or not adduct_name:
#         logger.warning(f'Unexpected or missing compound/adduct name: {data_extract_entry[var_regex['var_comp']]}.')
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
#     ce_i, ces_i, ces_warn = get_collision_energy(data_extract_entry[var_regex['var_ce']])
#     if not ce_i or not ce_i and not ces_i:
#         logger.warning(
#             f'No collision energy (CE) or unexpected number of CE or non-equal difference in CE spread. '
#             f'Check field {var_regex['var_ce']}')
#         file_skip = True
#     elif ces_warn:
#         logger.warning(f'Unexpected collision energy spread. '
#                        f'Check field {var_regex['var_ce']}. \n''Will NOT automatically skip entry due to this warning')  # todo: changed file to entry
#         file_warn = True
#
#     # Ionization type  # Todo: Problem here, is that its not in the data.
#     #  todo: Can be either retrieved from defaults. but then code is not universal, unless there are prior checks
#     # ionization_i = get_ionization_type(data_extract_entry[var_regex['var_ionization']])
#     # if not ionization_i:
#     #     logger.warning('Ionization type not detected.')
#     #     file_skip = True
#
#     # Formula
#     formula_i = get_formula(data_extract_entry[var_regex['var_formula']])
#     if not formula_i:
#         logger.warning('Formula not detected.')
#         file_skip = True
#
#     # InChIKey  # Todo: Not in the data
#     # inchikey_i, inchikey_main_i = get_inchikey(data_extract_entry[var_regex['var_inchikey']])
#     # if not inchikey_i:
#     #     logger.warning('InChiKey not detected.')
#     #     file_warn = True
#
#     # CAS registry number
#     cas_i = get_cas(data_extract_entry[var_regex['var_cas']])
#     if not cas_i:
#         logger.warning('CAS registry number not detected or malformed')
#         file_warn = True
#
#     # Skip if no InChIKey and no CAS registry number found
#     # if not inchikey_i and not cas_i:
#     #     file_skip = True
#
#     # SMILES  # Todo: Not in the data
#     # smiles_i = get_smiles(data_extract_entry[var_regex['var_smiles']])
#     # if not smiles_i:
#     #     logger.warning('Smiles not detected')
#     #     file_skip = True
#
#     # Precursor mass
#     mz_i = get_precursor_mz(data_extract_entry[var_regex['var_mz']])
#     if not mz_i:
#         logger.warning('Precursor mass not detected')
#         file_skip = True
#
#     # Retention time  # Todo: Not in the data
#     # rt_i = get_retention_time(data_extract_entry[var_regex['var_rt']])
#     # if not rt_i:
#     #     logger.warning('Retention time not detected')
#     #     file_skip = True
#
#     # Spectra / Peaks
#     spec_i = get_peaks(data_extract_entry[var_regex['var_peak']])
#     if spec_i.empty:
#         logger.warning('No spectra detected')
#         file_skip = True

    # Prepare dictionary from all extracted variables
    # form_data = {
    #     'pol_i': pol_i,
    #     'comp_i': comp_i,
    #     'adduct_i': adduct_i,
    #     'ce_i': ce_i,
    #     'ces_i': ces_i,
    #     'ionization_i': ionization_i,
    #     'formula_i': formula_i,
    #     'inchikey_i': inchikey_i,
    #     'inchikey_main_i': inchikey_main_i,
    #     'cas_i': cas_i,
    #     'smiles_i': smiles_i,
    #     'mz_i': mz_i,
    #     'rt_i': rt_i,
    #     'spec_i': spec_i
    # }
    #
    # return form_data, file_skip, file_warn