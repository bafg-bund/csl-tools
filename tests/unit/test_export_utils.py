from csl.export_functions.utils.export_utils import *
from csl.config import ROOT_DIR
from csl.utils.sql_utils import create_session
import pytest
from unittest.mock import patch, Mock, MagicMock
import os


@pytest.mark.parametrize("adduct_form, expected_precursor_charge",
                         [('[M]+', 1), ('[M-2H]2-', 2), ('[M+C2H7N+H]+', 1)])
def test_get_precursor_charge(adduct_form, expected_precursor_charge):
    """Tests function return with parametrized inputs."""
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

    # Assert
    assert spectrum == expected_spectrum


def test_get_splash_code():
    """Tests if the function returns the expected spectral hash code."""
    # Prepare mocks
    mock_spectrum = [(10.1, 1.1), (20.2, 2.2), (30.3, 3.3)]
    expected_temp_spectrum = [(10.1, 1100.0), (20.2, 2200.0), (30.3, 3300.0)]
    with patch('csl.export_functions.utils.export_utils.Spectrum') as MockSpectrum, \
         patch('csl.export_functions.utils.export_utils.Splash') as MockSplash:

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
    """Tests if the function removes "Uncategorized" and duplicate compound classes in the MassBank specific format."""
    # Mock objects with a 'name' attribute
    compound_groups = [
        Mock(name="Biocide"),
        Mock(name="Biocide"),
        Mock(name="Pharmaceutical"),
        Mock(name="Uncategorized"),
    ]
    for mock, value in zip(compound_groups, ["Biocide", "Biocide", "Pharmaceutical", "Uncategorized"]):
        mock.name = value

    # Call the function
    compound_classes = get_compound_classes(compound_groups)

    # Assert that the expected compound classes are returned
    assert compound_classes == 'Biocide; Pharmaceutical'


def test_get_compound_classes_none():
    """Tests if the function returns None when input compound class is only "Uncategorized"."""
    # Mock objects with a 'name' attribute
    compound_groups = [
        Mock(name="Uncategorized"),
    ]
    for mock, value in zip(compound_groups, ["Uncategorized"]):
        mock.name = value

    # Call the function
    compound_classes = get_compound_classes(compound_groups)

    # Assert that no compound classes are returned
    assert compound_classes is None


@pytest.mark.parametrize("dsrc_name, dsrc_long_name, dsrc_authors, year, expected_dsrc_copyright",
                         [('bfg', 'Data source A', 'Name A; Name B', '2025', 'Copyright 2025 Data source A'),
                          ('lfuby', 'Data source B', 'Name C', '2025', 'Copyright 2025 Data source B'),
                          ])
def test_get_contributors_copyright(dsrc_name, dsrc_long_name, dsrc_authors, year, expected_dsrc_copyright):
    """Tests if the function returns the expected copyright statements."""

    # Mock the DataSource object
    mock_data_src = Mock()
    mock_data_src.name = dsrc_name
    mock_data_src.long_name = dsrc_long_name
    mock_data_src.authors = dsrc_authors

    with patch('datetime.datetime') as mock_datetime:
        # Mock the current year
        mock_datetime.now.return_value.strftime.return_value = year
        # Call the function
        _, dsrc_copyright, _, _ = get_contributors_copyright(mock_data_src)
        # Assert
        assert dsrc_copyright == expected_dsrc_copyright

@pytest.mark.parametrize("data_source, expected_exp_id",
                         [('all', [1, 14166, 34937]),
                          ('bfg', [1]),
                          (['bfg', 'uba'], [1, 34937]),
                          ])
def test_get_experiment_ids_by_data_src(data_source, expected_exp_id):
    """Tests if the function returns the expected experiment ids with different data source filtering."""
    # Prepare
    csl_path = os.path.join(ROOT_DIR, 'tests/fixtures/export/CSL_v0_export_sqlite_1bfg_1lfuby_1uba.db')
    session = create_session(csl_path)
    # Call the function
    exp_id = get_experiment_ids_by_data_src(session, data_source)
    # Assert that the expected experiment ids are returned
    assert exp_id == expected_exp_id


@pytest.mark.parametrize("chrom_method, predicted, expected_exp_id",
                         [('bfg_nts_rp1', None, [34030, 12249, 14224, 31447]),
                          ('bfg_nts_rp1', False, [34030, 12249, 14224]),
                          ('bfg_nts_rp1', True, [31447]),
                          ('bfg_nts_rp1', "True", [31447]),
                          ('lfuby_nts_rp1', False, [34030, 14224]),
                          ('uba_nts_rp1', False, [31447]),
                          ('lanuk_nts_rp1', False, []),
                          ])
def test_get_experiment_ids_by_chrom_method(chrom_method, predicted, expected_exp_id):
    """Tests if the function returns the expected experiment ids with different chromatographic method filtering."""
    # Prepare
    csl_path = os.path.join(ROOT_DIR, 'tests/fixtures/csl_testfiles/CSL_v0_export_4expid_chrommethod.db')
    session = create_session(csl_path)
    # Call the function
    exp_id = get_experiment_ids_by_chrom_method(session, chrom_method, predicted)
    # Assert that the expected experiment ids are returned
    assert set(exp_id) == set(expected_exp_id)
