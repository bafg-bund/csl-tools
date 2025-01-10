import pytest
from rtscan_functions.rtscan_workflow_utils.rtscan_utils import *
from unittest.mock import patch, MagicMock


def test_get_inst_rt_info(mock_session, mock_inst_method_pairs, mock_inst_notation_pairs):
    """ Test that the function returns the expected institution strings."""
    # Prepare function inputs and return values
    uq_comp_id = 1000
    mock_session.query(RetentionTime.chrom_method).filter_by().all.return_value = [('method_a',), ('method_b',)]
    mock_session.query(ExperimentGroup).join().join().filter().all.return_value = ['inst_a_ExpGroup']
    mock_pairs = {mock_inst_notation_pairs[key]: mock_inst_method_pairs[key] for key in mock_inst_method_pairs}

    # Call the function
    inst_rt, inst_exp_rt, inst_pred_rt = get_inst_rt_info(uq_comp_id, mock_session, mock_pairs)

    # Assert
    assert inst_rt == ['inst_a', 'inst_b']
    assert inst_exp_rt == ['inst_a']
    assert inst_pred_rt == ['inst_b']


@pytest.mark.parametrize("mock_inst, mock_entry_count, expected_query_call_count, mock_pred_bool, expected_pred_bool, "
                         "expected_dupl, expected_pred_to_false",
                         [(['inst_a'], 1, 1, 'FALSE', 'FALSE', [], []),  # One institution
                          (['inst_a', 'inst_b'], 1, 2, 'FALSE', 'FALSE', [], []),  # Two institutions
                          (['inst_a'], 2, 0, 'FALSE', 'FALSE', [99], []),  # Duplicate entries for one institution
                          (['inst_a'], 1, 1, 'TRUE', 'FALSE', [], [99])  # Predicted flag is incorrect
                          ])
def test_check_experimental_data(mock_session, mock_inst_method_pairs, mock_inst_notation_pairs, mock_inst,
                                 mock_entry_count, expected_query_call_count, mock_pred_bool, expected_pred_bool,
                                 expected_dupl, expected_pred_to_false):
    """Parametrized test to check different scenarios."""
    # Prepare function inputs and return values
    uq_comp_id = 99
    mock_inst_exp_rt = mock_inst
    mock_session.query(RetentionTime).filter_by().count.return_value = mock_entry_count
    mock_rt_res = MagicMock(spec=RetentionTime)
    mock_rt_res.predicted = mock_pred_bool
    mock_session.query(RetentionTime).filter_by().one_or_none.return_value = mock_rt_res
    mock_pairs = {mock_inst_notation_pairs[key]: mock_inst_method_pairs[key] for key in mock_inst_method_pairs}

    # Call the function
    dupl, pred_to_false, no_exp_rt = check_experimental_data(
    uq_comp_id, mock_inst_exp_rt, mock_session, mock_pairs)

    # Assert
    assert dupl == expected_dupl
    assert pred_to_false == expected_pred_to_false
    assert no_exp_rt == []
    assert mock_rt_res.predicted == 'FALSE'
    assert mock_session.query().filter_by().one_or_none.call_count == expected_query_call_count


def test_check_experimental_data_no_exp_rt(mock_session, mock_inst_method_pairs, mock_inst_notation_pairs):
    """Test case when no RT is found for an experimental data entry."""
    # Prepare function inputs and return values
    uq_comp_id = 99
    mock_inst_exp_rt = ['inst_a']
    mock_session.query(RetentionTime).filter_by().count.return_value = 0
    mock_session.query(RetentionTime).filter_by().one_or_none.return_value = None
    mock_pairs = {mock_inst_notation_pairs[key]: mock_inst_method_pairs[key] for key in mock_inst_method_pairs}

    # Call the function
    dupl, pred_to_false, no_exp_rt = check_experimental_data(
    uq_comp_id, mock_inst_exp_rt, mock_session, mock_pairs)

    # Assert
    assert dupl == []
    assert pred_to_false == []
    assert no_exp_rt == [99]
    assert mock_session.query().filter_by().one_or_none.call_count == 1


