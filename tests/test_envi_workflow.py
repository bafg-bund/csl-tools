from unittest.mock import patch, MagicMock
from export_functions import EnviWorkflow


def test_csl_query_envi(mock_session, mock_df_envi):
    """Test if csl_query_envi correctly returns a DataFrame."""
    with patch('export_functions.envi_workflow.create_session') as mock_create_session, \
         patch('pandas.read_sql') as mock_read_sql:

        # Instantiate EnviWorkflow with dummy paths for testing
        workflow = EnviWorkflow(path_out='dummy_path_out', path_csl='dummy_csl_path')

        # Mock session query returns
        mock_create_session.return_value = mock_session
        mock_query = MagicMock()
        mock_session.return_value.query.return_value = mock_query

        # Mock return of a DataFrame
        mock_read_sql.return_value = mock_df_envi

        # Call the csl_query_envi method
        df = workflow.csl_query_envi([30, 45], 0, ['Inst1, Inst2'], 'chrom_method')[0]

        # Ensure that add_exp_to_session was called the expected number of times
        mock_create_session.assert_called_once()
        assert mock_session.query.call_count == 2
        assert not df.empty
        assert len(df) == 2
        assert 'name' in df.columns
        assert 'experiment_id' in df.columns


def test_process_data_envi(mock_df_envi):
    """Test if process_data_envi correctly formats the DataFrame."""

    mock_fragment_data = [
        MagicMock(experiment_id=1, mz=100.0, int=50),
        MagicMock(experiment_id=2, mz=200.0, int=100)
    ]

    fragment_cutoff_percent = 20

    # Instantiate EnviWorkflow with dummy paths for testing
    workflow = EnviWorkflow(path_out='dummy_path_out', path_csl='dummy_csl_path')

    # Call the function
    df_formatted = workflow.process_data_envi(mock_df_envi, mock_fragment_data, fragment_cutoff_percent)

    # Validate processed DataFrame
    assert not df_formatted.empty
    assert 'Fragments' in df_formatted.columns
    assert 'Name' in df_formatted.columns
    assert 'ID' in df_formatted.columns
    assert df_formatted.loc[0, 'Fragments'] != ""  # Assuming there is at least one fragment meeting criteria


def test_get_mz_fragments_int_cutoff():
    """Test return of get_mz_fragments_int_cutoff function with different input conditions."""
    # Create test data for fragments
    fragments = [(100.0, 30), (150.0, 100), (200.0, 75)]  # (m/z, intensity)

    # Test different cutoff values
    assert EnviWorkflow.get_mz_fragments_int_cutoff(fragments, 20) == "100.0, 150.0, 200.0"
    assert EnviWorkflow.get_mz_fragments_int_cutoff(fragments, 50) == "150.0, 200.0"
    assert EnviWorkflow.get_mz_fragments_int_cutoff(fragments, 80) == "150.0"
    # Test empty fragments list case
    assert EnviWorkflow.get_mz_fragments_int_cutoff([], 20) == ""
