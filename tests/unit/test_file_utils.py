from csl.utils import *
import pytest
from unittest.mock import patch


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
def test_update_version_filename(filename, update_type, year, expected_updated_filename):
    """Tests if filenames are correctly updated with parametrized inputs."""
    with patch('datetime.datetime') as mock_datetime:
        # Mock the current year
        mock_datetime.now.return_value.strftime.return_value = year
        # Call the function
        update_filename = update_version_filename(filename, update_type)
        # Assert that the updated filename is as expected
        assert update_filename == expected_updated_filename


@pytest.mark.parametrize("csl_path, expected_csl_version",
                         [('CSL_v24.0.4.db', '24.0.4'),
                          ('CSL_v0.db', '0'),
                          ('CSL_v25.1_subset.db', '25.1'),
                          ('CSL_v25.1-subset.db', '25.1'),
                          ('CSL_v25.1-subset_1.2.db', '25.1'),
                          ('CSL_v25.1test.db', '25.1'),
                          ('CSL_v0sub_test.db', '0'),
                          ('C:User/user/CSL_v2.8_test/CSL_v25.7.db', '25.7')
                          ])
def test_get_csl_version(csl_path, expected_csl_version):
    """Tests correct version extraction based on CSL path or CSL filename."""
    csl_version = get_csl_version(csl_path)
    assert csl_version == expected_csl_version

@pytest.mark.parametrize("csl_path", ['CSL_v_test.db', 'CSL_v0.1'])
def test_get_csl_version_error(csl_path):
    """Tests if errors are raised when filename does not match expected pattern."""
    with pytest.raises(ValueError):
        get_csl_version(csl_path)
