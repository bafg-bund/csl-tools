def extract_data_regex_mbank(file_path, par_regex):
    """
    Extracts relevant data based on regular expressions.

    Args:
        file_path (str)  : Path of file.
        par_regex (dict) : Regular expressions for data extraction. Input as dictionary with fixed parameters (keys)
                           and the respective regular expression (values).

    Returns:
        df (DataFrame) : DataFrame with extracted data.
    """
    import re
    import pandas as pd

    def extract_data_in_chunk(chunk, par_regex):
        """Extract data of a single chunk based on regular expressions."""
        data_extract_dict = {}
        peak_extract = []
        peak_start = False  # Initialize peak_start
        for variable in par_regex.items():
            par_key = variable[0]
            par_value = variable[1]
            if par_value:
                regex = re.compile(par_value, re.IGNORECASE)
                if par_key != 'par_peak':
                    for line in chunk.strip().split('\n'):
                        match = regex.search(line)
                        if match:
                            extracted_value = re.sub(regex, '', line, count=1).strip()
                            data_extract_dict[par_key] = extracted_value if extracted_value else []
                            break
                    else:  # If no match was detected in file_content (line was deleted or variable renamed)
                        data_extract_dict[par_key] = []
                else:  # Only for detecting peaks (par_peak)
                    for line in chunk.strip().split('\n'):
                        match = regex.search(line)
                        if match:
                            peak_start = True
                        # If par_peak was found, save every line as peak data until the line with '//'
                        elif peak_start and not line.strip() == '//':
                            peak_extract.append(line.strip())
                        elif peak_start and line.strip() == '//':
                            break
                    data_extract_dict[par_key] = peak_extract
            else:
                data_extract_dict[par_key] = []
        return data_extract_dict

    # Main function logic
    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()

    # Split content into chunks based on an identifier
    chunk_identifier = 'ACCESSION: '
    chunks = content.split(chunk_identifier)[1:]
    # Parse each chunk into a dictionary
    records = []
    for chunk in chunks:
        record = extract_data_in_chunk(chunk_identifier + chunk, par_regex)
        records.append(record)

    # Create DataFrame
    df = pd.DataFrame(records)
    return df
