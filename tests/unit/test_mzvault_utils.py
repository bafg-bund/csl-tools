from csl.export_functions.utils.mzvault_export_utils import *
import pytest


def test_build_export_chunk_mzvault(mock_formatted_data_mzvault):
    """Tests assembly of the export chunk."""
    # Prepare data
    expected_export_chunk = (
        "NAME: Compound\n"
        "ACCESSION: BAFG-CSL2501225\n"
        "RECORD_TITLE: Compound; Instr; MS2; 140 V\n"
        "DATE: 2025.01.09\n"
        "AUTHORS: Person A; Person B; Person C\n"
        "LICENSE: dl-de/by-2-0\n"
        "COPYRIGHT: Copyright 2025 Data source\n"
        "COMMENT: Information\n"
        "COMMENT: Additional information\n"
        "COMPOUNDCLASS: Industrial_process; Biocide\n"
        "FORMULA: C10H15N\n"
        "EXACT_MASS: 248.23\n"
        "CENTROIDED: TRUE\n"
        "SMILES: CC(C)CC\n"
        "INCHI: InChI=1S/C17H30N\n"
        "CASNO: 469-1-1\n"
        "INCHIKEY: SHF-USA-N\n"
        "INSTRUMENT: TripleTOF 5600 SCIEX\n"
        "INSTRUMENTTYPE: LC-ESI-QTOF\n"
        "MS_TYPE: MS2\n"
        "ION_MODE: Positive\n"
        "COLLISION_ENERGY: 140\n"
        "FRAGMENTATION_MODE: Q\n"
        "IONIZATION: ESI\n"
        "RETENTIONTIME: 12.11\n"
        "PREDICTED_RT: FALSE\n"
        "PRECURSORMZ: 123.23\n"
        "PRECURSORTYPE: [M]+\n"
        "PRECURSOR_CHARGE: 1\n"
        "SPLASH: splash10-0i-900-755\n"
        "Num Peaks: 2\n"
        "100.0 150.0\n"
        "200.0 250.0\n")

    # Call the function
    export_chunk = build_export_chunk_mzvault(mock_formatted_data_mzvault)

    # Assert
    assert export_chunk == expected_export_chunk


def test_format_spectrum_mzvault():
    """Tests if the spectrum is correctly formatted."""
    # Prepare data
    spectrum =  [(87.0441, 0.0326), (101.060643, 0.04768), (723.468001, 23.0), (233.4, 0.0)]
    expected_formatted_spectrum = [(87.0441, 0.0326), (101.0606, 0.0477), (723.468, 23.0)]

    # Call the function
    formatted_spectrum = format_spectrum_mzvault(spectrum)

    # Assert
    assert formatted_spectrum == expected_formatted_spectrum


@pytest.mark.parametrize("pol, expected_ion_mode",[('pos','Positive'),('neg','Negative')])
def test_get_ion_mode_mzvault(pol, expected_ion_mode):
    """Tests if the function returns the expected MassBank-specific ion mode strings."""
    ion_mode = get_ion_mode_mzvault(pol)
    assert ion_mode == expected_ion_mode

def test_get_ion_mode_mzvault_error():
    """Tests if the function returns an error when input is not valid."""
    pol = 'non_valid_input'
    with pytest.raises(ValueError, match=f"Unknown polarity format {pol}."):
        get_ion_mode_mzvault(pol)
