import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_session():
    """Mock the session object."""
    session = MagicMock()
    print('test mock session')
    return session


@pytest.fixture
def mock_logger():
    """Mock the logger to capture logging output."""
    with patch('logging.getLogger') as mock_get_logger:
        logger = MagicMock()
        mock_get_logger.return_value = logger
        yield logger


@pytest.fixture
def mock_inst_def():
    """Mock the institution-specific defaults used in process workflows."""
    return {
        'def_pol_p': 'mock_pol_p',
        'def_pol_n': 'mock_pol_n',
        'def_qf': 'mock_qf',
        'def_expg_csl': 'mock_expg',
        'def_compg_csl': 'mock_compg'
    }


@pytest.fixture
def mock_spec_adduct():
    return {
        'adduct_name': 'formatted_adduct'
    }


@pytest.fixture
def mock_extract_data():
    """Mock the extracted data (DataFrame)."""
    import pandas as pd

    data = [{
        "var_comp": 'mock_compound',
        "var_mz": '900',
        "var_ce": '40',
        "var_ionization": 'mock_ionization',
        "var_ion_mode": 'mock_ion_mode',
        "var_rt": '22',
        "var_inchikey": 'mock_inchikey',
        "var_formula": 'mock_formula',
        "var_cas": 'mock_cas',
        "var_smiles": 'mock_smiles',
        "var_peak": ['9.9 99.9', '7.7 77.7'],
        "file_path": 'mock_file_path',
        "var_chrom_method": 'mock_chrom_method',
        "var_instrument": 'mock_instrument',
        "var_isotope": 'mock_isotope',
        "var_col_type": 'mock_col_type',
        "var_ce_unit": 'mock_ce_unit'
    }]
    return pd.DataFrame(data)


@pytest.fixture
def mock_format_data():
    """Mock the formatted data (DataFrame)."""
    import pandas as pd
    data = {
        "dummy_i": ['mock_dummy'],
        "form_err_flag": [False],
        "form_warn_flag": [False]
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_format_data_match():
    """Mock the formatted and matched data (DataFrame)."""
    import pandas as pd
    data = {
        'dummy_i': ['mock_dummy'],
        'form_err_flag': [False],
        'form_warn_flag': [False],
        'csl_dupl_flag': [False],
        'csl_err_flag': [False],
        'csl_add_flag': [True]
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_entry_df():
    """Mock the data entry (that includes the formatted data) used in process workflows."""
    import pandas as pd

    data = {
        "var_comp": 'mock_compound',
        "var_mz": '900',
        "var_ce": '40',
        "var_ionization": 'mock_ionization',
        "var_ion_mode": 'mock_ion_mode',
        "var_rt": '22',
        "var_inchikey": 'mock_inchikey',
        "var_formula": 'mock_formula',
        "var_cas": 'mock_cas',
        "var_smiles": 'mock_smiles',
        "var_peak": ['9.9 99.9', '7.7 77.7'],
        "file_path": 'mock_file_path',
        "var_chrom_method": 'mock_chrom_method',
        "var_instrument": 'mock_instrument',
        "var_isotope": 'mock_isotope',
        "var_col_type": 'mock_col_type',
        "var_ce_unit": 'mock_ce_unit',
        "pol_i": 'mock_form_pol',
        "comp_i": 'mock_pol_comp',
        "adduct_i": 'mock_pol_adduct',
        "ce_i": 40,
        "ces_i": 0,
        "ionization_i": 'mock_pol_ionization',
        "formula_i": 'mock_pol_formula',
        "inchikey_i": 'mock_pol_inchikey',
        "inchikey_main_i": 'mock_pol_inchikey_main',
        "cas_i": 'mock_pol_cas',
        "smiles_i": 'mock_pol_smiles',
        "mz_i": 900,
        "rt_i": 22,
        "spec_i": pd.DataFrame({'mz': [9.9, 7.7], 'int': [99.9, 77.7]}),
        "form_err_flag": False,
        "form_warn_flag": False
    }
    return pd.Series(data)


@pytest.fixture
def mock_df_envi():
    """Mock a DataFrame returned by the CSL query used in the envimass export workflow."""
    import pandas as pd

    return pd.DataFrame({
        'name': ['compound1', 'compound2'],
        'formula': ['H2O', 'CO2'],
        'rt': [1.23, 2.34],
        'adduct': ['M+', 'M-H'],
        'polarity': ['positive', 'negative'],
        'experiment_id': [1, 2],
        'CAS': ['123-45-6', '789-01-2'],
        'inchi': ['InChI=1S/H2O/h1H2', 'InChI=1S/CO2/c2-1-3'],
        'SMILES': ['O', 'O=C=O']
    })


@pytest.fixture
def mock_inst_method_pairs():
    """Mock the mapping of institutions to chromatographic methods"""
    return {
        'bfg': 'method_a',
        'uba': 'method_b',
        'lfuby': 'method_c',
        'lanuv': 'method_d'
    }


@pytest.fixture
def mock_inst_notation_pairs():
    """Mock the mapping of institution code to CSL institution notation"""
    return {
        'bfg': 'inst_a',
        'uba': 'inst_b',
        'lfuby': 'inst_c',
        'lanuv': 'inst_d'
    }


@pytest.fixture
def mock_models_to_bfg():
    """Mock the models for predicting BfG RTs from other RTs."""
    return {
        'inst_b': MagicMock(return_value=22.5),
        'inst_c': MagicMock(return_value=7.0)
    }


@pytest.fixture
def mock_models_from_bfg():
    """Mock the models for predicting RTs from BfG RTs."""
    return {
        'inst_b': MagicMock(return_value=12.5),
        'inst_c': MagicMock(return_value=15.0)
    }
