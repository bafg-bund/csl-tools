import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from process_functions import InstitutionWorkflow


@patch('process_functions.institution_workflow.get_polarity', return_value='polarity')
@patch('process_functions.institution_workflow.get_compound_and_adduct_name', return_value=('comp', 'adduct'))
@patch('process_functions.institution_workflow.format_adduct', return_value='formatted_adduct')
@patch('process_functions.institution_workflow.get_collision_energy', return_value=('ce', 'ces', False))
@patch('process_functions.institution_workflow.get_ionization_type', return_value='ionization_type')
@patch('process_functions.institution_workflow.get_formula', return_value='formula')
@patch('process_functions.institution_workflow.get_inchikey', return_value=('inchikey', 'inchikey_main'))
@patch('process_functions.institution_workflow.get_cas', return_value='cas')
@patch('process_functions.institution_workflow.get_smiles', return_value='smiles')
@patch('process_functions.institution_workflow.get_inchi_from_smiles', return_value='inchi')
@patch('process_functions.institution_workflow.get_precursor_mz', return_value=99)
@patch('process_functions.institution_workflow.get_retention_time', return_value=99)
@patch('process_functions.institution_workflow.get_peaks', return_value=pd.DataFrame({'peak': [9.9, 9.9, 9.9]}))
@patch('process_functions.institution_workflow.get_compound_group', return_value=['Pesticide','Herbicide'])
def test_process_data(mock_get_compound_group, mock_get_peaks, mock_get_retention_time, mock_get_precursor_mz,
                      mock_get_inchi_from_smiles, mock_get_smiles, mock_get_cas, mock_get_inchikey, mock_get_formula,
                      mock_get_ionization_type, mock_get_collision_energy, mock_format_adduct,
                      mock_get_compound_and_adduct_name, mock_get_polarity, mock_extract_data, mock_inst_def,
                      mock_spec_adduct):
    """Test processing of sample data without creating warning or error flags."""

    # Instantiate the InstitutionWorkflow class
    workflow = InstitutionWorkflow(path_data='dummy_data_path', path_csl='dummy_csl_path')
    # Call the process_data method
    form_data = workflow.process_data(mock_extract_data, mock_inst_def, mock_spec_adduct)

    # Assert
    assert isinstance(form_data, pd.DataFrame)
    assert 'form_err_flag' in form_data.columns
    assert 'form_warn_flag' in form_data.columns
    assert all(form_data['form_err_flag']) is False
    assert all(form_data['form_warn_flag']) is False


@patch('process_functions.institution_workflow.get_polarity', return_value='polarity')
@patch('process_functions.institution_workflow.get_compound_and_adduct_name', return_value=('comp', 'adduct'))
@patch('process_functions.institution_workflow.format_adduct', return_value='formatted_adduct')
@patch('process_functions.institution_workflow.get_collision_energy', return_value=('ce', 'ces', False))
@patch('process_functions.institution_workflow.get_ionization_type', return_value='ionization_type')
@patch('process_functions.institution_workflow.get_formula', return_value='formula')
@patch('process_functions.institution_workflow.get_inchikey', return_value=(None, None))
@patch('process_functions.institution_workflow.get_cas', return_value=None)
@patch('process_functions.institution_workflow.get_smiles', return_value='smiles')
@patch('process_functions.institution_workflow.get_inchi_from_smiles', return_value='inchi')
@patch('process_functions.institution_workflow.get_precursor_mz', return_value=99)
@patch('process_functions.institution_workflow.get_retention_time', return_value=99)
@patch('process_functions.institution_workflow.get_peaks', return_value=pd.DataFrame({'peak': [9.9, 9.9, 9.9]}))
@patch('process_functions.institution_workflow.get_compound_group', return_value=['Pesticide','Herbicide'])
def test_process_data_inchi_cas_none(mock_get_compound_group, mock_get_peaks, mock_get_retention_time,
                                     mock_get_precursor_mz, mock_get_inchi_from_smiles, mock_get_smiles, mock_get_cas,
                                     mock_get_inchikey, mock_get_formula, mock_get_ionization_type,
                                     mock_get_collision_energy, mock_format_adduct, mock_get_compound_and_adduct_name,
                                     mock_get_polarity, mock_extract_data, mock_inst_def, mock_spec_adduct):
    """Test processing of sample data without creating warning or error flags."""

    # Instantiate the InstitutionWorkflow class
    workflow = InstitutionWorkflow(path_data='dummy_data_path', path_csl='dummy_csl_path')
    # Call the process_data method
    form_data = workflow.process_data(mock_extract_data, mock_inst_def, mock_spec_adduct)

    # Assert
    assert isinstance(form_data, pd.DataFrame)
    assert 'form_err_flag' in form_data.columns
    assert 'form_warn_flag' in form_data.columns
    assert all(form_data['form_err_flag'] == True)
    assert all(form_data['form_warn_flag'] == True)
    mock_get_polarity.assert_called_once_with('mock_ion_mode', 'mock_pol_p', 'mock_pol_n')
    mock_get_compound_and_adduct_name.assert_called_once_with('mock_compound')
    mock_format_adduct.assert_called_once_with('adduct', mock_spec_adduct, 'mock_qf', 'polarity')


@pytest.fixture
def mock_dependencies_match_with_csl():
    """Mock dependencies (sub-function returns) for the function match_with_csl."""
    with patch('process_functions.institution_workflow.create_session') as mock_create_session, \
            patch('process_functions.institution_workflow.check_duplicate') as mock_check_duplicate, \
            patch('process_functions.institution_workflow.add_exp_to_session') as mock_add_exp_to_session:
        yield mock_create_session, mock_check_duplicate, mock_add_exp_to_session


