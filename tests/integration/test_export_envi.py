from csl.main_functions.export import export_data
from csl.config import ROOT_DIR, DEFAULT_PAIRS_DSOURCE_CHROM
import os
import shutil
import glob
from pathlib import Path
from unittest.mock import patch


def test_export_envi():
    """
    Tests export of CSL entries as enviMass documents with mixed data (LC and GC).

    The CSL subset CSL_v0_export_envi.db contains experimental data for the following compounds:

    LC-methods
    - 5-Chloro-2-hydroxybenzophenone [M-H]- (bfg)
    - 5-Chloro-2-hydroxybenzophenone [M+H]+ (bfg)
    - 5-Chloro-2-hydroxybenzophenone [M+H]+ (uba)
    - Bezafibrate-d4 [M+H]+ (bfg)
    - Dinoterb [M-H]- (bfg)
    - Fluralaner [M-H]- (uba)
    - Tributylphosphine oxide [M+H]+ (lfuby)
    - Octrizole [M+H]+ (bfg)

    GC-methods
    - Octrizole [M+] (bfg_gc)
    - Methoxychlor [M+] (bfg_gc)

    Envimass export for LC-methods:
    - Only compounds with LC-experiments; Each unique combination of compound, adduct, and ion mode is one entry
    - All export files have the same number of entries because every compound has an RT (experimental or modeled) for each chrom. method (only LC)

    Envimass export for GC-methods:
    - Only compounds with GC-experiments; Each unique combination of compound, adduct, and ion mode is one entry
    - Entries of export files can differ because only experimental RTs are considered (and currently GC-methods have no modeled RTs)

    Assertions:
    1. Correct number of produced files (one for each chrom. method)
    2. Correct filtering of fragments for standard settings
    3. Any export for LC-method contains exactly 6 entries
        + Each type of adduct gets one entry -> 5-Chloro-2-hydroxybenzophenone [M+H]+ entries are merged
        + Bezafibrate-d4 is skipped (standard compound)
    4. Export for GC-method bfg_nts_gc1 contains exactly 2 entries
    5. There is no entry for LC-methods for Methoxychlor (has only experimental data for GC)
    6. There is only one entry for the GC-method bfg_nts_gc1 for compound Octrizole
    """
    # Prepare mock for envimass export configuration (standard settings)
    mock_config = {
        'fragment_cutoff_percent_def': 20,  # Intensity cutoff as a percentage of the maximum intensity (%)
        'ce_def': [0, 60],                  # Collision energy filter range (inclusive)
        'ces_def': [0, 0],                  # Collision energy spread range (inclusive)
        'tolerance_def': 0.015,             # Tolerance for identifying duplicate fragments (Da)
    }

    with patch('csl.export_functions.utils.envi_export_utils.default_sql_query_filter_envi') as MockConfig:
        # Apply mock configuration
        MockConfig.return_value = mock_config

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

        # Load file content for LC-method (using bfg_nts_rp1)
        bfg_file = next(f for f in files if "bfg_nts_rp1" in f.lower())
        with open(bfg_file, 'r') as f:
            content_bfg_lc = f.read()

        # Assert the correct number of entries
        num_entries = len(content_bfg_lc.strip().split('\n')) - 1
        assert num_entries == 6, f"Expected 5 entries in {files[0]}, but found {num_entries}"

        # Assert that entries for compound '5-Chloro-2-hydroxybenzophenone' were correctly merged
        assert content_bfg_lc.count("5-Chloro-2-hydroxybenzophenone") == 2

        # Assert that there is no entry for compound 'Methoxychlor' (only GC-data)
        assert "Methoxychlor" not in content_bfg_lc

        # Assert that fragments were correctly filtered
        expected_mz_values = "\t45.0031, 77.0384, 121.0282, 231.0216\t"
        assert expected_mz_values in content_bfg_lc

        # Load file content for GC-method (using bfg_nts_gc1)
        bfg_gc_file = next(f for f in files if "bfg_nts_gc1" in f.lower())
        with open(bfg_gc_file, 'r') as f:
            content_bfg_gc = f.read()

        # Assert the correct number of entries
        num_entries = len(content_bfg_gc.strip().split('\n')) - 1
        assert num_entries == 2, f"Expected 2 entries in {files[0]}, but found {num_entries}"

        # Assert only GC-data (and not also LC-data) for compound 'Octrizole' was exported
        assert content_bfg_lc.count("Octrizole") == 1

        # Cleanup temp directory
        for f in files:
            os.remove(f)
