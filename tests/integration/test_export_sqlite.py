from csl.main_functions.export import export_data
from csl.utils.sql_utils import *
from csl.config import ROOT_DIR
import os
import shutil
import glob
from pathlib import Path


def test_export_sqlite_bfg():
    """Tests export of CSL subset only with BfG experiments."""
    # Prepare paths
    csl_path = os.path.join(ROOT_DIR,'tests/fixtures/export/CSL_v0_export_sqlite_1bfg_1lfuby_1uba.db')
    out_path = os.path.join(ROOT_DIR,'tests/integration/temp')

    # Create out_path folder if necessary
    Path(out_path).mkdir(parents=False, exist_ok=True)

    # Make sure temp directory is clean
    for f in Path(out_path).iterdir():
        try:
            if f.is_file() or f.is_symlink():
                f.unlink()  # Delete file or symlink
            elif f.is_dir():
                shutil.rmtree(f)  # Delete directory and contents
        except PermissionError as e:
            print(f"Could not delete {f}: {e}")

    # Export workflow
    export_data(format='sqlite', path_csl=csl_path, path_out=out_path, subset='bfg')

    # Assert that the file was produced
    files = glob.glob(os.path.join(out_path, '*'))  # List all files in the output folder
    assert len(files) == 1, f"Expected 1 file, but found {len(files)}: {files}"

    # Connect to CSL database
    session = create_session(path_csl=files[0])

    # Assert that only one experiments remained in the CSL
    assert len(session.query(Experiment).all()) == 1  # Previously 3 in total; 1 after subsetting for 'bfg'

    # Assert that experiment, compound and parameter id are all equal to 1
    exp_id = session.query(Experiment.experiment_id).one_or_none()
    comp_id = session.query(Compound.compound_id).one_or_none()
    par_id = session.query(Parameter.parameter_id).one_or_none()
    assert exp_id[0] == 1
    assert comp_id[0] == 1
    assert par_id[0] == 1

    # Assert that the number of fragments is 10
    assert len(session.query(Fragment.fragment_id).all()) == 10

    # Assert that there are 4 entries for retention times
    assert len(session.query(RetentionTime.retention_time_id).all()) == 5

    # Assert that there is just one data source with the id 1 (bfg)
    data_src_id = session.query(Experiment.data_source_id).one_or_none()
    assert data_src_id[0] == 1

    # Assert that there are two compound groups
    assert len(session.query(CompoundGroupMap.c.compound_group_id).all()) == 1

    # Cleanup
    session.close()

    # Cleanup temp directory
    for f in files:
        os.remove(f)