@pytest.mark.parametrize("mock_res_count, expected_dupl_flag, expected_err_flag, expected_add_flag",
                         [(0, False, False, True),  # Case with no duplicate CSL match
                          (1, True, False, False),  # Case with a duplicate CSL match
                          (-1, False, True, False)]  # Case with no attempted CSL matching due to missing inchi and cas
                         )
def test_match_with_csl(mock_dependencies_match_with_csl, mock_session, mock_format_data, mock_inst_def,
                        mock_res_count, expected_dupl_flag, expected_err_flag, expected_add_flag):
    """Test if match_with_csl correctly adds entries to session depending on flags."""

    mock_create_session, mock_check_duplicate, mock_add_exp_to_session = mock_dependencies_match_with_csl

    # Add relevant data to DataFrame fixture
    tmp_data = {
        'var_comp': ['compound1'],
        'var_ce': ['40'],
        'file_path': ['file1']
    }
    mock_format_data = pd.concat(objs=[mock_format_data, pd.DataFrame(tmp_data)], axis='columns')

    # Mock return values
    mock_create_session.return_value = mock_session
    mock_check_duplicate.return_value = mock_res_count

    # Instantiate the InstitutionWorkflow class
    workflow = InstitutionWorkflow(path_data='dummy_data_path', path_csl='dummy_csl_path')
    # Call the match_with_csl method
    form_data_match, session_out = workflow.match_with_csl(mock_format_data, mock_inst_def)

    # Assert
    if expected_add_flag:
        mock_add_exp_to_session.assert_called_once()
    else:
        mock_add_exp_to_session.assert_not_called()
    assert mock_check_duplicate.call_count == len(mock_format_data)
    assert all(form_data_match['csl_dupl_flag']) == expected_dupl_flag
    assert all(form_data_match['csl_err_flag']) == expected_err_flag
    assert all(form_data_match['csl_add_flag']) == expected_add_flag


@pytest.mark.parametrize("mock_form_data_match, user_input",
                         [
                             # Case 1: All data entries eligible for CSL commit; User confirms;
                             (pd.DataFrame({
                                            'comp_i': ['compound1', 'compound2'],
                                            'ce_i': ['40', '30'],
                                            'file_path': ['file1', 'file2'],
                                            'form_err_flag': [False, False],
                                            'form_warn_flag': [False, False],
                                            'csl_dupl_flag': [False, False],
                                            'csl_err_flag': [False, False],
                                            'csl_add_flag': [True, True]}),
                              'yes'),
                             # Case 2: One error flag; One data entry eligible for CSL commit; User confirms
                             (pd.DataFrame({'comp_i': ['compound1', 'compound2'],
                                            'ce_i': ['40', '30'],
                                            'file_path': ['file1', 'file2'],
                                            'form_err_flag': [False, False],
                                            'form_warn_flag': [False, False],
                                            'csl_dupl_flag': [False, False],
                                            'csl_err_flag': [False, True],
                                            'csl_add_flag': [True, False]}),
                              'yes'),
                             # Case 3: All data entries eligible for CSL commit; User cancels;
                             (pd.DataFrame({'comp_i': ['compound1', 'compound2'],
                                            'ce_i': ['40', '30'],
                                            'file_path': ['file1', 'file2'],
                                            'form_err_flag': [False, False],
                                            'form_warn_flag': [False, False],
                                            'csl_dupl_flag': [False, False],
                                            'csl_err_flag': [False, False],
                                            'csl_add_flag': [True, True]}),
                              'any_other_input'),
                             # Case 4: No data entries are eligible for CSL commit;
                             (pd.DataFrame({'comp_i': ['compound1', 'compound2'],
                                            'ce_i': ['40', '30'],
                                            'file_path': ['file1', 'file2'],
                                            'form_err_flag': [False, False],
                                            'form_warn_flag': [False, False],
                                            'csl_dupl_flag': [True, True],
                                            'csl_err_flag': [False, False],
                                            'csl_add_flag': [False, False]}),
                              ''),
                         ])
def test_commit_to_csl(mock_session, mock_logger, monkeypatch, mock_form_data_match, user_input):
    """Test scenarios with different flags and user input."""

    # Mock user input
    with patch('builtins.input', return_value=user_input) as mock_input:
        # Instantiate the InstitutionWorkflow class
        workflow = InstitutionWorkflow(path_data='dummy_data_path', path_csl='dummy_csl_path')
        # Call the commit_to_csl method
        workflow.commit_to_csl(mock_session, mock_form_data_match)

        # Assert session calls
        if any(mock_form_data_match.csl_add_flag) and user_input == 'yes':
            mock_session.commit.assert_called_once()
        else:
            mock_session.commit.assert_not_called()
        if any(mock_form_data_match.form_err_flag) or any(mock_form_data_match.csl_err_flag):
            mock_logger.error.assert_called()
        if any(mock_form_data_match.form_warn_flag) or any(mock_form_data_match.csl_dupl_flag):
            mock_logger.warning.assert_called()
        if not any(mock_form_data_match.csl_add_flag):
            mock_input.assert_not_called()


        # session_change = mock_session.new or session.dirty  # todo test if session.dirty is none if no changes were made
        # print(f'session change is {session_change}')

        mock_session.close.assert_called_once()  # Session should always be closed
