import pytest
from unittest.mock import MagicMock, patch
import pandas as pd


@pytest.fixture
def mock_session():
    """Mock the session object."""
    session = MagicMock()
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
    }


@pytest.fixture
def mock_spec_adduct():
    return {
        'adduct_name': 'formatted_adduct'
    }


@pytest.fixture
def mock_extract_data():
    """Mock the extracted data (DataFrame)."""
    data = [{
        "var_comp": 'mock_compound',
        "var_adduct": 'mock_adduct',
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
        "var_compgroup": 'mock_cg1;mock_cg2',
        "var_inchi": 'mock_inchi',
        "file_path": 'mock_file_path',
        "var_chrom_method": 'mock_chrom_method',
        "var_instrument": 'mock_instrument',
        "var_instrument_type": 'mock_instrument_type',
        "var_isotope": 'mock_isotope',
        "var_col_type": 'mock_col_type',
        "var_ce_unit": 'mock_ce_unit',
        "var_accession": 'mock_accession',
    }]
    return pd.DataFrame(data)


@pytest.fixture
def mock_format_data():
    """Mock the formatted data (DataFrame)."""
    data = {
        "dummy_i": ['mock_dummy'],
        "form_err_flag": [False],
        "form_warn_flag": [False]
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_format_data_match():
    """Mock the formatted and matched data (DataFrame)."""
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
        "var_instrument_type": 'mock_instrument_type',
        "var_isotope": 'mock_isotope',
        "var_col_type": 'mock_col_type',
        "var_ce_unit": 'mock_ce_unit',
        "var_accession": 'mock_accession',
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
        "inchi_i": 'mock_inchi',
        "mz_i": 900,
        "rt_i": 22,
        "spec_i": pd.DataFrame({'mz': [9.9, 7.7], 'int': [99.9, 77.7]}),
        "compgroup_i": ['Pesticide','Herbicide'],
        "col_type_i": "mock_col_type",
        "var_expg_csl": 'mock_expg',
        "var_compg_csl": 'mock_compg',
        "instrument_i": 'mock_instrument',
        "experiment_id_i": 'mock_experiment_id',
        "form_err_flag": False,
        "form_warn_flag": False
    }
    return pd.Series(data)


@pytest.fixture
def mock_df_envi():
    """Mock a DataFrame returned by the CSL query used in the envimass export workflow."""
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
        'lanuk': 'method_d'
    }


@pytest.fixture
def mock_inst_notation_pairs():
    """Mock the mapping of institution code to CSL institution notation"""
    return {
        'bfg': 'inst_a',
        'uba': 'inst_b',
        'lfuby': 'inst_c',
        'lanuk': 'inst_d'
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


@pytest.fixture
def mock_formatted_data_mbank():
    """Mock a FormattedData dataclass required for building final text chunks in the MassBank export workflow."""
    mock_f_data = MagicMock()
    mock_f_data.accession = 'MSBNK-BAFG-CSL250109103'
    mock_f_data.title = 'Compound; Instr; MS2; 140 V'
    mock_f_data.date = '2025.01.09'
    mock_f_data.authors = 'Person A; Person B; Person C'
    mock_f_data.inst_license = 'dl-de/by-2-0'
    mock_f_data.inst_copyright = 'Copyright 2025 Institution'
    mock_f_data.comment_chunk = (f"COMMENT: Information\n"
         f"COMMENT: Additional information\n")
    mock_f_data.compound_name = 'Compound'
    mock_f_data.compound_classes = 'Industrial_process; Biocide'
    mock_f_data.formula = '[C10H15N]+'
    mock_f_data.exact_mass = 248.23
    mock_f_data.smiles = 'CC(C)CC'
    mock_f_data.inchi = 'InChI=1S/C17H30N'
    mock_f_data.cas = '469-1-1'
    mock_f_data.inchikey = 'SHF-USA-N'
    mock_f_data.instrument_name = 'TripleTOF 5600 SCIEX'
    mock_f_data.instrument_type = 'LC-ESI-QTOF'
    mock_f_data.def_mslevel = 'MS2'
    mock_f_data.ion_mode = 'POSITIVE'
    mock_f_data.ce = 140
    mock_f_data.frag_mode = 'CID'
    mock_f_data.ionization = 'ESI'
    mock_f_data.chrom_chunk = f"AC$CHROMATOGRAPHY: RETENTION_TIME 12 min\n"
    mock_f_data.precursor_mz = 123.23
    mock_f_data.adduct = '[M]+'
    mock_f_data.splash_code = 'splash10-0i-900-755'
    mock_f_data.data_proc_chunk = f"MS$DATA_PROCESSING: COMMENT Export with pycsl 1.0.0 and CSL 25.0.0\n"
    mock_f_data.nr_peaks = 2
    mock_f_data.spectrum = [
        (100.0, 150.0, 10.0),
        (200.0, 250.0, 20.0),
    ]
    return mock_f_data


@pytest.fixture
def mock_formatted_data_thermo():
    """Mock a FormattedData dataclass required for building final text chunks in the thermo export workflow."""
    mock_f_data = MagicMock()
    mock_f_data.compound_name = 'Compound'
    mock_f_data.accession = 'BAFG-CSL2501225'
    mock_f_data.title = 'Compound; Instr; MS2; 140 V'
    mock_f_data.date = '2025.01.09'
    mock_f_data.authors = 'Person A; Person B; Person C'
    mock_f_data.inst_license = 'dl-de/by-2-0'
    mock_f_data.inst_copyright = 'Copyright 2025 Institution'
    mock_f_data.comment_chunk = (f"COMMENT: Information\n"
         f"COMMENT: Additional information\n")
    mock_f_data.compound_classes = 'Industrial_process; Biocide'
    mock_f_data.formula = 'C10H15N'
    mock_f_data.exact_mass = 248.23
    mock_f_data.def_centroided = 'TRUE'
    mock_f_data.smiles = 'CC(C)CC'
    mock_f_data.inchi = 'InChI=1S/C17H30N'
    mock_f_data.cas = '469-1-1'
    mock_f_data.inchikey = 'SHF-USA-N'
    mock_f_data.instrument_name = 'TripleTOF 5600 SCIEX'
    mock_f_data.instrument_type = 'LC-ESI-QTOF'
    mock_f_data.def_mslevel = 'MS2'
    mock_f_data.ion_mode = 'Positive'
    mock_f_data.ce = 140
    mock_f_data.frag_mode = 'Q'
    mock_f_data.ionization = 'ESI'
    mock_f_data.precursor_mz = 123.23
    mock_f_data.adduct = '[M]+'
    mock_f_data.rt = 12.11
    mock_f_data.precursor_charge = 1
    mock_f_data.splash_code = 'splash10-0i-900-755'
    mock_f_data.nr_peaks = 2
    mock_f_data.spectrum = [
        (100.0, 150.0),
        (200.0, 250.0),
    ]
    return mock_f_data
