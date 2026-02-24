from csl.main_functions.export import export_data
from csl.config import ROOT_DIR, DEFAULT_PAIRS_DSOURCE_CHROM
import os
import shutil
import glob
from pathlib import Path


def test_export_envi():
    """Tests export of CSL entries as enviMass documents."""
    # Prepare paths
    csl_path = os.path.join(ROOT_DIR,'tests/fixtures/export/CSL_v0_export_envi.db')
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
    export_data(format='envi', path_csl=csl_path, path_out=out_path)

    # Assert that the correct number of files were produced
    all_methods = DEFAULT_PAIRS_DSOURCE_CHROM
    files = glob.glob(os.path.join(out_path, '*'))  # List all files in the output folder
    assert len(files) == len(all_methods), f"Expected {len(all_methods)} file(s), but found {len(files)}: {files}"

    # Assert that the file content is as expected (using the BfG-method-file)
    bfg_file = next(f for f in files if all_methods['bfg'] in f.lower())
    with open(bfg_file, 'r') as f:
        content = f.read()

    # Assert the correct number of entries
    num_entries = len(content.strip().split('\n')) - 1
    assert num_entries == 5, f"Expected 5 entries in {files[0]}, but found {num_entries}"

    # Assert that entries for compound '5-Chloro-2-hydroxybenzophenone' were correctly merged
    assert content.count("5-Chloro-2-hydroxybenzophenone") == 2

    # Assert that fragments were correctly filtered
    expected_mz_values = '45.0031, 77.0384, 121.0282, 231.0216'
    assert expected_mz_values in content

    # Cleanup temp directory
    for f in files:
        os.remove(f)
