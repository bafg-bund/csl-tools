from csl.main_functions.process import process_data
from csl.utils.sql_utils import create_session, Experiment, Compound, Parameter, RetentionTime
from csl.config import ROOT_DIR
import os
import shutil
from pathlib import Path
from unittest import mock


def test_process_gcdata():
    """Tests processing of GC data experiments and import into the CSL."""
    # Prepare paths
    data_path = os.path.join(ROOT_DIR, 'tests/fixtures/import/gcdata_testfiles/gcdata_testdata.txt')
    csl_template_path = os.path.join(ROOT_DIR,'tests/fixtures/import/CSL_v0_import_gcdata.db')
    csl_copy_path =  os.path.join(ROOT_DIR,'tests/integration/temp/CSL_v0_import_gcdata.db')
    config_path = os.path.join(ROOT_DIR, 'tests/fixtures/import/test_config/bfg_gc_config.yaml')
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

    # Process workflow
    with mock.patch('builtins.input', return_value='yes'):  # Mocks user input
        process_data(format='gcdata', path_csl=csl_copy_path, path_data=data_path,
                     path_config=config_path)

    # Connect to CSL database
    session = create_session(path_csl=csl_copy_path)

    # Assert that two experiments were added to the CSL (one duplicate should be skipped)
    assert len(session.query(Experiment).all()) == 4  # 2 previous + 2 added experiments

    # Assert that the correct compound was added to the CSL
    compounds = session.query(Compound.name).all()
    assert any('Trimethyl phosphate' in cp for cp in compounds)

    # Assert that one set of parameter was added
    assert len(session.query(Parameter).all()) == 3  # 2 previous + 1 added set of parameter

    # Assert that one new retention time for gc data was added
    assert len(session.query(RetentionTime).filter(RetentionTime.chrom_method=='bfg_nts_gc1').all()) == 2 # 1 previous + 1 added

    # Cleanup
    session.close()
    try:
        os.remove(csl_copy_path)
    except PermissionError as e:
        print(f"Could not delete database file: {e}")