@pytest.mark.parametrize("predicted_flag, expected_pred_to_true", [('TRUE', []), ('FALSE', [99]), (None, [99])])
def test_check_predicted_flags_pred_data(mock_session, mock_inst_method_pairs, mock_inst_notation_pairs, predicted_flag,
                                         expected_pred_to_true):
    """Test that "predicted" flags are corrected as expected."""
    # Prepare function inputs and return values
    uq_comp_id = 99
    mock_inst_pred_rt = ['inst_a']  # Institutions with predicted RTs
    mock_return = MagicMock()
    mock_return.predicted = predicted_flag
    mock_session.query().filter_by().one_or_none.return_value = mock_return
    mock_pairs = {mock_inst_notation_pairs[key]: mock_inst_method_pairs[key] for key in mock_inst_method_pairs}

    # Call the function
    pred_to_true = check_predicted_flags_pred_data(uq_comp_id, mock_inst_pred_rt, mock_session, mock_pairs)

    # Assert
    assert pred_to_true == expected_pred_to_true


def test_predict_bfg_rt(mock_session, mock_models_to_bfg, mock_inst_method_pairs, mock_inst_notation_pairs):
    """Test that the BfG retention time (RT) was predicted correctly and the expected model was used."""
    # Prepare function inputs and return values
    mock_check_order = ['lfuby', 'uba']  # Order of preference
    mock_inst_rt = ['inst_b', 'inst_c']  # Available institutions with RTs
    mock_session.query().filter_by().one_or_none.return_value = [15.0]
    mock_pairs = {mock_inst_notation_pairs[key]: mock_inst_method_pairs[key] for key in mock_inst_method_pairs}

    # Call the function
    predicted_rt = predict_bfg_rt(99, mock_session, mock_models_to_bfg, mock_check_order, mock_inst_rt,
                                  mock_pairs, mock_inst_notation_pairs)

    # Assert
    assert predicted_rt == 7.0
    mock_models_to_bfg['inst_c'].assert_called_once_with(15.0)  # Check if the correct model was called
    mock_session.add.assert_called_once()  # Check if the RT was added to the session


def test_predict_bfg_rt_none(mock_session, mock_models_to_bfg, mock_inst_method_pairs, mock_inst_notation_pairs):
    """Test that the BfG retention time (RT) was not predicted due to missing available institutions with RT data."""
    # Prepare function inputs and return values
    mock_check_order = ['lfuby', 'uba']  # Order of preference
    mock_inst_rt = []  # No available institutions with RTs
    mock_pairs = {mock_inst_notation_pairs[key]: mock_inst_method_pairs[key] for key in mock_inst_method_pairs}

    # Call the function
    predicted_rt = predict_bfg_rt(99, mock_session, mock_models_to_bfg, mock_check_order, mock_inst_rt,
                                  mock_pairs, mock_inst_notation_pairs)

    # Assert
    assert predicted_rt is None


def test_predict_rt(mock_session, mock_models_from_bfg, mock_inst_method_pairs, mock_inst_notation_pairs):
    """Test that the retention time (RT) was predicted correctly and the expected model was used."""
    # Prepare function inputs and return values
    mock_inst_str = 'inst_b'  # Institute that needs prediction of an RT
    mock_session.query().filter_by().one_or_none.return_value = [7.0]
    mock_pairs = {mock_inst_notation_pairs[key]: mock_inst_method_pairs[key] for key in mock_inst_method_pairs}

    # Call the function
    predicted_rt = predict_rt(99, mock_session, mock_models_from_bfg, mock_inst_str, mock_pairs,
                              mock_inst_notation_pairs)

    # Assert
    assert predicted_rt == 12.5
    mock_models_from_bfg['inst_b'].assert_called_once_with(7.0)  # Check if the correct model was called
    mock_session.add.assert_called_once()  # Check if the RT was added to the session


