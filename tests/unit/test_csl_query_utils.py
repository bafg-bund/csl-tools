from csl.process_functions.utils import check_duplicate, add_exp_to_session
from unittest.mock import MagicMock


def test_check_duplicate_inchikey_only(mock_session, mock_entry_df):
    """Test result count when checking for duplicates only with the InChIKey present."""
    # Mock query calls
    mock_query = MagicMock()
    mock_query.join.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.count.return_value = 1
    mock_session.query.return_value = mock_query

    entry_df = mock_entry_df.copy()
    entry_df['cas_i'] = ''  # CAS RN is empty

    # Call the function
    result = check_duplicate(mock_session, entry_df)

    # Assert
    assert result == 1
    mock_query.count.assert_called_once()


def test_check_duplicate_cas_only(mock_session, mock_entry_df):
    """Test result count when checking for duplicates only with the CAS registry number present."""
    # Mock query calls
    mock_query = MagicMock()
    mock_query.join.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.count.return_value = 1
    mock_session.query.return_value = mock_query

    entry_df = mock_entry_df.copy()
    entry_df['inchikey_main_i'] = ''  # InChIKey is empty

    # Call the function
    result = check_duplicate(mock_session, entry_df)

    # Assert
    assert result == 1
    mock_query.count.assert_called_once()


def test_check_duplicate_inchikey_and_cas(mock_session, mock_entry_df):
    """Test result count when checking for duplicates with both the InChIKey and the CAS registry number present."""
    # Mock query calls
    mock_query = MagicMock()
    mock_query.join.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [('13384-57-5', 'compoundX', 99.0, 7.0, 'pos')]  # Same result for both queries
    mock_session.query.return_value = mock_query

    # Call the function
    result = check_duplicate(mock_session, mock_entry_df)

    # Assert
    assert result == 1
    assert mock_query.all.call_count == 2


def test_check_duplicate_no_inchikey_and_cas(mock_session, mock_entry_df):
    """Test result count when checking for duplicates with both the InChIKey and the CAS registry number missing."""
    # Mock query calls
    mock_query = MagicMock()
    mock_query.join.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_session.query.return_value = mock_query

    entry_df = mock_entry_df.copy()
    entry_df['inchikey_main_i'] = ''  # InChIKey is empty
    entry_df['cas_i'] = ''  # CAS RN is empty

    # Call the function
    result = check_duplicate(mock_session, entry_df)

    # Assert
    assert result == -1
    mock_query.count.assert_not_called()


def test_add_exp_to_session_exp_group_not_exists(mock_session, mock_entry_df, mock_inst_def):
    """Test if call is made to add experiment group when it is missing.
    Todo: Don't add more tests for this function before it is not reworked (quality, smaller parts). """
    # Mock query calls
    mock_query = MagicMock()
    mock_query.query.return_value = mock_query
    mock_query.filter_by.return_value = mock_query
    mock_query.one_or_none.return_value = None
    mock_session.query.return_value = mock_query

    # Call the function
    add_exp_to_session(mock_session, mock_entry_df, mock_inst_def)

    # Assert if the expected string ('mock_expg') is in any of the calls
    calls = mock_session.add.call_args_list  # List of calls made
    assert any(call[0][0].name == mock_entry_df['var_expg_csl'] for call in calls)
