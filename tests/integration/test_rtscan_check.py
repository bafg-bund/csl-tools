from csl.main_functions.rtscan import scan_rt
from csl.utils.sql_utils import create_session, RetentionTime
from csl.config import ROOT_DIR, DEFAULT_PAIRS_INST_CHROM
import os
import shutil
from pathlib import Path
from unittest import mock


def test_rtscan_check():
    """
    Tests correct prediction of retention times (RTs) and correction of incorrect or missing "predicted" flags.

    The CSL file at `csl_template_path` contains intentional mistakes and missing data that should be corrected:
    - Some "predicted" flags are incorrectly set or missing
    - Some RTs are missing and should be predicted by RT models
    """
    # Prepare paths
    csl_template_path = os.path.join(ROOT_DIR,'tests/fixtures/rtscan/CSL_v0_rtscan_incomplete.db')
    csl_copy_path =  os.path.join(ROOT_DIR,'tests/integration/temp/CSL_v0_rtscan_incomplete.db')
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

    # Rtscan update workflow
    with mock.patch('builtins.input', return_value='yes'):  # Mocks user input
        scan_rt(operation='check', path_csl=csl_copy_path)

    # Assert that new CSL file was created
    name, ext = os.path.splitext(os.path.basename(csl_copy_path))
    csl_new_path = os.path.join(os.path.dirname(csl_copy_path), f"{name}_minor_edit{ext}")
    assert os.path.isfile(csl_new_path), f"Did not find expected file: {csl_new_path}. Check `update_version_filename`"

    # Connect to CSL database
    session = create_session(path_csl=csl_new_path)

    # Assert that there is one RT-entry for each method per compound (4 compounds in this database)
    assert len(session.query(RetentionTime).all()) == 4*len(DEFAULT_PAIRS_INST_CHROM), \
        (f"Expected {4*len(DEFAULT_PAIRS_INST_CHROM)} entries, but found {len(session.query(RetentionTime).all())}. "
         f"Check methods in config.py")

    # Assert that for the compound id 1443 the experimental lfuby-RT is now FALSE (was empty)
    assert session.query(RetentionTime.predicted).filter_by(
        compound_id=1443, chrom_method=DEFAULT_PAIRS_INST_CHROM['lfuby']).one_or_none()[0] == 'FALSE'

    # Assert that for the compound id 1672 the experimental uba-RT is now 'FALSE' (was 'TRUE')
    assert session.query(RetentionTime.predicted).filter_by(
        compound_id=1672, chrom_method=DEFAULT_PAIRS_INST_CHROM['uba']).one_or_none()[0] == 'FALSE'

    # Assert that for the compound id 1670 the predicted bfg-RT is now 'TRUE' (was 'FALSE')
    assert session.query(RetentionTime.predicted).filter_by(
        compound_id=1670, chrom_method=DEFAULT_PAIRS_INST_CHROM['bfg']).one_or_none()[0] == 'TRUE'

    # Cleanup
    session.close()
    try:
        os.remove(csl_copy_path)
        os.remove(csl_new_path)
    except PermissionError as e:
        print(f"Could not delete database file: {e}")
