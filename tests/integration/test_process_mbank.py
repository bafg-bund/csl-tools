from csl.main_functions.process import process_data
from csl.utils.sql_utils import create_session, Experiment, Compound
from csl.config import ROOT_DIR
import os
import shutil
from pathlib import Path
from unittest import mock


def test_process_mbank():
    """Tests processing of MassBank documents and import into the CSL."""
    # Prepare paths
    data_path = os.path.join(ROOT_DIR, 'tests/fixtures/import/mbank_testfiles')
    csl_template_path = os.path.join(ROOT_DIR,'tests/fixtures/import/CSL_v0_4entries.db')
    csl_copy_path =  os.path.join(ROOT_DIR,'tests/integration/temp/CSL_v0_4entries.db')
    config_path = os.path.join(ROOT_DIR, 'tests/fixtures/import/test_config/bfg_config.yaml')
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

    # Process mbank workflow
    with mock.patch('builtins.input', side_effect=['1','yes']):  # Mocks user input
        process_data(format='mbank', path_csl=csl_copy_path, path_data=data_path,
                     path_config=config_path, path_extra=None)

    # Connect to CSL database
    session = create_session(path_csl=csl_copy_path)

    # Assert that one experiments was added to the CSL
    assert len(session.query(Experiment).all()) == 5  # 4 previous + 1 added experiment

    # Assert that the correct compound was added to the CSL
    compounds = session.query(Compound.name).all()
    assert any('Butocarboxim' in cp for cp in compounds)

    # Cleanup
    session.close()
    try:
        os.remove(csl_copy_path)
    except PermissionError as e:
        print(f"Could not delete database file: {e}")
