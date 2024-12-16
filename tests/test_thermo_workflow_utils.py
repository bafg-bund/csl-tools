import pytest

from export_functions.format_workflow_utils.thermo_workflow_utils import *


@pytest.mark.parametrize("adduct_form, expected_precursor_charge",
                         [('[M]+', 1), ('[M-2H]2-', 2), ('[M+C2H7N+H]+', 1)])
def test_extract_precursor_charge(adduct_form, expected_precursor_charge):
    """Test teh function `extract_precursor_charge` with parametrized inputs."""
    precursor_charge = extract_precursor_charge(adduct_form)
    assert precursor_charge == expected_precursor_charge

