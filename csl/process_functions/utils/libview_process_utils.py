def extract_data_regex_libview(file_path_data, par_regex, file_path_extra):
    """
    Splits file content into chunk records and extracts relevant data based on specified regular expressions.
    Merges compound name and retention time data from a supplementary file.

    Args:
        file_path_data (str)  : Path of file.
        par_regex (dict)      : Regular expressions for data extraction. Input as dictionary with fixed parameters (keys)
                                and the respective regular expression (values).
        file_path_extra (str) : Path of supplementary file (containing compound names and retention times)

    Returns:
        df (DataFrame) : DataFrame with extracted data for each chunk.
    """
    import re
    import pandas as pd
    from io import StringIO
    from rdkit import Chem
    from rdkit.Chem import inchi
    from rdkit import RDLogger

    def extract_data_in_chunk(chunk, par_regex):
        """Extract data of a single chunk based on regular expressions."""
        data_extract_dict = {}
        lines = chunk.strip().split('\n')

        for variable in par_regex.items():
            par_key = variable[0]
            par_value = variable[1]
            extract = []  # Reset extracted data
            regex = re.compile(par_value, re.IGNORECASE)

            # Extract variable values
            if par_key == 'par_molblock':
                in_mol = False
                for line in lines:
                    match = regex.search(line)
                    if match:
                        in_mol = True
                    if in_mol:
                        extract.append(line)
                        if line.strip() == "M  END":
                            extract = '\n\n\n' + '\n'.join(extract) # Prepend three empty lines
                            break
                else:  # If no match was detected in file_content (line was deleted or variable renamed)
                    data_extract_dict[par_key] = []
            else:  # All other variables
                start = False  # Reset start variable
                for line in lines:
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
                    data_extract_dict[par_key] = []

            # Fill data dictionary
            if len(extract) == 1:
                data_extract_dict[par_key] = extract[0]  # Unpack list.
            else:
                data_extract_dict[par_key] = extract  # For variables with multiline values (par_peak and par_molblock).

        return data_extract_dict


    def add_smiles_and_inchikey_to_dict(record):
        """Calculates SMILES and InChIKey from molblock and add values to dictionary."""
        RDLogger.DisableLog('rdApp.warning')
        if record['par_molblock']:
            m = Chem.MolFromMolBlock(record['par_molblock'])
            record['par_smiles'] = Chem.MolToSmiles(m)
            record['par_inchi'] = inchi.MolToInchi(m)
            record['par_inchikey'] = inchi.InchiToInchiKey(record['par_inchi'])
        else:
            record['par_smiles'] = []
            record['par_inchi'] = []
            record['par_inchikey'] = []
        return record


    def add_rt_from_dict(record, rt_dict):
        """Matches record compound name to dictionary (compound name and retention times) and adds RT value to record."""
        par_comp = record.get('par_comp')
        record['par_rt'] = rt_dict.get(par_comp.lower(), []) if par_comp else []
        return record


    # Main function logic

    # Read data files
    with open(file_path_data, 'r', encoding='utf-8') as file:
        content = file.read()
    with open(file_path_extra, 'r', encoding='utf-8') as file_extra:
        suppl = file_extra.read()
    suppl_text = suppl.lstrip('\ufeff')
    df = pd.read_csv(StringIO(suppl_text), sep=None, engine='python')
    df.columns = ['compound_name', 'rt']
    df['rt'] = pd.to_numeric(df['rt'], errors='coerce')
    comp_rt_dict = {  # Create dictionary with lower case compound names for better sensitivity
        k.lower(): v
        for k, v in df.set_index('compound_name')['rt'].to_dict().items()
    }

    # Split content into chunks based on an identifier
    chunk_identifier = '$$$$'
    chunks = content.split(chunk_identifier)[0:-1]  # assumes chunk identifier at the end of each record

    # Parse each chunk into a dictionary
    records = []
    for chunk in chunks:
        record = extract_data_in_chunk(chunk_identifier + chunk, par_regex)
        record = add_smiles_and_inchikey_to_dict(record)
        record = add_rt_from_dict(record, comp_rt_dict)
        records.append(record)

    # Create DataFrame
    df = pd.DataFrame(records)
    return df
