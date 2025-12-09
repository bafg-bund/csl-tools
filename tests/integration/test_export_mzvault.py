from csl.main_functions.export import export_data
from csl.config import ROOT_DIR, DEFAULT_PAIRS_DSOURCE_CHROM
import os
import shutil
import glob
from pathlib import Path


def test_export_mzvault():
    """Tests export of CSL entries as MSP/NIST documents."""
    # Prepare paths
    csl_path = os.path.join(ROOT_DIR,'tests/fixtures/export/CSL_v0_export_mzvault_1bfg_1uba.db')
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
    export_data(format='mzvault', path_csl=csl_path, path_out=out_path)

    # Assert that the correct number of files were produced
    all_methods = DEFAULT_PAIRS_DSOURCE_CHROM
    files = glob.glob(os.path.join(out_path, '*'))  # List all files in the output folder
    assert len(files) == len(all_methods), f"Expected {len(all_methods)} file(s), but found {len(files)}: {files}"

    # Assert that the BfG-method (bfg_nts_rp1) file content is as expected
    bfg_file = next(f for f in files if all_methods['bfg'] in f.lower())
    with open(bfg_file, 'r') as f:
        content = f.read()

    # Assert the correct number of entries
    num_entries = len(content.split('NAME: ')) - 1
    assert num_entries == 2, f"Expected 2 entries in {files[0]}, but found {num_entries}"

    # Assert that there is one experimental and one predicted RT for one chrom. method
    assert content.count("PREDICTED_RT: FALSE") == 1
    assert content.count("PREDICTED_RT: TRUE") == 1
    assert content.count("bfg_nts_rp1") == 2

    # Assert that the LfU-method (lfuby_nts_rp1) file content is as expected (no experimental data)
    lfuby_file = next(f for f in files if all_methods['lfuby'] in f.lower())
    with open(lfuby_file, 'r') as f:
        content = f.read()

    # Assert that both of the entries have predicted RTs
    assert content.count("PREDICTED_RT: TRUE") == 2
    assert content.count("lfuby_nts_rp1") == 2

    # Cleanup temp directory
    for f in files:
        os.remove(f)
