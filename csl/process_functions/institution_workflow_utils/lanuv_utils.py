
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
