import pytest
from unittest.mock import patch
from rtscan_functions import UpdateWorkflow
from rtscan_functions.rtscan_workflow_utils.rtscan_utils import *


@pytest.mark.parametrize("mock_inst_rt, mock_inst_exp_rt, mock_inst_pred_rt, mock_predict_bfg_rt_called", [
                         # Case 1: Main RT (a) is available as experimental RT
                         (['inst_a', 'inst_b'],  # All available RTs
                          ['inst_a'],  # Experimental RT
                          ['inst_b'],  # Predicted RT
                          False),  # Function to predict main RT not called
                         # Case 2: Main RT (a) is not available as experimental RT, but as predicted RT
                         (['inst_a', 'inst_c'],
                          ['inst_c'],
                          ['inst_a'],
                          False),
                         # Case 3: Main RT (a) is not available and needs to be predicted first
                         (['inst_b'],
                          ['inst_b'],
                          [],
                          True)  # Function to predict main RT called
                         ])
@patch('tqdm.tqdm', lambda x: x)  # Disable tqdm progress bar
def test_rtscan(mock_session, mock_inst_method_pairs, mock_inst_notation_pairs, mock_inst_rt, mock_inst_exp_rt,
                mock_inst_pred_rt, mock_predict_bfg_rt_called):
    with patch('rtscan_functions.update_workflow.DEFAULT_PAIRS_INST_CHROM', mock_inst_method_pairs), \
         patch('rtscan_functions.update_workflow.inst_code_csl_mapping') as mock_default_inst_mapping, \
         patch('rtscan_functions.update_workflow.check_order_pred_bfg_rt') as mock_check_order_pred_bfg_rt, \
         patch('rtscan_functions.update_workflow.update_version') as mock_update_version, \
         patch('shutil.copy'), \
         patch('rtscan_functions.update_workflow.create_session') as mock_create_session, \
         patch('rtscan_functions.update_workflow.get_inst_rt_info') as mock_get_inst_rt_info, \
         patch('rtscan_functions.update_workflow.check_experimental_data') as mock_check_exp_data, \
         patch('rtscan_functions.update_workflow.check_predicted_flags_pred_data') as mock_check_pred_flags, \
         patch('rtscan_functions.update_workflow.predict_bfg_rt') as mock_predict_bfg_rt, \
         patch('rtscan_functions.update_workflow.predict_rt') as mock_predict_rt, \
         patch('rtscan_functions.update_workflow.summarize_corrections_and_errors'), \
         patch('rtscan_functions.update_workflow.commit_changes_choice'):

        # Mock function returns
        mock_default_inst_mapping.return_value = mock_inst_notation_pairs
        mock_create_session.return_value = mock_session
        mock_session.query(RetentionTime.compound_id).all.return_value = [[1443]]
        mock_check_order_pred_bfg_rt.return_value = ['lfuby', 'uba', 'lanuv']
        mock_update_version.return_value = 'mock_filename'
        mock_get_inst_rt_info.return_value = (mock_inst_rt, mock_inst_exp_rt, mock_inst_pred_rt)
        mock_check_exp_data.return_value = ([], [], [])
        mock_check_pred_flags.return_value = []
        mock_predict_bfg_rt.return_value = True
        mock_predict_rt.return_value = True

        # Instantiate workflow with dummy path
        mock_update_workflow = UpdateWorkflow(path_csl='path/to/csl')

        # Execute the rtscan method
        mock_update_workflow.rtscan()

        # Assert
        mock_session.query.assert_called_with(RetentionTime.compound_id)  # Check if query was called
        assert mock_predict_bfg_rt.called == mock_predict_bfg_rt_called
        # Check the number of time other RTs were predicted
        mock_pairs = {mock_inst_notation_pairs[key]: mock_inst_method_pairs[key] for key in mock_inst_method_pairs}
        assert mock_predict_rt.call_count == len(list(set(mock_pairs.keys()) - set(mock_inst_rt)))
