import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from process_functions import LfubyWorkflow


@pytest.mark.parametrize("mock_files", [(['file1.txt', 'file2.txt']), (['one_file.txt'])])
@patch('process_functions.lfuby_workflow.match_file_paths')
@patch('process_functions.lfuby_workflow.extract_data_regex_lfuby')
def test_read_files_dir(mock_extract_data_regex, mock_match_file_paths, mock_files):
    """Test that the sub-functions of read_files behave correctly when input is a directory path string."""
    with patch('os.path.isfile', return_value=False):
        # Configure the mocks
        mock_var_regex = MagicMock()
        mock_match_file_paths.return_value = mock_files

        # Use side_effect to return a new DataFrame for each call
        mock_extract_data_regex.side_effect = [
            pd.DataFrame({"file_path": [None]}),
            pd.DataFrame({"file_path": [None]})
        ]

        # Instantiate LfubyWorkflow with dummy paths for testing
        workflow = LfubyWorkflow(path_data='dummy_dir_path', path_csl='dummy_csl_path')
        # Call the read_files method
        extract_data = workflow.read_files(mock_var_regex)

        # Assert
        mock_match_file_paths.assert_called_once()
        assert mock_extract_data_regex.call_count == len(mock_files)
        assert all(extract_data == pd.DataFrame({"file_path": mock_files}))


@patch('process_functions.lfuby_workflow.match_file_paths')
@patch('process_functions.lfuby_workflow.extract_data_regex_lfuby')
def test_read_files_single_file(mock_extract_data_regex, mock_match_file_paths):
    """Test that the sub-functions of read_files behave correctly when input is a single file path string."""
    with patch('os.path.isfile', return_value=True):
        # Configure the mocks
        mock_var_regex = MagicMock()
        mock_extract_data_regex.return_value = pd.DataFrame({"file_path": [None]})

        # Instantiate LfubyWorkflow with dummy paths for testing
        workflow = LfubyWorkflow(path_data='dummy_file.txt', path_csl='dummy_csl_path')
        # Call the read_files method
        extract_data = workflow.read_files(mock_var_regex)

        # Assert
        mock_match_file_paths.assert_not_called()
        assert mock_extract_data_regex.call_count == 1
        assert all(extract_data == pd.DataFrame({"file_path": ['dummy_file.txt']}))


@pytest.mark.parametrize("mock_files", [(['file1.txt', 'file2.txt']), (['one_file.txt'])])
@patch('process_functions.lfuby_workflow.match_file_paths')
@patch('process_functions.lfuby_workflow.extract_data_regex_lfuby')
def test_read_files_mult_files(mock_extract_data_regex, mock_match_file_paths, mock_files):
    """Test that the sub-functions of read_files behave correctly when input is a list of file string(s)."""
    # Configure the mocks
    mock_var_regex = MagicMock()
    mock_extract_data_regex.return_value = pd.DataFrame({"file_path": [None]})

    # Instantiate LfubyWorkflow with dummy paths for testing
    workflow = LfubyWorkflow(path_data=mock_files, path_csl='dummy_csl_path')
    # Call the read_files method
    extract_data = workflow.read_files(mock_var_regex)

    # Assert
    mock_match_file_paths.assert_not_called()
    assert mock_extract_data_regex.call_count == len(mock_files)
    assert all(extract_data == pd.DataFrame({"file_path": mock_files}))
