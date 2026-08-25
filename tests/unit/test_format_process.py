from csl.process_functions.format_process import FormatProcess
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd


# Fixture for the TestProcess class
@pytest.fixture
def workflow():
    class TestProcess(FormatProcess):
        def extract_data_regex(self, file, par_regex, file_extra=None):
            """Mock return for the function `extract_data_regex`."""
            return pd.DataFrame([{"par_comp": "Test", "par_ce": 10, "file_path": file}])

    return TestProcess(path_data='data_path', path_csl='csl_path', path_config='config_path', path_extra='extra_path')


class TestFormatProcess:

    @pytest.fixture
    # Patch all format_process functions for valid return values
    def mocked_format_process_functions(self, mocker):
        mocker.patch('csl.process_functions.format_process.get_instrument', return_value='instrument')
        mocker.patch('csl.process_functions.format_process.get_polarity', return_value='polarity'),
        mocker.patch('csl.process_functions.format_process.get_compound_and_adduct_name',
              return_value=('comp', 'adduct')),
        mocker.patch('csl.process_functions.format_process.format_adduct', return_value='formatted_adduct'),
        mocker.patch('csl.process_functions.format_process.get_collision_energy', return_value=(40, 0, 'V')),
        mocker.patch('csl.process_functions.format_process.get_electron_energy', return_value=(70, 'eV')),
        mocker.patch('csl.process_functions.format_process.get_ionization_type', return_value='ionization_type'),
        mocker.patch('csl.process_functions.format_process.get_formula', return_value='formula'),
        mocker.patch('csl.process_functions.format_process.get_inchikey',
              return_value=('inchikey', 'inchikey_main')),
        mocker.patch('csl.process_functions.format_process.get_cas', return_value='cas'),
        mocker.patch('csl.process_functions.format_process.get_smiles', return_value='smiles'),
        mocker.patch('csl.process_functions.format_process.get_inchi_from_smiles', return_value='inchi'),
        mocker.patch('csl.process_functions.format_process.get_precursor_mz', return_value=99),
        mocker.patch('csl.process_functions.format_process.get_retention_time', return_value=99),
        mocker.patch('csl.process_functions.format_process.get_peaks',
              return_value=pd.DataFrame({'peak': [9.9, 9.9, 9.9]})),
        mocker.patch('csl.process_functions.format_process.get_compound_group',
              return_value=['Pesticide', 'Herbicide']),
        mocker.patch('csl.process_functions.format_process.get_collision_type', return_value='col_type'),
        mocker.patch('csl.process_functions.format_process.get_experiment_id', return_value='experiment_id'),
        mocker.patch('csl.process_functions.format_process.get_exact_mass_adduct_mass',
              return_value=([9.9], [1.0])),
        mocker.patch('csl.process_functions.format_process.get_isotope', return_value='isotope')
        mocker.patch('csl.process_functions.format_process.get_retention_time_index', return_value=1022.11),
        mocker.patch('csl.process_functions.format_process.get_pubchem_id', return_value=1005)

    def test_process_data(self, workflow, mock_extract_data, mock_dsrc_def, mock_spec_adduct, mocked_format_process_functions):
        """Tests processing of sample data without creating warning or error flags."""

        # Call the process_data method
        form_data = workflow.process_data(mock_extract_data, mock_dsrc_def, mock_spec_adduct)

        # Assert that the returned data is a DataFrame and contains the expected flags
        assert isinstance(form_data, pd.DataFrame)
        assert 'form_err_flag' in form_data.columns
        assert 'form_warn_flag' in form_data.columns
        assert all(form_data['form_err_flag']) is False
        assert all(form_data['form_warn_flag']) is False


    def test_process_data_inchi_cas_none(self, workflow, mock_extract_data, mock_dsrc_def, mock_spec_adduct, mocked_format_process_functions, mocker):
        """Tests processing of sample data with missing InChIKey and CAS."""

        mocker.patch('csl.process_functions.format_process.get_inchikey', return_value=(None, None))
        mocker.patch('csl.process_functions.format_process.get_cas', return_value=None)

        # Call the method
        form_data = workflow.process_data(mock_extract_data, mock_dsrc_def, mock_spec_adduct)

        # Assert that the returned data is a DataFrame and contains the expected flags
        assert isinstance(form_data, pd.DataFrame)
        assert 'form_err_flag' in form_data.columns
        assert 'form_warn_flag' in form_data.columns
        assert all(form_data['form_err_flag']) is True
        assert all(form_data['form_warn_flag']) is True


    def test_process_data_all_err(self, workflow, mock_extract_data, mock_dsrc_def, mock_spec_adduct, mocked_format_process_functions, mocker):
        """Tests all errors with logger warnings where processing continues."""
        mock_logger = MagicMock()
        with patch("logging.getLogger", return_value=mock_logger):

            mocker.patch('csl.process_functions.format_process.get_polarity',return_value=None),
            mocker.patch('csl.process_functions.format_process.get_compound_and_adduct_name', return_value=(None, None)),
            mocker.patch('csl.process_functions.format_process.format_adduct',return_value=None),
            mocker.patch('csl.process_functions.format_process.get_collision_energy', return_value=(None, None, None)),
            mocker.patch('csl.process_functions.format_process.get_electron_energy', return_value=(None, None)),
            mocker.patch('csl.process_functions.format_process.get_ionization_type', return_value=None),
            mocker.patch('csl.process_functions.format_process.get_formula', return_value=None),
            mocker.patch('csl.process_functions.format_process.get_inchikey', return_value=(None, None)),
            mocker.patch('csl.process_functions.format_process.get_cas', return_value=None),
            mocker.patch('csl.process_functions.format_process.get_smiles', return_value=None),
            mocker.patch('csl.process_functions.format_process.get_inchi_from_smiles', return_value=None),
            mocker.patch('csl.process_functions.format_process.get_precursor_mz', return_value=None),
            mocker.patch('csl.process_functions.format_process.get_retention_time', return_value=None),
            mocker.patch('csl.process_functions.format_process.get_peaks', return_value=pd.DataFrame({'peak': []})),
            mocker.patch('csl.process_functions.format_process.get_compound_group', return_value=[]),
            mocker.patch('csl.process_functions.format_process.get_collision_type', return_value=None),
            mocker.patch('csl.process_functions.format_process.get_experiment_id', return_value=None),
            mocker.patch('csl.process_functions.format_process.get_exact_mass_adduct_mass', return_value=(None, None))
            mocker.patch('csl.process_functions.format_process.get_isotope', return_value=None)

            # Call the method
            form_data = workflow.process_data(mock_extract_data, mock_dsrc_def, mock_spec_adduct)

            # Assert the number of logger warning calls
            assert mock_logger.warning.call_count == 17

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
            'par_comp': ['compound1'],
            'par_ce': ['40'],
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
                                 (pd.DataFrame({'form_err_flag': [False, False],
                                                'form_warn_flag': [False, False],
                                                'csl_dupl_flag': [False, False],
                                                'csl_err_flag': [False, False],
                                                'csl_add_flag': [True, True]}),
                                  'yes'),
                                 # Case 2: All data entries eligible for CSL commit; User cancels;
                                 (pd.DataFrame({'form_err_flag': [False, False],
                                                'form_warn_flag': [False, False],
                                                'csl_dupl_flag': [False, False],
                                                'csl_err_flag': [False, False],
                                                'csl_add_flag': [True, True]}),
                                  'any_other_input'),
                                 # Case 3: One error; One format warning entry eligible for CSL commit; User confirms;
                                 (pd.DataFrame({'form_err_flag': [False, False],
                                                'form_warn_flag': [False, True],
                                                'csl_dupl_flag': [False, False],
                                                'csl_err_flag': [True, False],
                                                'csl_add_flag': [False, True]}),
                                  'yes'),

                                 # Case 4: One duplicate, One format error; No data entries are eligible for CSL commit;
                                 (pd.DataFrame({'form_err_flag': [False, True],
                                                'form_warn_flag': [False, False],
                                                'csl_dupl_flag': [True, False],
                                                'csl_err_flag': [False, False],
                                                'csl_add_flag': [False, False]}),
                                 ''),
                             ])
    def test_summarize_and_commit_to_csl(self, workflow, mock_session, mock_logger, monkeypatch, mock_form_data_match, user_input):
        """Tests committing scenarios with different flags and user input."""
        # Mock user input
        with patch('builtins.input', return_value=user_input) as mock_input:

            # Prepare mock data
            mock_extract_data_add = pd.DataFrame({'par_comp': ['comp_a', 'comp_b']})
            form_data_match_add = pd.DataFrame({
                'pol_i': ['pos', 'neg'],
                'comp_i': ['compound1', 'compound2'],
                'adduct_i': ['adduct1', 'adduct2'],
                'ionization_i': ['ESI', 'ESI'],
                'formula_i': ['C1', 'C1'],
                'inchikey_i': ['INCHIKEY', 'INCHIKEY'],
                'cas_i': ['25-7', '25-7'],
                'smiles_i': ['CCCC', 'CCCC'],
                'mz_i': ['7', '7'],
                'rt_i': ['7', '7'],
                'spec_i': ['7', '7'],
                'col_type_i': ['Q', 'Q'],
                'instrument_i': ['instrument_a', 'instrument_b'],
                'ce_i': ['40', '30'],
                'ces_i': ['0', '15'],
                'par_ion_mode': ['P', 'N'],
                'file_path': ['file1', 'file2']})
            mock_form_data_match = mock_form_data_match.join(form_data_match_add)

            # Call the method
            workflow.summarize_and_commit_to_csl(mock_session, mock_extract_data_add, mock_form_data_match)

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
