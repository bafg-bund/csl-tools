from csl.export_functions.utils.envi_export_utils import *
from unittest.mock import patch, MagicMock


def test_get_fragments_int_cutoff():
    """Test return of get_fragments_int_cutoff function with different input conditions."""
    # Create test data for fragments
    mock_fragment_data = [
                MagicMock(mz=100.0, int=30),
                MagicMock(mz=150.0, int=100),
                MagicMock(mz=200.0, int=75)
            ] # (m/z, intensity)

    # Test different cutoff values
    assert get_fragments_int_cutoff(mock_fragment_data, 20) == [(100.0, 30), (150.0, 100), (200.0, 75)]
    assert get_fragments_int_cutoff(mock_fragment_data, 50) == [(150.0, 100), (200.0, 75)]
    assert get_fragments_int_cutoff(mock_fragment_data, 80) == [(150.0, 100)]
    # Test empty fragments list case
    assert get_fragments_int_cutoff([], 20) is None
