def extract_data_regex_lfuby(file_path, var_regex):
    """
    Splits file content into chunks by identifying the first line of a chunk and extracts relevant data based on
    regular expressions.

    Args:
        file_path (str)  : Path of file.
        var_regex (dict) : Regular expressions for data extraction. Input as dictionary with fixed variable
                           names (keys) and the respective regular expression (values), to keep it consistent
                           across data source workflows. See <data source>_config.py.

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
        peak_extract = []
        peak_start = False  # Initialize peak_start
        for variable in var_regex.items():
            var_key = variable[0]
            var_value = variable[1]
            regex = re.compile(var_value, re.IGNORECASE)
            if var_key != 'var_peak':
                for line in chunk.strip().split('\n'):
                    match = regex.search(line)
                    if match:
                        delim = ':'
                        parts = re.split(pattern=delim, string=line, maxsplit=1)
                        if len(parts) > 1:
                            data_extract_dict[var_key] = parts[-1].strip()
                        else:  # If line is malformed
                            data_extract_dict[var_key] = []
                        break
                else:  # If no match was detected in file_content (line was deleted or variable renamed)
                    data_extract_dict[var_key] = []
            else:  # Only for detecting peaks (var_peak)
                for line in chunk.strip().split('\n'):
                    match = regex.search(line)
                    if match:
                        peak_start = True
                    # If var_peak was found, save every non-empty line as peak data
                    # until the next empty line (assumes no empty lines in between).
                    elif peak_start and line.strip():
                        peak_extract.append(line.strip())
                    elif peak_start and not line.strip():
                        break
                data_extract_dict[var_key] = peak_extract
        return data_extract_dict

    # Main function logic
    with open(file_path, 'r') as file:
        content = file.read()

    # Split content into chunks based on an identifier
    chunk_identifier = 'Name: '
    chunks = content.split(chunk_identifier)[1:]
    # Parse each chunk into a dictionary
    records = []
    for chunk in chunks:
        record = extract_data_in_chunk(chunk_identifier + chunk, var_regex)
        records.append(record)

    # Create DataFrame
    df = pd.DataFrame(records)
    return df
