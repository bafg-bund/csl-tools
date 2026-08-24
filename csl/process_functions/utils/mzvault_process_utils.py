def extract_data_regex_mzvault(file_path, par_regex):
    """
    Splits file content into chunks by identifying the first line of a chunk and extracts relevant data based on
    regular expressions.

    Args:
        file_path (str)  : Path of file.
        par_regex (dict) : Regular expressions for data extraction. Input as dictionary with fixed parameters (keys) 
                           and the respective regular expression (values).

    Returns:
        df (DataFrame) : DataFrame with extracted data for each chunk.
    """
    import re
    import pandas as pd

    def extract_data_in_chunk(chunk, par_regex, delim):
        """Extract data of a single chunk based on regular expressions."""
        data_extract_dict = {}
        peak_extract = []
        peak_start = False  # Initialize peak_start
        for variable in par_regex.items():
            par_key = variable[0]
            par_value = variable[1]
            regex = re.compile(par_value, re.IGNORECASE)
            if par_key != 'par_peak':
                for line in chunk.strip().split('\n'):
                    match = regex.search(line)
                    if match:
                        if len(delim)>1:
                            use_delim = delim[0] if delim[0] in line else delim[1]
                        else:
                            use_delim = delim[0]
                        parts = re.split(pattern=use_delim, string=line, maxsplit=1)
                        if len(parts) > 1:
                            data_extract_dict[par_key] = parts[-1].strip()
                        else:  # If line is malformed
                            data_extract_dict[par_key] = []
                        break
                else:  # If no match was detected in file_content (line was deleted or variable renamed)
                    data_extract_dict[par_key] = []
            else:  # Only for detecting peaks (par_peak)
                for line in chunk.strip().split('\n'):
                    match = regex.search(line)
                    if match:
                        peak_start = True
                    # If par_peak was found, save every non-empty line as peak data
                    # until the next empty line (assumes no empty lines in between).
                    elif peak_start and line.strip():
                        peak_extract.append(line.strip())
                    elif peak_start and not line.strip():
                        break
                data_extract_dict[par_key] = peak_extract
        return data_extract_dict

    # Main function logic
    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()

    # Split content into chunks based on an identifier
    if 'MS:1009003|Name' in content:  # Export format of older mzVault version
        chunk_identifier = 'MS:1009003|Name'
        delim = ['=', r'\|']
    else:  # Export format of mzVault version 2.3.64.0
        chunk_identifier = 'Name: '
        delim = ':'
    chunks = content.split(chunk_identifier)[1:]
    # Parse each chunk into a dictionary
    records = []
    for chunk in chunks:
        record = extract_data_in_chunk(chunk_identifier + chunk, par_regex, delim)
        records.append(record)

    # Create DataFrame
    df = pd.DataFrame(records)
    return df
