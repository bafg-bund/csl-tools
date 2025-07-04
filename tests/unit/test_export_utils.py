from csl.export_functions.utils.export_utils import *
from config import ROOT_DIR
from csl.utils.sql_utils import create_session
import pytest
from unittest.mock import patch, Mock, MagicMock
import os


@pytest.mark.parametrize("adduct_form, expected_precursor_charge",
                         [('[M]+', 1), ('[M-2H]2-', 2), ('[M+C2H7N+H]+', 1)])
def test_get_precursor_charge(adduct_form, expected_precursor_charge):
    """Test the function `get_precursor_charge` with parametrized inputs."""
    precursor_charge = get_precursor_charge(adduct_form)
    assert precursor_charge == expected_precursor_charge


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
    expected_spectrum = [(47.07, 10.0), (54.05, 50.0), (55.06, 100.0)]

    # Call the function
    spectrum = get_spectrum(fragments)
    assert spectrum == expected_spectrum


def test_get_splash_code():
    """Tests if get_splash_code returns the expected spectral hash code."""
    mock_spectrum = [(10.1, 1.1), (20.2, 2.2), (30.3, 3.3)]
    expected_temp_spectrum = [(10.1, 1100.0), (20.2, 2200.0), (30.3, 3300.0)]
    with patch('csl.export_functions.utils.export_utils.Spectrum') as MockSpectrum, \
         patch('csl.export_functions.utils.export_utils.Splash') as MockSplash:
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

@pytest.mark.parametrize("data_source, expected_exp_id",
                         [('all', [1, 14166, 34937]),
                          ('bfg', [1]),
                          (['bfg', 'uba'], [1, 34937]),
                          ])
def test_get_experiment_ids_by_exp_group(data_source, expected_exp_id):
    """Tests if the function returns the expected experiment ids based on data source filtering."""

    # Prepare
    csl_path = os.path.join(ROOT_DIR, 'tests/fixtures/export/CSL_v0_export_sqlite_1bfg_1lfuby_1uba.db')
    session = create_session(csl_path)

    # Run function
    exp_id = get_experiment_ids_by_exp_group(session, data_source)

    # Assert
    assert exp_id == expected_exp_id


@pytest.mark.parametrize("chrom_method, expected_exp_id",
                         [('dx.doi.org/10.1016/j.chroma.2015.11.014', [34030, 12249, 14224, 31447]),
                          ('lfu_nts_rp1', [34030, 14224, 31447]),
                          ('uba_nts_rp1', [14224, 31447]),
                          ('lanuv_nts', [31447]),
                          ])
def test_get_experiment_ids_by_chrom_method(chrom_method, expected_exp_id):
    """Tests if the function returns the expected experiment ids based on chrom. method filtering."""

    # Prepare
    csl_path = os.path.join(ROOT_DIR, 'tests/fixtures/csl_testfiles/CSL_v0_export_4expid_chrommethod.db')
    session = create_session(csl_path)

    # Run function
    exp_id = get_experiment_ids_by_chrom_method(session, chrom_method)

    # Assert
    assert set(exp_id) == set(expected_exp_id)
