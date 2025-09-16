from csl.rtscan_functions.update_rtscan import UpdateRtscan
from csl.rtscan_functions.utils.rtscan_utils import *
import pytest
from unittest.mock import patch


@pytest.mark.parametrize("mock_inst_rt, mock_inst_exp_rt, mock_inst_pred_rt, mock_predict_bfg_rt_called", [
                         # Case 1: Main RT (a) is available as experimental RT
                         (['bfg', 'inst_b'],  # All available RTs
                          ['bfg'],  # Experimental RT
                          ['inst_b'],  # Predicted RT
                          False),  # Function to predict main RT not called
                         # Case 2: Main RT (a) is not available as experimental RT, but as predicted RT
                         (['bfg', 'inst_c'],  # All
                          ['inst_c'],  # Experimental
                          ['bfg'],  # Predicted
                          False),  # Function to predict main RT not called
                         # Case 3: Main RT (a) is not available and needs to be predicted first
                         (['inst_b'],  # All
                          ['inst_b'],  # Experimental
                          [],  # Predicted
                          True)  # Function to predict main RT called
                         ])
@patch('tqdm.tqdm', lambda x: x)  # Disable tqdm progress bar
def test_rtscan(mock_session, mock_inst_method_pairs, mock_inst_rt, mock_inst_exp_rt,
                mock_inst_pred_rt, mock_predict_bfg_rt_called):
    """Tests function and query calls for rtscan update workflow."""
    with patch('csl.rtscan_functions.update_rtscan.DEFAULT_PAIRS_INST_CHROM') as mock_inst_method_pairs, \
         patch('csl.rtscan_functions.update_rtscan.check_order_pred_bfg_rt') as mock_check_order_pred_bfg_rt, \
         patch('csl.rtscan_functions.update_rtscan.update_version_filename') as mock_update_version_filename, \
         patch('shutil.copy'), \
         patch('csl.rtscan_functions.update_rtscan.create_session') as mock_create_session, \
         patch('csl.rtscan_functions.update_rtscan.get_inst_rt_info') as mock_get_inst_rt_info, \
         patch('csl.rtscan_functions.update_rtscan.check_experimental_data') as mock_check_exp_data, \
         patch('csl.rtscan_functions.update_rtscan.check_predicted_flags_pred_data') as mock_check_pred_flags, \
         patch('csl.rtscan_functions.update_rtscan.predict_bfg_rt') as mock_predict_bfg_rt, \
         patch('csl.rtscan_functions.update_rtscan.predict_rt') as mock_predict_rt, \
         patch('csl.rtscan_functions.update_rtscan.summarize_corrections_and_errors'), \
         patch('csl.rtscan_functions.update_rtscan.commit_changes_choice'):

        # Mock function returns
        mock_create_session.return_value = mock_session
        mock_session.query(RetentionTime.compound_id).all.return_value = [[1443]]
        mock_check_order_pred_bfg_rt.return_value = ['lfuby', 'uba', 'lanuk']
        mock_update_version_filename.return_value = 'mock_filename'
        mock_get_inst_rt_info.return_value = (mock_inst_rt, mock_inst_exp_rt, mock_inst_pred_rt)
        mock_check_exp_data.return_value = ([], [], [])
        mock_check_pred_flags.return_value = []
        mock_predict_bfg_rt.return_value = True
        mock_predict_rt.return_value = True

        # Instantiate workflow with dummy path
        mock_update_workflow = UpdateRtscan(path_csl='path/to/csl')

        # Execute the rtscan method
        mock_update_workflow.rtscan()

        # Assert that query was called
        mock_session.query.assert_called_with(RetentionTime.compound_id)
        # Assert the function call to predict the main RT
        assert mock_predict_bfg_rt.called == mock_predict_bfg_rt_called
        # Assert that the number of times other RTs were predicted is as expected
        assert mock_predict_rt.call_count == len(list(set(mock_inst_method_pairs.keys()) - set(mock_inst_rt)))
