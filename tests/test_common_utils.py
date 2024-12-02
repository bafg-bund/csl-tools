import pytest
from unittest.mock import patch
import os
import tempfile
import pandas as pd

from process_functions.institution_workflow_utils.process_utils import *
from process_functions.institution_workflow_utils.lfuby_utils import extract_data_regex_lfuby


def test_match_file_paths():
    """
    Test that match_file_paths correctly identifies files (also in a subdirectory) containing the identifier string.
    """
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create temporary subdirectory
        os.makedirs(os.path.join(temp_dir, "subdir"))
        # Create temporary files
        file_paths = [
            os.path.join(temp_dir, "file1_test.txt"),
            os.path.join(temp_dir, "file2_testX.txt"),
            os.path.join(temp_dir, "other_file.txt"),  # This one should not be detected
            os.path.join(temp_dir, "subdir", "file4_test.txt")  # Create file in subdirectory
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


# def test_extract_data_regex():
#     # Create test dictionary for regular expression matching of file content
#     var_regex_tmp = {
#         'var_comp': 'Name',
#         'var_inchikey': 'InChiKey',
#         'var_cas': 'CASNo',
#         'var_peak': 'Peak',
#     }
#
#     # Create test file content
#     file_content = """Name: Acetylsalicylic Acid
#     InChiKey: BSYNRYMUTXBXSQ-UHFFFAOYSA-N
#     CASNo: 50-78-2
#     PEAK: m/z int
#     73.0287 14813.86
#     136.0397 154862.31
#     154.0503 72739.36
#     """
#
#     # Define expected output
#     expected_output = [{
#         var_regex_tmp['var_comp']: 'Acetylsalicylic Acid',
#         var_regex_tmp['var_inchikey']: 'BSYNRYMUTXBXSQ-UHFFFAOYSA-N',
#         var_regex_tmp['var_cas']: '50-78-2',
#         var_regex_tmp['var_peak']: ['73.0287 14813.86', '136.0397 154862.31', '154.0503 72739.36']
#     }]
#
#     # Create temporary file with file content
#     with tempfile.NamedTemporaryFile('w+', delete=False) as temp_file:
#         temp_file.write(file_content)
#         temp_file_path = temp_file.name
#
#     try:
#         # Call the function
#         data_extract_tmp = extract_data_regex([temp_file_path], var_regex_tmp)  # todo extract_data_regex need to be changed to neutral once it is combined
#         # Test if the data was correctly extracted
#         assert data_extract_tmp == expected_output, f"Expected {expected_output}, but got {data_extract_tmp}"
#     finally:
#         # Clean up temporary file (even if test fails)
#         os.remove(temp_file_path)


# @pytest.fixture
# def mock_dependencies_process_one_file():
#     """Mock dependencies (sub-function returns) for the function process_one_file."""
#     with patch('process_functions.institution_workflow_utils.get_polarity') as mock_get_polarity, \
#             patch('process_functions.institution_workflow_utils.get_compound_and_adduct_name') as mock_get_compound_and_adduct_name, \
#             patch('process_functions.institution_workflow_utils.format_adduct') as mock_format_adduct, \
#             patch('process_functions.institution_workflow_utils.get_collision_energy') as mock_get_collision_energy, \
#             patch('process_functions.institution_workflow_utils.get_ionization_type') as mock_get_ionization_type, \
#             patch('process_functions.institution_workflow_utils.get_formula') as mock_get_formula, \
#             patch('process_functions.institution_workflow_utils.get_inchikey') as mock_get_inchikey, \
#             patch('process_functions.institution_workflow_utils.get_cas') as mock_get_cas, \
#             patch('process_functions.institution_workflow_utils.get_smiles') as mock_get_smiles, \
#             patch('process_functions.institution_workflow_utils.get_precursor_mz') as mock_get_precursor_mz, \
#             patch('process_functions.institution_workflow_utils.get_retention_time') as mock_get_retention_time, \
#             patch('process_functions.institution_workflow_utils.get_peaks') as mock_get_peaks:
#         yield (mock_get_polarity, mock_get_compound_and_adduct_name, mock_format_adduct,
#                mock_get_collision_energy, mock_get_ionization_type, mock_get_formula,
#                mock_get_inchikey, mock_get_cas, mock_get_smiles,
#                mock_get_precursor_mz, mock_get_retention_time, mock_get_peaks)


# @pytest.mark.parametrize("mock_returns, extract_data, expected_form_data, file_skip, file_warn", [
#     # Test Case 1: Successful processing without skipping or warnings
#     (
#             {
#                 'mock_get_polarity': 'pos',
#                 'mock_get_compound_and_adduct_name': ('Desmedipham', 'NH4'),
#                 'mock_format_adduct': '[M+NH4]+',
#                 'mock_get_collision_energy': (40, 20, False),
#                 'mock_get_ionization_type': 'ESI',
#                 'mock_get_formula': 'C16H16N2O4',
#                 'mock_get_inchikey': ('WZJZMXBKUWKXTQ-UHFFFAOYSA-N', 'WZJZMXBKUWKXTQ'),
#                 'mock_get_cas': '13684-56-5',
#                 'mock_get_smiles': 'C1CCCCC1',
#                 'mock_get_precursor_mz': 318.14,
#                 'mock_get_retention_time': 11.2,
#                 'mock_get_peaks': pd.DataFrame({'mz': [65.1, 73.0], 'int': [25736.5, 10705.9]})
#             },  # mock_returns
#             {
#                 'Name': 'Desmedipham_NH4',
#                 'PrecursorMz': '318.14',
#                 'Collision_energy': '20.00,40.00,60.00',
#                 'Ionization': 'ESI',
#                 'IonMode': 'positive',
#                 'RetentionTime': '11.2',
#                 'InChiKey': 'WZJZMXBKUWKXTQ-UHFFFAOYSA-N',
#                 'Formula': 'C16H16N2O4',
#                 'CASNo': '13684-56-5',
#                 'Smiles': 'C1CCCCC1',
#                 'Peak': ['65.1 25736.5', '73.0 10705.9']
#             },  # extract_data
#             {
#                 'pol_i': 'pos',
#                 'comp_i': 'Desmedipham',
#                 'adduct_i': '[M+NH4]+',
#                 'ce_i': 40,
#                 'ces_i': 20,
#                 'ionization_i': 'ESI',
#                 'formula_i': 'C16H16N2O4',
#                 'inchikey_i': 'WZJZMXBKUWKXTQ-UHFFFAOYSA-N',
#                 'inchikey_main_i': 'WZJZMXBKUWKXTQ',
#                 'cas_i': '13684-56-5',
#                 'smiles_i': 'C1CCCCC1',
#                 'mz_i': 318.14,
#                 'rt_i': 11.2,
#                 'spec_i': pd.DataFrame({'mz': [65.1, 73.0], 'int': [25736.5, 10705.9]})
#             },  # expected_form_data
#             False,  # file_skip
#             False  # file_warn
#     ),
#     # Test Case 2: Skipping due to missing polarity
#     (
#             {
#                 'mock_get_polarity': None,
#                 'mock_get_compound_and_adduct_name': ('Desmedipham', 'NH4'),
#                 'mock_format_adduct': None,
#                 'mock_get_collision_energy': (40, 20, False),
#                 'mock_get_ionization_type': 'ESI',
#                 'mock_get_formula': 'C16H16N2O4',
#                 'mock_get_inchikey': ('WZJZMXBKUWKXTQ-UHFFFAOYSA-N', 'WZJZMXBKUWKXTQ'),
#                 'mock_get_cas': '13684-56-5',
#                 'mock_get_smiles': 'C1CCCCC1',
#                 'mock_get_precursor_mz': 318.14,
#                 'mock_get_retention_time': 11.2,
#                 'mock_get_peaks': pd.DataFrame({'mz': [65.1, 73.0], 'int': [25736.5, 10705.9]})
#             },  # mock_returns
#             {
#                 'Name': 'Desmedipham_NH4',
#                 'PrecursorMz': '318.14',
#                 'Collision_energy': '20.00,40.00,60.00',
#                 'Ionization': 'ESI',
#                 'IonMode': 'unknown',
#                 'RetentionTime': '11.2',
#                 'InChiKey': 'WZJZMXBKUWKXTQ-UHFFFAOYSA-N',
#                 'Formula': 'C16H16N2O4',
#                 'CASNo': '13684-56-5',
#                 'Smiles': 'C1CCCCC1',
#                 'Peak': ['65.1 25736.5', '73.0 10705.9']
#             },  # extract_data
#             {
#                 'pol_i': None,
#                 'comp_i': 'Desmedipham',
#                 'adduct_i': None,
#                 'ce_i': 40,
#                 'ces_i': 20,
#                 'ionization_i': 'ESI',
#                 'formula_i': 'C16H16N2O4',
#                 'inchikey_i': 'WZJZMXBKUWKXTQ-UHFFFAOYSA-N',
#                 'inchikey_main_i': 'WZJZMXBKUWKXTQ',
#                 'cas_i': '13684-56-5',
#                 'smiles_i': 'C1CCCCC1',
#                 'mz_i': 318.14,
#                 'rt_i': 11.2,
#                 'spec_i': pd.DataFrame({'mz': [65.1, 73.0], 'int': [25736.5, 10705.9]})
#             },  # expected_form_data
#             True,  # file_skip
#             False  # file_warn
#     ),
#     # Test Case 3: Not skipping but warning due to unexpected CES
#     (
#             {
#                 'mock_get_polarity': 'pos',
#                 'mock_get_compound_and_adduct_name': ('Desmedipham', 'NH4'),
#                 'mock_format_adduct': '[M+NH4]+',
#                 'mock_get_collision_energy': (40, 10, True),
#                 'mock_get_ionization_type': 'ESI',
#                 'mock_get_formula': 'C16H16N2O4',
#                 'mock_get_inchikey': ('WZJZMXBKUWKXTQ-UHFFFAOYSA-N', 'WZJZMXBKUWKXTQ'),
#                 'mock_get_cas': '13684-56-5',
#                 'mock_get_smiles': 'C1CCCCC1',
#                 'mock_get_precursor_mz': 318.14,
#                 'mock_get_retention_time': 11.2,
#                 'mock_get_peaks': pd.DataFrame({'mz': [65.1, 73.0], 'int': [25736.5, 10705.9]})
#             },  # mock_returns
#             {
#                 'Name': 'Desmedipham_NH4',
#                 'PrecursorMz': '318.14',
#                 'Collision_energy': '30.00,40.00,50.00',
#                 'Ionization': 'ESI',
#                 'IonMode': 'positive',
#                 'RetentionTime': '11.2',
#                 'InChiKey': 'WZJZMXBKUWKXTQ-UHFFFAOYSA-N',
#                 'Formula': 'C16H16N2O4',
#                 'CASNo': '13684-56-5',
#                 'Smiles': 'C1CCCCC1',
#                 'Peak': ['65.1 25736.5', '73.0 10705.9']
#             },  # extract_data
#             {
#                 'pol_i': 'pos',
#                 'comp_i': 'Desmedipham',
#                 'adduct_i': '[M+NH4]+',
#                 'ce_i': 40,
#                 'ces_i': 10,
#                 'ionization_i': 'ESI',
#                 'formula_i': 'C16H16N2O4',
#                 'inchikey_i': 'WZJZMXBKUWKXTQ-UHFFFAOYSA-N',
#                 'inchikey_main_i': 'WZJZMXBKUWKXTQ',
#                 'cas_i': '13684-56-5',
#                 'smiles_i': 'C1CCCCC1',
#                 'mz_i': 318.14,
#                 'rt_i': 11.2,
#                 'spec_i': pd.DataFrame({'mz': [65.1, 73.0], 'int': [25736.5, 10705.9]})
#             },  # expected_form_data
#             False,  # file_skip
#             True  # file_warn
#     )
# ])
# def test_process_one_file(mock_dependencies_process_one_file, mock_returns, extract_data, expected_form_data, file_skip,
#                           file_warn):
#     """Test processing a file with parametrized inputs."""
#     # Get mock dependencies
#     (mock_get_polarity, mock_get_compound_and_adduct_name, mock_format_adduct,
#      mock_get_collision_energy, mock_get_ionization_type, mock_get_formula,
#      mock_get_inchikey, mock_get_cas, mock_get_smiles,
#      mock_get_precursor_mz, mock_get_retention_time, mock_get_peaks) = mock_dependencies_process_one_file
#
#     # Apply the mock return values
#     mock_get_polarity.return_value = mock_returns['mock_get_polarity']
#     mock_get_compound_and_adduct_name.return_value = mock_returns['mock_get_compound_and_adduct_name']
#     mock_format_adduct.return_value = mock_returns['mock_format_adduct']
#     mock_get_collision_energy.return_value = mock_returns['mock_get_collision_energy']
#     mock_get_ionization_type.return_value = mock_returns['mock_get_ionization_type']
#     mock_get_formula.return_value = mock_returns['mock_get_formula']
#     mock_get_inchikey.return_value = mock_returns['mock_get_inchikey']
#     mock_get_cas.return_value = mock_returns['mock_get_cas']
#     mock_get_smiles.return_value = mock_returns['mock_get_smiles']
#     mock_get_precursor_mz.return_value = mock_returns['mock_get_precursor_mz']
#     mock_get_retention_time.return_value = mock_returns['mock_get_retention_time']
#     mock_get_peaks.return_value = mock_returns['mock_get_peaks']
#
#     var_regex = {
#         'var_comp': 'Name',
#         'var_mz': 'PrecursorMz',
#         'var_ce': 'Collision_energy',
#         'var_ionization': 'Ionization',
#         'var_ionmode': 'IonMode',
#         'var_rt': 'RetentionTime',
#         'var_inchikey': 'InChiKey',
#         'var_formula': 'Formula',
#         'var_cas': 'CASNo',
#         'var_smiles': 'Smiles',
#         'var_peak': 'Peak',
#     }
#     inst_def = {'pol_p_def': 'positive', 'pol_n_def': 'negative', 'qf_def': 'QF'}
#     spec_adduct = {'dummy': '[dummy+H]+'}
#
#     # Call the function
#     form_data, skip, warn = process_one_file(extract_data, var_regex, inst_def, spec_adduct)
#
#     # Ensure the actual form_data['spec_i'] DataFrame has consistent data types
#     form_data['spec_i'] = form_data['spec_i'].astype({'mz': 'float64', 'int': 'float64'})
#
#     # Assertions
#     for key in expected_form_data:
#         if isinstance(expected_form_data[key], pd.DataFrame):
#             pd.testing.assert_frame_equal(form_data[key], expected_form_data[key])
#         else:
#             assert form_data[key] == expected_form_data[key]
#
#     assert skip == file_skip
#     assert warn == file_warn


@pytest.mark.parametrize("data_ionmode, expected_pol_i",
                         [('positive', 'pos'), ('negative', 'neg'), ('wrong_string', None)])
def test_get_polarity(data_ionmode, expected_pol_i):
    """Test the function `get_polarity` with parametrized inputs."""
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
    """Test the function `get_compound_and_adduct_name` with parametrized inputs."""
    comp_i, adduct_name = get_compound_and_adduct_name(data_comp)
    assert comp_i == expected_comp_i
    assert adduct_name == expected_adduct_name


@pytest.mark.parametrize("adduct_name, pol_i, expected_adduct_i", [
    ('NH4', 'pos', '[M+NH4]+'),
    ('NH4', 'neg', '[M-NH4]-'),
    (None, 'pos', None),
    (None, None, None),
    ('special', 'pos', 'special_format'),  # Test if spec_adduct is overriding the standard conversion
    ('QF121', 'pos', '[QF121]+'),
    ('QF121', 'neg', '[QF121]-')
])
def test_format_adduct(adduct_name, pol_i, expected_adduct_i):
    """Test the function `format_adduct` with parametrized inputs."""
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
    """Test the function `get_collision_energy` with parametrized inputs."""
    ce_i, ces_i, ces_warn = get_collision_energy(data_ce)
    assert ce_i == expected_ce_i
    assert ces_i == expected_ces_i
    assert ces_warn == expected_ces_warn


@pytest.mark.parametrize("data_ionization, expected_ionization_i",
                         [('ESI', 'ESI'), ('', None)])
def test_get_ionization_type(data_ionization, expected_ionization_i):
    """Test the function `get_ionization_type` with parametrized inputs."""
    ionization_i = get_ionization_type(data_ionization)
    assert ionization_i == expected_ionization_i


@pytest.mark.parametrize("data_formula, expected_form_i",
                         [('C16H16N2O4', 'C16H16N2O4'), ('', None)])
def test_get_formula(data_formula, expected_form_i):
    """Test the function `get_formula` with parametrized inputs."""
    form_i = get_formula(data_formula)
    assert form_i == expected_form_i


@pytest.mark.parametrize("data_inchikey, expected_inchikey_i, expected_inchikey_main_i", [
    ('WZJZMXBKUWKXTQ-UHFFFAOYSA-N', 'WZJZMXBKUWKXTQ-UHFFFAOYSA-N', 'WZJZMXBKUWKXTQ'),
    ('', None, None)
])
def test_get_inchikey(data_inchikey, expected_inchikey_i, expected_inchikey_main_i):
    """Test the function `get_inchikey` with parametrized inputs."""
    inchikey_i, inchikey_main_i = get_inchikey(data_inchikey)
    assert inchikey_i == expected_inchikey_i
    assert inchikey_main_i == expected_inchikey_main_i


@pytest.mark.parametrize("data_cas, expected_cas_i",
                         [('13684-56-5', '13684-56-5'), ('136BA-56-5', None), ('', None)])
def test_get_cas(data_cas, expected_cas_i):
    """Test the function `get_cas` with parametrized inputs."""
    cas_i = get_cas(data_cas)
    assert cas_i == expected_cas_i


@pytest.mark.parametrize("data_smiles, expected_smiles_i",
                         [('CCOC(=O)Nc1cccc(c1)OC(=O)Nc2ccccc2', 'CCOC(=O)Nc1cccc(c1)OC(=O)Nc2ccccc2'), ('', None)])
def test_get_smiles(data_smiles, expected_smiles_i):
    """Test the function `get_smiles` with parametrized inputs."""
    smiles_i = get_smiles(data_smiles)
    assert smiles_i == expected_smiles_i


@pytest.mark.parametrize("data_mz, expected_mz_i",
                         [('318.45672', 318.45672), ('319', 319.0), ('', None)])
def test_get_precursor_mz(data_mz, expected_mz_i):
    """Test the function `get_precursor_mz` with parametrized inputs."""
    mz_i = get_precursor_mz(data_mz)
    assert mz_i == expected_mz_i


@pytest.mark.parametrize("data_rt, expected_rt_i",
                         [('11.24195', 11.24195), ('10', 10.0), ('', None)])
def test_get_retention_time(data_rt, expected_rt_i):
    """Test the function `get_retention_time` with parametrized inputs."""
    rt_i = get_retention_time(data_rt)
    assert rt_i == expected_rt_i


@pytest.mark.parametrize("data_peak, expected_spec_i", [
    (['136.0397 13393.02', '182.0816 349997.91'],
     pd.DataFrame([['136.0397', '13393.02'], ['182.0816', '349997.91']], columns=['mz', 'int'])),
    (['136.0397 13393.02'],
     pd.DataFrame([['136.0397', '13393.02']], columns=['mz', 'int'])),
    ('', pd.DataFrame())
])
def test_get_peaks(data_peak, expected_spec_i):
    """Test the function `get_peaks` with parametrized inputs"""
    spec_i = get_peaks(data_peak)
    pd.testing.assert_frame_equal(spec_i, expected_spec_i)
