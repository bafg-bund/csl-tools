import pytest
from unittest.mock import patch
import os
import tempfile
import pandas as pd
from process_functions.utils.process_utils import *


@pytest.mark.parametrize("mock_data_paths, mock_isfile, expected_file_paths",
                         [('one_file.txt', True, ['one_file.txt']),  # Expect conversion to list for single file str
                          (['file1.txt', 'file2.txt'], None, ['file1.txt', 'file2.txt']),  # Expect no changes
                          ('dir', False, ['dir/file.txt']),  # Expect use of mock function `mock_match_file_paths`
                          ])  # List of file str should be unchanged.
@patch('process_functions.utils.process_utils.match_file_paths')
def test_get_file_paths(mock_match_file_paths, mock_data_paths, mock_isfile, expected_file_paths):
    """Test if file paths are correctly returned."""
    with patch('os.path.isfile', return_value=mock_isfile):
        mock_match_file_paths.return_value = expected_file_paths
        file_paths = get_file_paths(mock_data_paths)

    assert file_paths == expected_file_paths


def test_match_file_paths():
    """Test if files are found and correctly identified."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create temporary subdirectory
        os.makedirs(os.path.join(temp_dir, "subdir"))
        # Create temporary files
        file_paths = [
            os.path.join(temp_dir, "file1_test.txt"),
            os.path.join(temp_dir, "file2_testX.txt"),
            os.path.join(temp_dir, "other_file.txt"),  # This one should not be detected
            os.path.join(temp_dir, "subdir", "file4_test.txt")  # File should be found in subdirectory
        ]

        for file_path in file_paths:
            with open(file_path, 'w') as f:
                f.write('some_content')

        # Call the function
        matched_file_paths = match_file_paths(temp_dir, 'test')

        # Expected matched file paths
        expected_file_paths = [
            os.path.join(temp_dir, "file1_test.txt"),
            os.path.join(temp_dir, "file2_testX.txt"),
            os.path.join(temp_dir, "subdir", "file4_test.txt")
        ]

        # Sort the lists to ensure order doesn't matter
        matched_file_paths.sort()
        expected_file_paths.sort()

        # Verify that the matched files are correct
        assert matched_file_paths == expected_file_paths, f"Expected {expected_file_paths}, but got {matched_file_paths}"


# Todo: add test for get_user_choice


@pytest.mark.parametrize("data_ionmode, expected_pol_i",
                         [('positive', 'pos'), ('negative', 'neg'), ('wrong_string', None)])
def test_get_polarity(data_ionmode, expected_pol_i):
    """Test the function with parametrized inputs."""
    pol_i = get_polarity(data_ionmode, 'positive', 'negative')
    assert pol_i == expected_pol_i


@pytest.mark.parametrize("data_comp, expected_comp_i, expected_adduct_name", [
    ('CompoundName_AdductName', 'CompoundName', 'AdductName'),
    ('CompoundName', 'CompoundName', 'H'),
    ('CompoundName_AdductName_AdditionalString', None, None),
    ('CompoundName_', None, None),
    ('', None, None),
    ('_', None, None)
])
def test_get_compound_and_adduct_name(data_comp, expected_comp_i, expected_adduct_name):
    """Test the function with parametrized inputs."""
    comp_i, adduct_name = get_compound_and_adduct_name(data_comp)
    assert comp_i == expected_comp_i
    assert adduct_name == expected_adduct_name


@pytest.mark.parametrize("adduct_name, pol_i, expected_adduct_i", [
    ('H', 'pos', '[M+H]+'),
    ('NH4', 'neg', '[M-NH4]-'),
    (None, 'pos', None),
    (None, None, None),
    ('special', 'pos', 'special_format'),  # Test if spec_adduct is overriding the standard conversion
    ('QF121', 'pos', '[QF121]+'),
    ('QF121', 'neg', '[QF121]-'),
    ('[M]+', 'pos', '[M]+'),
])
def test_format_adduct(adduct_name, pol_i, expected_adduct_i):
    """Test the function with parametrized inputs."""
    adduct_i = format_adduct(adduct_name, {'special': 'special_format'}, 'QF', pol_i)
    assert adduct_i == expected_adduct_i


@pytest.mark.parametrize("data_ce, expected_ce_i, expected_ces_i, expected_ces_warn", [
    ('10', 10, 0, False),
    ('20, 40, 60', 40, 20, False),
    ('-10', 10, 0, False),  # Negative input values are transformed to positive values
    ('-20, -40, -60', 40, 20, False),
    ('20.00,40.00,60.00', 40, 20, False),
    ('10, 20, 30', 20, 10, True),  # Warning when CES is not 20
    ('10, 20, 50', None, None, False),  # Non-equal difference in CES
    ('20, 40', None, None, False),  # Unexpected number of CE
    ('', None, None, False)  # No data
])
def test_get_collision_energy(data_ce, expected_ce_i, expected_ces_i, expected_ces_warn):
    """Test the function with parametrized inputs."""
    ce_i, ces_i, ces_warn = get_collision_energy(data_ce)
    assert ce_i == expected_ce_i
    assert ces_i == expected_ces_i
    assert ces_warn == expected_ces_warn


@pytest.mark.parametrize("data_ionization, expected_ionization_i",
                         [('ESI', 'ESI'), ('', None)])
def test_get_ionization_type(data_ionization, expected_ionization_i):
    """Test the function with parametrized inputs."""
    ionization_i = get_ionization_type(data_ionization)
    assert ionization_i == expected_ionization_i


@pytest.mark.parametrize("data_formula, expected_form_i",
                         [('C16H16N2O4', 'C16H16N2O4'), ('', None), ('[C18H24N]+','C18H24N'), ('[C18H24N]-','C18H24N')])
def test_get_formula(data_formula, expected_form_i):
    """Test the function with parametrized inputs."""
    form_i = get_formula(data_formula)
    assert form_i == expected_form_i


@pytest.mark.parametrize("data_inchikey, expected_inchikey_i, expected_inchikey_main_i", [
    ('WZJZMXBKUWKXTQ-UHFFFAOYSA-N', 'WZJZMXBKUWKXTQ-UHFFFAOYSA-N', 'WZJZMXBKUWKXTQ'),
    ('', None, None)
])
def test_get_inchikey(data_inchikey, expected_inchikey_i, expected_inchikey_main_i):
    """Test the function with parametrized inputs."""
    inchikey_i, inchikey_main_i = get_inchikey(data_inchikey)
    assert inchikey_i == expected_inchikey_i
    assert inchikey_main_i == expected_inchikey_main_i


@pytest.mark.parametrize("data_cas, expected_cas_i",
                         [('13684-56-5', '13684-56-5'), ('136BA-56-5', None), ('', None)])
def test_get_cas(data_cas, expected_cas_i):
    """Test the function with parametrized inputs."""
    cas_i = get_cas(data_cas)
    assert cas_i == expected_cas_i


@pytest.mark.parametrize("data_smiles, expected_smiles_i",
                         [('CCOC(=O)Nc1cccc(c1)OC(=O)Nc2ccccc2', 'CCOC(=O)Nc1cccc(c1)OC(=O)Nc2ccccc2'), ('', None)])
def test_get_smiles(data_smiles, expected_smiles_i):
    """Test the function with parametrized inputs."""
    smiles_i = get_smiles(data_smiles)
    assert smiles_i == expected_smiles_i


@pytest.mark.parametrize("smiles_i, expected_inchi_i",
                         [('CCO', 'InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3'), ('', None), (None, None)])
def test_get_inchi_from_smiles(smiles_i, expected_inchi_i):
    """Test the function with parametrized inputs."""
    inchi_i = get_inchi_from_smiles(smiles_i)
    assert inchi_i == expected_inchi_i


@pytest.mark.parametrize("data_mz, expected_mz_i",
                         [('318.45672', 318.45672), ('319', 319.0), ('', None)])
def test_get_precursor_mz(data_mz, expected_mz_i):
    """Test the function with parametrized inputs."""
    mz_i = get_precursor_mz(data_mz)
    assert mz_i == expected_mz_i


@pytest.mark.parametrize("data_rt, expected_rt_i",
                         [('11.24195', 11.24195), ('10', 10.0), ('', None), ('12 min', 12.0)])
def test_get_retention_time(data_rt, expected_rt_i):
    """Test the function with parametrized inputs."""
    rt_i = get_retention_time(data_rt)
    assert rt_i == expected_rt_i


@pytest.mark.parametrize("data_peak, expected_spec_i", [
    (['136.0397 13393.02', '182.0816 349997.91'],  # Two entries
     pd.DataFrame([['136.0397', '13393.02'], ['182.0816', '349997.91']], columns=['mz', 'int'])),
    (['136.0397 13393.02'],  # Only one entry
     pd.DataFrame([['136.0397', '13393.02']], columns=['mz', 'int'])),
    ('', pd.DataFrame()),  # Empty DataFrame
    ('55.0603 2 219',pd.DataFrame([['55.0603', '2']], columns=['mz', 'int'])),  # Only the first two columns
])
def test_get_peaks(data_peak, expected_spec_i):
    """Test the function with parametrized inputs."""
    spec_i = get_peaks(data_peak)
    pd.testing.assert_frame_equal(spec_i, expected_spec_i)


@pytest.mark.parametrize("data_col_type, expected_col_type_i", [('CID', 'Q'),('HCD', 'HCD')])
def test_get_collision_type(data_col_type, expected_col_type_i):
    """Test the function with parametrized inputs."""
    col_type_i = get_collision_type(data_col_type)
    assert col_type_i == expected_col_type_i


@pytest.mark.parametrize("data_instrument, data_instrument_type, expected_instrument_i",
                         [('TripleTOF 5600 SCIEX', 'LC-ESI-QTOF', 'LC-ESI-QTOF TripleTOF 5600 SCIEX'),
                          ('LC-ESI-QTOF TripleTOF 5600 SCIEX', None, 'LC-ESI-QTOF TripleTOF 5600 SCIEX'),
                          ('QExactive','LC-ESI-Orbitrap','LC-ESI-Orbitrap QExactive')])
def test_get_instrument(data_instrument, data_instrument_type, expected_instrument_i):
    """Test the function with parametrized inputs."""
    instrument_i = get_instrument(data_instrument, data_instrument_type)
    assert instrument_i == expected_instrument_i


@pytest.mark.parametrize("data_accession, expected_experiment_id_i",
                         [('MSBNK-BAFG-CSL23110949', '49'), (None, None), ('MSBNK-BAFG-CSL231109', None)])
def test_get_experiment_id(data_accession, expected_experiment_id_i):
    """Test the function with parametrized inputs."""
    experiment_id_i = get_experiment_id(data_accession)
    assert experiment_id_i == expected_experiment_id_i