def test_predict_rt_none(mock_session, mock_models_from_bfg, mock_inst_method_pairs, mock_inst_notation_pairs):
    """Test that the retention time (RT) was not predicted due to missing available BfG RT data."""
    # Prepare function inputs and return values
    mock_inst_str = 'inst_b'  # Institute that needs prediction of an RT
    mock_session.query().filter_by().one_or_none.return_value = None
    mock_pairs = {mock_inst_notation_pairs[key]: mock_inst_method_pairs[key] for key in mock_inst_method_pairs}

    # Call the function
    predicted_rt = predict_rt(99, mock_session, mock_models_from_bfg, mock_inst_str, mock_pairs,
                              mock_inst_notation_pairs)

    # Assert
    assert predicted_rt is None


@patch('os.remove')  # Mock os.remove to prevent actual file deletion
def test_commit_changes_choice_commit(mock_remove, mock_session, monkeypatch):
    """Test the scenario where session changes are committed after user confirmation."""
    mock_session.new = True  # Simulate a change in session
    path_csl = "path/to/csl"

    # Mock input to return 'yes'
    monkeypatch.setattr('builtins.input', lambda: 'yes')

    # Call the function
    commit_changes_choice(path_csl, mock_session)

    # Assert
    mock_session.commit.assert_called_once()
    mock_session.close.assert_called_once()
    mock_remove.assert_not_called()


@patch('os.remove')  # Mock os.remove to prevent actual file deletion
def test_commit_changes_choice_no_commit(mock_remove, mock_session, monkeypatch, caplog):
    """Test the scenario where session changes are not committed after user cancels."""
    mock_session.new = True  # Simulate a change in session
    path_csl = "path/to/csl"

    # Mock input to return '' (cancel)
    monkeypatch.setattr('builtins.input', lambda: '')

    # Call the function
    with caplog.at_level('INFO'):
        commit_changes_choice(path_csl, mock_session)

    # Assert
    mock_session.commit.assert_not_called()
    mock_session.close.assert_called_once()
    mock_session.bind.dispose.assert_called_once()
    mock_remove.assert_called_once_with(path_csl)
    assert "Canceled by user. No changes to the CSL committed." in caplog.text


@patch('os.remove')  # Mock os.remove to prevent actual file deletion
def test_commit_changes_choice_no_changes(mock_remove, mock_session, caplog):
    """Test the scenario where there are no session changes to commit."""
    mock_session.new = False  # Simulate no new objects in session
    mock_session.dirty = False  # Simulate no dirty objects in session
    path_csl = "path/to/csl"

    # Call the function
    with caplog.at_level('INFO'):
        commit_changes_choice(path_csl, mock_session)

    # Assert
    mock_session.commit.assert_not_called()
    mock_session.close.assert_called_once()
    mock_session.bind.dispose.assert_called_once()
    mock_remove.assert_called_once_with(path_csl)
    assert "No changes in current session detected." in caplog.text




### Examples for checking : Todo: use for pytests later..
# Example 1 (BfG FALSE)
# 3743	8.82194	lfu_nts_rp1	                            1443
# 3555	16.85	lanuv_nts	                            1443	TRUE
# 2159	9.147	dx.doi.org/10.1016/j.chroma.2015.11.014	1443	FALSE

# Example 2 (BfG TRUE)
# 3854	13.31	dx.doi.org/10.1016/j.chroma.2015.11.014	1672	TRUE
# 3853	11.208	uba_nts_rp1	                            1672	FALSE

# Example 3 (BfG missing)
# 3851	5.703	uba_nts_rp1	    1670	FALSE

# Example 4 (Only LfU, but with prediction = empty)
# 3846	13.27532	lfu_nts_rp1	    1666

# uq_comp_ids = [1443, 1672, 1670, 1666]  # Todo: ..until here

