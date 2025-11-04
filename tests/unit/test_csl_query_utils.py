from csl.process_functions.utils import check_duplicate, add_exp_to_session
from unittest.mock import MagicMock
import pytest


@pytest.mark.parametrize("inchikey_main, cas, expected_result_count, expected_count_callcount, expected_all_callcount",
                         [("", "1234-12-3", 0, 2, 0),       # No InChIKey present
                          ("BSYNRYMUTXBXSQ", "", 0, 2, 0),  # No CAS present
                          ("", "", -1, 0, 0),               # Both not present
                          ("BSYNRYMUTXBXSQ","1234-12-3", 0, 1, 2)])  # Both present
def test_check_duplicate_inchikey_cas_variants(mock_session, mock_entry_df, inchikey_main, cas, expected_result_count,
                                      expected_count_callcount, expected_all_callcount):
    """
    Tests function return when checking for duplicates with different data input for InChIKey and CAS,
    assuming no duplicates present in CSL file and assuming available experiment id for double check.
    """
    # Mock query calls
    mock_query = MagicMock()
    mock_query.join.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.count.return_value = 0
    mock_query.all.return_value = []
    mock_session.query.return_value = mock_query

    # Prepare input data
    entry_df = mock_entry_df.copy()
    entry_df['inchikey_main_i'] = inchikey_main
    entry_df['cas_i'] = cas

    # Call the function
    result = check_duplicate(mock_session, entry_df)

    # Assert that the function return and call counts are as expected
    assert result == expected_result_count
    assert mock_query.count.call_count == expected_count_callcount
    assert mock_query.all.call_count == expected_all_callcount


def test_add_exp_to_session_data_src_not_exists(mock_session, mock_entry_df):
    """Tests if call is made to add missing data source."""
    # Mock query calls
    mock_query = MagicMock()
    mock_query.query.return_value = mock_query
    mock_query.filter_by.return_value = mock_query
    mock_query.one_or_none.return_value = None
    mock_session.query.return_value = mock_query

    # Call the function
    add_exp_to_session(mock_session, mock_entry_df)

    # Assert that the expected string ('mock_dsrc') is in any of the calls
    calls = mock_session.add.call_args_list  # List of calls made
    assert any(call[0][0].name == mock_entry_df['var_dsrc_csl'] for call in calls)
