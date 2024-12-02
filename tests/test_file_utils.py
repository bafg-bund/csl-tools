import pytest
from utils import *
from unittest.mock import patch


def test_validate_file_path_not_exists():
    """Tests if validate_file_path returns the expected FileNotFoundError when path does not exist"""
    with patch('os.path.exists', return_value=False):
        path = "some/path"
        with pytest.raises(FileNotFoundError, match=f'File at {path} does not exist.'):
            validate_file_path(path)


@pytest.mark.parametrize("filename, update_type, year, expected_updated_filename",
                         [('CSL_v24.1.1.db', 'major', 24, 'CSL_v24.2.db'),
                          ('CSL_v24.9.db', 'major', 24, 'CSL_v24.10.db'),
                          ('CSL_v24.0.3.db', 'minor', 24, 'CSL_v24.0.4.db'),
                          ('CSL_v24.1.db', 'minor', 24, 'CSL_v24.1.1.db'),
                          ('CSL_v24.3.1.db', 'major', 25, 'CSL_v25.0.db'),
                          ('CSL_v24.3.1.db', 'minor', 25, 'CSL_v25.0.db'),
                          ('MS_db_v11.db', 'major', 24, 'MS_db_v11_major_edit.db'),  # Old CSL name
                          ('CSL_test.db', 'major', 24, 'CSL_test_major_edit.db'),  # No version number / major
                          ('CSL_test.db', 'minor', 24, 'CSL_test_minor_edit.db')  # No version number / minor
                          ])
def test_update_version(filename, update_type, year, expected_updated_filename):
    """Test correct updated filenames with parametrized inputs."""
    with patch('datetime.datetime') as mock_datetime:
        # Mock the current year
        mock_datetime.now.return_value.strftime.return_value = year
        # Call the function
        update_filename = update_version(filename, update_type)
        # Assert
        assert update_filename == expected_updated_filename
