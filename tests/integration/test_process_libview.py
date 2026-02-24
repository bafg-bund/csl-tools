from csl.main_functions.process import process_data
from csl.utils import RetentionTime
from csl.utils.sql_utils import create_session, Experiment, Compound
from csl.config import ROOT_DIR
import os
import shutil
from pathlib import Path
from unittest import mock


def test_process_libview():
    """Tests processing of LibraryView-based experiments and import into the CSL."""
    # Prepare paths
    data_path = os.path.join(ROOT_DIR, 'tests/fixtures/import/libview_testfiles/libview_testdata.sdf')
    extra_path = os.path.join(ROOT_DIR, 'tests/fixtures/import/libview_testfiles/extrafile_testdata.CSV')
    csl_template_path = os.path.join(ROOT_DIR,'tests/fixtures/import/CSL_v0_4entries.db')
    csl_copy_path =  os.path.join(ROOT_DIR,'tests/integration/temp/CSL_v0_4entries.db')
    config_path = os.path.join(ROOT_DIR, 'tests/fixtures/import/test_config/lanuk_config.yaml')
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
        process_data(format='libview', path_csl=csl_copy_path, path_data=data_path,
                     path_config=config_path, path_extra=extra_path)

    # Connect to CSL database
    session = create_session(path_csl=csl_copy_path)

    # Assert that two experiments were added to the CSL
    assert len(session.query(Experiment).all()) == 6  # 4 previous + 2 added experiments

    # Assert that the correct compounds were added/not added to the CSL
    compounds = session.query(Compound.name).all()
    assert any('NewSubstance1' in cp for cp in compounds)
    assert any('NewSubstance2' in cp for cp in compounds)
    assert not any('SynonymSubstance' in cp for cp in compounds)

    # Cleanup
    session.close()
    try:
        os.remove(csl_copy_path)
    except PermissionError as e:
        print(f"Could not delete database file: {e}")


def test_process_replace_predicted_libview():
    """Tests processing of experiments with experimental RT that need to replace existing modeled RT entries."""
    # Prepare paths
    data_path = os.path.join(ROOT_DIR, 'tests/fixtures/import/libview_testfiles/libview_replace_predicted.sdf')
    extra_path = os.path.join(ROOT_DIR, 'tests/fixtures/import/libview_testfiles/extrafile_testdata.CSV')
    csl_template_path = os.path.join(ROOT_DIR,'tests/fixtures/import/CSL_v0_4entries.db')
    csl_copy_path =  os.path.join(ROOT_DIR,'tests/integration/temp/CSL_v0_4entries.db')
    config_path = os.path.join(ROOT_DIR, 'tests/fixtures/import/test_config/lanuk_config.yaml')
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
        process_data(format='libview', path_csl=csl_copy_path, path_data=data_path,
                     path_config=config_path, path_extra=extra_path)

    # Connect to CSL database
    session = create_session(path_csl=csl_copy_path)

    # Assert that two new experiments were added to the CSL
    assert len(session.query(Experiment).all()) == 6  # 4 previous + 2 added experiments

    # Assert that no new compound was added to the CSL
    assert len(session.query(Compound.name).all()) == 4

    # Assert that values for retention time and predicted were updated correctly
    rt_res = session.query(RetentionTime).filter_by(compound_id=848, chrom_method="lanuk_nts_rp1").one_or_none()
    assert rt_res.rt == 19
    assert rt_res.predicted == "FALSE"

    # Cleanup
    session.close()
    try:
        os.remove(csl_copy_path)
    except PermissionError as e:
        print(f"Could not delete database file: {e}")
