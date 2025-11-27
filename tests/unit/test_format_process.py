from csl.process_functions.format_process import FormatProcess
import pytest
from unittest.mock import patch
import pandas as pd


# Define a fixture for the TestProcess class
@pytest.fixture
def workflow():
    class TestProcess(FormatProcess):
        def extract_data_regex(self, file, var_regex, file_extra=None):
            """Mock return for the function `extract_data_regex`."""
            return pd.DataFrame([{"var_comp": "Test", "var_ce": 10, "file_path": file}])

    return TestProcess(path_data='data_path', path_csl='csl_path', path_config='config_path', path_extra='extra_path')


class TestFormatProcess:

    def test_process_data(self, workflow, mock_extract_data, mock_dsrc_def, mock_spec_adduct):
        """Tests processing of sample data without creating warning or error flags."""

        with patch('csl.process_functions.format_process.get_polarity', return_value='polarity'), \
             patch('csl.process_functions.format_process.get_compound_and_adduct_name',
                      return_value=('comp', 'adduct')), \
             patch('csl.process_functions.format_process.format_adduct', return_value='formatted_adduct'), \
             patch('csl.process_functions.format_process.get_collision_energy',
                      return_value=('ce', 'ces')), \
             patch('csl.process_functions.format_process.get_ionization_type', return_value='ionization_type'), \
             patch('csl.process_functions.format_process.get_formula', return_value='formula'), \
             patch('csl.process_functions.format_process.get_inchikey',
                      return_value=('inchikey', 'inchikey_main')), \
             patch('csl.process_functions.format_process.get_cas', return_value='cas'), \
             patch('csl.process_functions.format_process.get_smiles', return_value='smiles'), \
             patch('csl.process_functions.format_process.get_inchi_from_smiles', return_value='inchi'), \
             patch('csl.process_functions.format_process.get_precursor_mz', return_value=99), \
             patch('csl.process_functions.format_process.get_retention_time', return_value=99), \
             patch('csl.process_functions.format_process.get_peaks',
                      return_value=pd.DataFrame({'peak': [9.9, 9.9, 9.9]})), \
             patch('csl.process_functions.format_process.get_compound_group',
                      return_value=['Pesticide', 'Herbicide']), \
             patch('csl.process_functions.format_process.get_instrument', return_value='instrument'), \
             patch('csl.process_functions.format_process.get_experiment_id', return_value='experiment_id'):

            # Call the process_data method
            form_data = workflow.process_data(mock_extract_data, mock_dsrc_def, mock_spec_adduct)

            # Assert that the returned data is a DataFrame and contains the expected flags
            assert isinstance(form_data, pd.DataFrame)
            assert 'form_err_flag' in form_data.columns
            assert 'form_warn_flag' in form_data.columns
            assert all(form_data['form_err_flag']) is False
            assert all(form_data['form_warn_flag']) is False


    def test_process_data_inchi_cas_none(self, workflow, mock_extract_data, mock_dsrc_def, mock_spec_adduct):
        """Tests processing of sample data with missing InChIKey and CAS."""

        with patch('csl.process_functions.format_process.get_polarity',return_value='polarity'), \
             patch('csl.process_functions.format_process.get_compound_and_adduct_name',
                   return_value=('comp', 'adduct')), \
             patch('csl.process_functions.format_process.format_adduct',return_value='formatted_adduct'), \
             patch('csl.process_functions.format_process.get_collision_energy',
                   return_value=('ce', 'ces')), \
             patch('csl.process_functions.format_process.get_ionization_type', return_value='ionization_type'), \
             patch('csl.process_functions.format_process.get_formula', return_value='formula'), \
             patch('csl.process_functions.format_process.get_inchikey', return_value=(None, None)), \
             patch('csl.process_functions.format_process.get_cas', return_value=None), \
             patch('csl.process_functions.format_process.get_smiles', return_value='smiles'), \
             patch('csl.process_functions.format_process.get_inchi_from_smiles', return_value='inchi'), \
             patch('csl.process_functions.format_process.get_precursor_mz', return_value=99), \
             patch('csl.process_functions.format_process.get_retention_time', return_value=99), \
             patch('csl.process_functions.format_process.get_peaks',
                  return_value=pd.DataFrame({'peak': [9.9, 9.9, 9.9]})), \
             patch('csl.process_functions.format_process.get_compound_group',
                  return_value=['Pesticide', 'Herbicide']), \
             patch('csl.process_functions.format_process.get_instrument', return_value='instrument'), \
             patch('csl.process_functions.format_process.get_experiment_id', return_value='experiment_id'):

            # Call the method
            form_data = workflow.process_data(mock_extract_data, mock_dsrc_def, mock_spec_adduct)

            # Assert that the returned data is a DataFrame and contains the expected flags
            assert isinstance(form_data, pd.DataFrame)
            assert 'form_err_flag' in form_data.columns
            assert 'form_warn_flag' in form_data.columns
            assert all(form_data['form_err_flag']) is True
            assert all(form_data['form_warn_flag']) is True


    @pytest.fixture
    def mock_dependencies_match_with_csl(self):
        """Mock dependencies (sub-function returns) for the function match_with_csl."""
        with patch('csl.process_functions.format_process.create_session') as mock_create_session, \
             patch('csl.process_functions.format_process.check_duplicate') as mock_check_duplicate, \
             patch('csl.process_functions.format_process.add_exp_to_session') as mock_add_exp_to_session:
             yield mock_create_session, mock_check_duplicate, mock_add_exp_to_session

    @pytest.mark.parametrize("mock_res_count, expected_dupl_flag, expected_err_flag, expected_add_flag",
                             [(0, False, False, True),   # Case with no duplicate CSL match
                              (1, True, False, False),   # Case with a duplicate CSL match
                              (-1, False, True, False)]  # Case with no CSL matching due to missing InChIKey and CAS
                             )
    def test_match_with_csl(self, workflow, mock_dependencies_match_with_csl, mock_session, mock_format_data,
                            mock_res_count, expected_dupl_flag, expected_err_flag, expected_add_flag):
        """Tests adding of entries to the session depending on input flags."""
        # Prepare mocks
        mock_create_session, mock_check_duplicate, mock_add_exp_to_session = mock_dependencies_match_with_csl

        # Add relevant data to the DataFrame fixture
        tmp_data = {
            'var_comp': ['compound1'],
            'var_ce': ['40'],
            'file_path': ['file1']
        }
        mock_format_data = pd.concat(objs=[mock_format_data, pd.DataFrame(tmp_data)], axis='columns')

        # Mock return values
        mock_create_session.return_value = mock_session
        mock_check_duplicate.return_value = mock_res_count

        # Call the method
        form_data_match, session_out = workflow.match_with_csl(mock_format_data)

        # Assert that calls were made as expected
        if expected_add_flag:
            mock_add_exp_to_session.assert_called_once()
        else:
            mock_add_exp_to_session.assert_not_called()
        assert mock_check_duplicate.call_count == len(mock_format_data)

        # Assert that flags are set to the expected bool
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
    def test_commit_to_csl(self, workflow, mock_session, mock_logger, monkeypatch, mock_form_data_match, user_input):
        """Tests committing scenarios with different flags and user input."""
        # Mock user input
        with patch('builtins.input', return_value=user_input) as mock_input:
            # Call the method
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
            mock_session.close.assert_called_once()
