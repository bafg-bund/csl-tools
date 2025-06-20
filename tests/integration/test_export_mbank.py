from csl.main_functions.export import run_export_workflow
from csl.config import ROOT_DIR
import os
import re
import shutil
import glob
from datetime import datetime
from pathlib import Path


def test_export_mbank_bfg():
    """Tests correct export of BfG experiments as MassBank documents."""
    # Prepare paths
    csl_path = os.path.join(ROOT_DIR,'tests/integration/fixtures/CSL_v0_export_1bfg_1bfgIS_1lfuby_1uba.db')
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

    # Export mbank workflow
    run_export_workflow(format='mbank', path_out=out_path, path_csl=csl_path, subset='bfg')

    # Assert that only one file was produced (CSL subset contains only one bfg experiment, that is not an internal standard)
    files = glob.glob(os.path.join(out_path, '*'))  # List all files in the output folder
    assert len(files) == 1, f"Expected 1 file, but found {len(files)}: {files}"

    # Assert that file content is as expected
    with open(files[0], 'r') as f:
        content = f.read()
    # Check all mandatory tags (https://github.com/MassBank/MassBank-web/blob/main/Documentation/MassBankRecordFormat.md#table-1--massbank-record-format-summary)
    mandatory_tags = ["ACCESSION", "RECORD_TITLE", "DATE", "AUTHORS", "LICENSE", "CH$NAME", "CH$COMPOUND_CLASS",
                      "CH$FORMULA", "CH$EXACT_MASS", "CH$SMILES", "CH$IUPAC", "AC$INSTRUMENT", "AC$INSTRUMENT_TYPE",
                      "AC$MASS_SPECTROMETRY: MS_TYPE", "AC$MASS_SPECTROMETRY: ION_MODE", "PK$SPLASH", "PK$NUM_PEAK",
                      "PK$PEAK"]
    for tag in mandatory_tags:
        assert tag in content, f"Mandatory tag '{tag}' not in file content"
    # Check that current date is in content
    match_date = re.search(r'\bDATE: (\d{4}\.\d{2}\.\d{2})', content)
    assert match_date.group(1) == datetime.now().strftime('%Y.%m.%d'), "Date string does not match"

    # Cleanup temp directory
    for f in files:
        os.remove(f)
