import pytest
from unittest.mock import patch, Mock, MagicMock
from export_functions.format_workflow_utils.mbank_utils import *


@pytest.mark.parametrize("col_type, expected_frag_mode",[('Q','CID'),('HCD','HCD')])
def test_get_fragmentation_mode_mbank(col_type, expected_frag_mode):
    """Tests if get_fragmentation_mode_mbank returns the expected MassBank-specific fragmentation mode strings."""
    frag_mode = get_fragmentation_mode_mbank(col_type)
    assert frag_mode == expected_frag_mode


def test_get_fragmentation_mode_mbank_error():
    """Tests if get_fragmentation_mode_mbank returns an error when input is not valid."""
    col_type = 'non_valid_input'
    with pytest.raises(ValueError, match=f"Unknown fragmentation mode {col_type}"):
        get_fragmentation_mode_mbank(col_type)


@pytest.mark.parametrize("pol, expected_ion_mode",[('pos','POSITIVE'),('neg','NEGATIVE')])
def test_get_ion_mode_mbank(pol, expected_ion_mode):
    """Tests if get_ion_mode_mbank returns the expected MassBank-specific ion mode strings."""
    ion_mode = get_ion_mode_mbank(pol)
    assert ion_mode == expected_ion_mode


def test_get_ion_mode_mbank_error():
    """Tests if get_ion_mode_mbank returns an error when input is not valid."""
    pol = 'non_valid_input'
    with pytest.raises(ValueError, match=f"Unknown polarity format {pol}."):
        get_ion_mode_mbank(pol)


@pytest.mark.parametrize("adduct, formula, expected_formula",
                         [('[M]+', 'C9H13NO3', '[C9H13NO3]+'),
                          ('[M]-', 'C9H13NO3', '[C9H13NO3]-')
                          ])
def test_format_formula_mbank(adduct, formula, expected_formula):
    """Tests if format_formula_mbank returns the expected MassBank-specific formula strings."""
    formula_res = format_formula_mbank(adduct, formula)
    assert formula_res == expected_formula


def test_format_spectrum_mbank():
    """Tests if spectrum is correctly formatted and relative intensities are calculated."""
    spectrum =  [(87.0441, 0.0326), (101.060643, 0.04768), (723.468001, 23.0), (233.4, 0.0)]
    expected_formatted_spectrum = [(87.0441, 0.0326, 1), (101.0606, 0.0477, 2), (723.468, 23.0, 999)]
    # Call the function
    formatted_spectrum = format_spectrum_mbank(spectrum)
    assert formatted_spectrum == expected_formatted_spectrum


def test_build_export_chunk_mbank(mock_formatted_data_mbank):
    """Tests if export chunk is correctly assembled."""
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
        "CH$NAME: Compound X\n"
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
    assert export_chunk == expected_export_chunk
