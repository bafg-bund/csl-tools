def extract_data_regex_mbank(file_path, var_regex):
    """
    Extracts relevant data based on regular expressions.

    Args:
        file_path (str)  : Path of file.
        var_regex (dict) : Regular expressions for data extraction. Input as dictionary with fixed variable
                           names (keys) and the respective regular expression (values), to keep it consistent
                           across institutional workflows. See <inst>_config.py.

    Returns:
        df (DataFrame) : DataFrame with extracted data.
    """
    import re
    import pandas as pd

    def extract_data_in_chunk(chunk, var_regex):
        """Extract data of a single chunk based on regular expressions."""
        data_extract_dict = {}
        peak_extract = []
        peak_start = False  # Initialize peak_start
        for variable in var_regex.items():
            var_key = variable[0]
            var_value = variable[1]
            if var_value:
                regex = re.compile(var_value, re.IGNORECASE)
                if var_key != 'var_peak':
                    for line in chunk.strip().split('\n'):
                        match = regex.search(line)
                        if match:
                            extracted_value = re.sub(regex, '', line, count=1).strip()
                            data_extract_dict[var_key] = extracted_value if extracted_value else []
                            break
                    else:  # If no match was detected in file_content (line was deleted or variable renamed)
                        data_extract_dict[var_key] = []
                else:  # Only for detecting peaks (var_peak)
                    for line in chunk.strip().split('\n'):
                        match = regex.search(line)
                        if match:
                            peak_start = True
                        # If var_peak was found, save every line as peak data until the line with '//'
                        elif peak_start and not line.strip() == '//':
                            peak_extract.append(line.strip())
                        elif peak_start and line.strip() == '//':
                            break
                    data_extract_dict[var_key] = peak_extract
            else:
                data_extract_dict[var_key] = []
        return data_extract_dict

    # Main function logic
    with open(file_path, 'r') as file:
        content = file.read()

    # Split content into chunks based on an identifier
    chunk_identifier = 'ACCESSION: '
    chunks = content.split(chunk_identifier)[1:]
    # Parse each chunk into a dictionary
    records = []
    for chunk in chunks:
        record = extract_data_in_chunk(chunk_identifier + chunk, var_regex)
        records.append(record)

    # Create DataFrame
    df = pd.DataFrame(records)
    return df
