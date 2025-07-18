from csl.export_functions.utils.mbank_export_utils import *
import pytest
from unittest.mock import patch


def test_get_exp_ids_mbank():
    """Tests if the returned dictionary contains the valid file paths and is correctly formatted."""
    # Prepare data
    mock_files = [
        "MSBNK-BAFG-CSL250401123.txt",
        "invalid_file.db",
        "MSBNK-BAFG-CSL250402456.txt"
    ]
    expected_dict = {
        123: "MSBNK-BAFG-CSL250401123",
        456: "MSBNK-BAFG-CSL250402456"
    }

    # Call the function
    with patch("os.listdir", return_value=mock_files):
        dict_mbank_exp_id = get_exp_ids_mbank("/dummy/path")

    # Assert
    assert dict_mbank_exp_id == expected_dict


def test_build_export_chunk_mbank(mock_formatted_data_mbank):
    """Tests the assembly of the export chunk."""
    # Prepare data
    expected_export_chunk = (
        "ACCESSION: MSBNK-BAFG-CSL250109103\n"
        "RECORD_TITLE: Compound; Instr; MS2; 140 V\n"
        "DATE: 2025.01.09\n"
        "AUTHORS: Person A; Person B; Person C\n"
        "LICENSE: dl-de/by-2-0\n"
        "COPYRIGHT: Copyright 2025 Institution\n"
        f"COMMENT: Information\n"
        f"COMMENT: Additional information\n"
        "CH$NAME: Compound\n"
        "CH$COMPOUND_CLASS: Industrial_process; Biocide\n"
        "CH$FORMULA: [C10H15N]+\n"
        "CH$EXACT_MASS: 248.23\n"
        "CH$SMILES: CC(C)CC\n"
        "CH$IUPAC: InChI=1S/C17H30N\n"
        "CH$LINK: CAS 469-1-1\n"
        "CH$LINK: INCHIKEY SHF-USA-N\n"
        "AC$INSTRUMENT: TripleTOF 5600 SCIEX\n"
        "AC$INSTRUMENT_TYPE: LC-ESI-QTOF\n"
        "AC$MASS_SPECTROMETRY: MS_TYPE MS2\n"
        "AC$MASS_SPECTROMETRY: ION_MODE POSITIVE\n"
        "AC$MASS_SPECTROMETRY: COLLISION_ENERGY 140\n"
        "AC$MASS_SPECTROMETRY: FRAGMENTATION_MODE CID\n"
        "AC$MASS_SPECTROMETRY: IONIZATION ESI\n"
        f"AC$CHROMATOGRAPHY: RETENTION_TIME 12 min\n"
        "MS$FOCUSED_ION: PRECURSOR_M/Z 123.23\n"
        "MS$FOCUSED_ION: PRECURSOR_TYPE [M]+\n"
        "MS$DATA_PROCESSING: COMMENT Export with pycsl 1.0.0 and CSL 25.0.0\n"
        "PK$SPLASH: splash10-0i-900-755\n"
        "PK$NUM_PEAK: 2\n"
        "PK$PEAK: m/z int. rel.int.\n"
        "  100.0 150.0 10.0\n"
        "  200.0 250.0 20.0\n"
        "//\n")

    # Call the function
    export_chunk = build_export_chunk_mbank(mock_formatted_data_mbank)

    # Assert
    assert export_chunk == expected_export_chunk


def test_format_spectrum_mbank():
    """Tests if the spectrum is correctly formatted and relative intensities are calculated."""
    # Prepare data
    spectrum =  [(87.0441, 0.0326), (101.060643, 0.04768), (723.468001, 23.0), (233.4, 0.0)]
    expected_formatted_spectrum = [(87.0441, 0.0326, 1), (101.0606, 0.0477, 2), (723.468, 23.0, 999)]

    # Call the function
    formatted_spectrum = format_spectrum_mbank(spectrum)

    # Assert
    assert formatted_spectrum == expected_formatted_spectrum


@pytest.mark.parametrize("adduct, formula, expected_formula",
                         [('[M]+', 'C9H13NO3', '[C9H13NO3]+'),
                          ('[M]-', 'C9H13NO3', '[C9H13NO3]-')
                          ])
def test_format_formula_mbank(adduct, formula, expected_formula):
    """Tests if the function returns the expected MassBank-specific formula strings."""
    formula_res = format_formula_mbank(adduct, formula)
    assert formula_res == expected_formula


@pytest.mark.parametrize("pol, expected_ion_mode",[('pos','POSITIVE'),('neg','NEGATIVE')])
def test_get_ion_mode_mbank(pol, expected_ion_mode):
    """Test if the function returns the expected MassBank-specific ion mode strings."""
    ion_mode = get_ion_mode_mbank(pol)
    assert ion_mode == expected_ion_mode

def test_get_ion_mode_mbank_error():
    """Tests if the function returns an error when input is not valid."""
    pol = 'non_valid_input'
    with pytest.raises(ValueError, match=f"Unknown polarity format {pol}."):
        get_ion_mode_mbank(pol)


@pytest.mark.parametrize("col_type, expected_frag_mode",[('Q','CID'),('HCD','HCD')])
def test_get_fragmentation_mode_mbank(col_type, expected_frag_mode):
    """Tests if the function returns the expected MassBank-specific fragmentation mode strings."""
    frag_mode = get_fragmentation_mode_mbank(col_type)
    assert frag_mode == expected_frag_mode

def test_get_fragmentation_mode_mbank_error():
    """Tests if the function returns an error when input is not valid."""
    col_type = 'non_valid_input'
    with pytest.raises(ValueError, match=f"Unknown fragmentation mode {col_type}"):
        get_fragmentation_mode_mbank(col_type)


@pytest.mark.parametrize("exp_id, expected_accession",
                         [(777, 'MSBNK-BAFG-CSL250401777'),  # New accession string is created
                          (999, 'accession_string1')  # Existing accession string is used
                          ])
def test_get_accession_mbank(exp_id, expected_accession):
    """Tests if accession strings are correctly build and pre-existing ones are correctly identified."""
    # Prepare data
    mock_dict = {  # Dictionary for linking existing experiment ids to filenames (=accession string)
        999: "accession_string1",
        222: "accession_string2"
    }
    mock_contrib_prefix = 'BAFG'

    # Call the function with mocked datetime
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now().strftime.return_value = '250401'  # Mock current date
        accession = get_accession_mbank(exp_id, mock_contrib_prefix, mock_dict)

    # Assert
    assert accession == expected_accession
