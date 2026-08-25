from csl.main_functions.rtscan import scan_rt
from csl.utils.sql_utils import create_session, RetentionTime
from csl.config import ROOT_DIR
import os
import shutil
from pathlib import Path
from unittest import mock


def test_rtscan_recalc():
    """Tests replacing of all predicted retention times (RTs) entries with recalculated values."""
    # Prepare paths
    csl_template_path = os.path.join(ROOT_DIR,'tests/fixtures/rtscan/CSL_v0_rtscan.db')
    csl_copy_path =  os.path.join(ROOT_DIR,'tests/integration/temp/CSL_v0_rtscan.db')
    temp_path = os.path.join(ROOT_DIR,'tests/integration/temp')

    # Create temp_path folder if necessary
    Path(temp_path).mkdir(parents=False, exist_ok=True)

    # Make sure temp directory is clean
    for f in Path(temp_path).iterdir():
        try:
            if f.is_file() or f.is_symlink():
                f.unlink()  # Delete file or symlink
            elif f.is_dir():
                shutil.rmtree(f)  # Delete directory and contents
        except PermissionError as e:
            print(f"Could not delete {f}: {e}")

    # Copy the database file
    shutil.copy(csl_template_path, csl_copy_path)

    # Get relevant information from copied template database file
    session_template = create_session(csl_copy_path)
    no_rt_entries_template = len(session_template.query(RetentionTime).all())
    pred_rt_entries_template =  [rt for (rt,) in session_template.query(RetentionTime.rt).filter(RetentionTime.predicted == "TRUE").all()]
    session_template.close()

    # Rtscan workflow
    with mock.patch('builtins.input', return_value='yes'):  # Mocks user input
        scan_rt(operation='recalc', path_csl=csl_copy_path)

    # Assert that new CSL file was created
    name, ext = os.path.splitext(os.path.basename(csl_copy_path))
    csl_new_path = os.path.join(os.path.dirname(csl_copy_path), f"{name}_minor_edit{ext}")
    assert os.path.isfile(csl_new_path), f"Did not find expected file: {csl_new_path}. Check `update_version_filename`"

    # Connect to CSL database
    session = create_session(path_csl=csl_new_path)

    # Assert that the number of RT-entries have not changed
    assert len(session.query(RetentionTime).all()) == no_rt_entries_template

    # Assert that all predicted RT values have changed
    pred_rt_entries = [rt for (rt,) in session.query(RetentionTime.rt).filter(RetentionTime.predicted == "TRUE").all()]
    assert set(pred_rt_entries).isdisjoint(pred_rt_entries_template)

    # Cleanup
    session.close()
    try:
        os.remove(csl_copy_path)
        os.remove(csl_new_path)
    except PermissionError as e:
        print(f"Could not delete database file: {e}")
