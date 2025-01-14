import pytest
from unittest.mock import patch, Mock, MagicMock
from export_functions.format_workflow_utils.mbank_utils import *


@pytest.mark.parametrize("exp_group, year, expected_inst_copyright",
                         [('BfG', '2025', 'Copyright 2025 Federal Institute of Hydrology, Koblenz, Germany'),
                          ('LfU', '2025', 'Copyright 2025 Bavarian Environment Agency, Augsburg, Germany'),
                          ('UBA', '2025', 'Copyright 2025 Federal Environment Agency, Berlin, Germany'),
                          ('not_an_institution', '2025', None)
                          ])
def test_get_contributors_copyright(exp_group, year, expected_inst_copyright):
    """Tests if get_contributors_copyright returns the expected copyright statements."""
    with patch('datetime.datetime') as mock_datetime:
        # Mock the current year
        mock_datetime.now.return_value.strftime.return_value = year
        # Call the function
        _, inst_copyright, _, _ = get_contributors_copyright(exp_group)
        # Assert
        assert inst_copyright == expected_inst_copyright


@pytest.mark.parametrize("col_type, expected_frag_mode",[('Q','CID'),('HCD','HCD')])
def test_get_fragmentation_mode(col_type, expected_frag_mode):
    """Tests if get_fragmentation_mode returns the expected MassBank-specific fragmentation mode strings."""
    frag_mode = get_fragmentation_mode(col_type)
    assert frag_mode == expected_frag_mode

def test_get_fragmentation_mode_error():
    """Tests if get_fragmentation_mode returns an error when input is not valid."""
    col_type = 'non_valid_input'
    with pytest.raises(ValueError, match=f"Unknown fragmentation mode {col_type}"):
        get_fragmentation_mode(col_type)


@pytest.mark.parametrize("pol, expected_ion_mode",[('pos','POSITIVE'),('neg','NEGATIVE')])
def test_get_ion_mode(pol, expected_ion_mode):
    """Tests if get_ion_mode returns the expected MassBank-specific ion mode strings."""
    ion_mode = get_ion_mode(pol)
    assert ion_mode == expected_ion_mode

def test_get_ion_mode_error():
    """Tests if get_ion_mode returns an error when input is not valid."""
    pol = 'non_valid_input'
    with pytest.raises(ValueError, match=f"Unknown polarity format {pol}."):
        get_ion_mode(pol)


def test_get_compound_classes():
    """Tests if get_compound_classes returns only non-institutional compound classes in the MassBank specific format."""
    # Mock objects with a 'name' attribute
    compound_groups = [
        Mock(name="BfG"),
        Mock(name="Industrial_process"),
        Mock(name="Pharmaceutical"),
    ]
    # Set the 'name' attribute for each Mock explicitly
    for mock, value in zip(compound_groups, ["BfG", "Industrial_process", "Pharmaceutical"]):
        mock.name = value
    # Call the function
    compound_classes = get_compound_classes(compound_groups)
    assert compound_classes == 'Industrial_process; Pharmaceutical'

def test_get_compound_classes_none():
    """Tests if get_compound_classes returns None when input is only institutional compound classes."""
    # Mock objects with a 'name' attribute
    compound_groups = [
        Mock(name="BfG"),
        Mock(name="LfU"),
    ]
    # Set the 'name' attribute for each Mock explicitly
    for mock, value in zip(compound_groups, ["BfG", "LfU"]):
        mock.name = value
    # Call the function
    compound_classes = get_compound_classes(compound_groups)
    assert compound_classes is None


@pytest.mark.parametrize("adduct, formula, expected_formula",
                         [('[M]+', 'C9H13NO3', '[C9H13NO3]+'),
                          ('[M]-', 'C9H13NO3', '[C9H13NO3]-')
                          ])
def test_format_formula(adduct, formula, expected_formula):
    """Tests if format_formula returns the expected MassBank-specific formula strings."""
    formula_res = format_formula(adduct, formula)
    assert formula_res == expected_formula


def test_get_splash_code():
    """Tests if get_splash_code returns the expected spectral hash code."""
    mock_spectrum = [(10.1, 1.1), (20.2, 2.2), (30.3, 3.3)]
    expected_temp_spectrum = [(10.1, 1100.0), (20.2, 2200.0), (30.3, 3300.0)]
    with patch('export_functions.format_workflow_utils.mbank_utils.Spectrum') as MockSpectrum, \
         patch('export_functions.format_workflow_utils.mbank_utils.Splash') as MockSplash:
        # Prepare mocks
        mock_spec = MagicMock()
        MockSpectrum.return_value = mock_spec
        mock_splash = MagicMock()
        mock_splash.splash.return_value = "splash10-009x-6900000000-306b1298d1ks43m5fsj6"
        MockSplash.return_value = mock_splash
        # Call the function
        splash_code = get_splash_code(mock_spectrum)
        # Assert
        MockSpectrum.assert_called_once_with(expected_temp_spectrum, 1)
        assert splash_code == "splash10-009x-6900000000-306b1298d1ks43m5fsj6"


def test_format_spectrum():
    """Tests if spectrum is correctly formatted."""
    spectrum =  [(87.0441, 0.0326, 1), (101.060643, 0.04768, 2), (723.468001, 23.0, 999), (233.4, 0.0, 0)]
    expected_formatted_spectrum = [(87.0441, 0.0326, 1), (101.0606, 0.0477, 2), (723.468, 23.0, 999)]
    # Call the function
    formatted_spectrum = format_spectrum(spectrum)
    assert formatted_spectrum == expected_formatted_spectrum


def test_get_spectrum():
    """Tests if spectrum is correctly sorted and relative intensities are calculated."""
    # Prepare data
    class Fragments:
        def __init__(self, mz, intensity, exp_id):
            self.mz = mz
            self.int = intensity
            self.exp_id = exp_id

        def __repr__(self):
            return f"mz = {self.mz}, int = {self.int}, exp_id = {self.exp_id}"

    fragments = [
        Fragments(54.05, 50.0, 1),
        Fragments(55.06, 100.0, 1),
        Fragments(47.07, 10.0, 1)
    ]
    expected_spectrum = [(47.07, 10.0, 99), (54.05, 50.0, 499), (55.06, 100.0, 999)]

    # Call the function
    spectrum = get_spectrum(fragments)
    assert spectrum == expected_spectrum


def test_build_export_chunk(mock_formatted_data_mbank):
    """Tests if export chunk is correctly assembled."""
    # Prepare data
    csl_version = "25.0.0"
    pycsl_version = "1.0.0"
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
    export_chunk = build_export_chunk(mock_formatted_data_mbank, csl_version, pycsl_version)
    assert export_chunk == expected_export_chunk

