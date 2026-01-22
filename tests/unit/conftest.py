import pytest
from unittest.mock import MagicMock, patch
import pandas as pd


@pytest.fixture
def mock_session():
    """Mocks the session object."""
    session = MagicMock()
    return session


@pytest.fixture
def mock_logger():
    """Mocks the logger to capture logging output."""
    with patch('logging.getLogger') as mock_get_logger:
        logger = MagicMock()
        mock_get_logger.return_value = logger
        yield logger


@pytest.fixture
def mock_dsrc_def():
    """Mocks the data-source-specific defaults used in process workflows."""
    return {
        'def_pol_p': 'mock_pol_p',
        'def_pol_n': 'mock_pol_n',
        'def_qf': 'mock_qf',
    }


@pytest.fixture
def mock_spec_adduct():
    """Mocks special adduct notation used in process workflows."""
    return {
        'adduct_name': 'formatted_adduct'
    }


@pytest.fixture
def mock_extract_data():
    """Mocks the extracted data (DataFrame) used in process workflows."""
    data = [{
        "par_comp": 'mock_compound',
        "par_adduct": 'mock_adduct',
        "par_mz": '900',
        "par_ce": '40',
        "par_ionization": 'mock_ionization',
        "par_ion_mode": 'mock_ion_mode',
        "par_rt": '22',
        "par_inchikey": 'mock_inchikey',
        "par_formula": 'mock_formula',
        "par_cas": 'mock_cas',
        "par_smiles": 'mock_smiles',
        "par_peak": ['9.9 99.9', '7.7 77.7'],
        "par_compgroup": 'mock_cg1;mock_cg2',
        "par_inchi": 'mock_inchi',
        "file_path": 'mock_file_path',
        "par_chrom_method": 'mock_chrom_method',
        "par_instrument": 'mock_instrument',
        "par_instrument_type": 'mock_instrument_type',
        "par_isotope": 'mock_isotope',
        "par_col_type": 'mock_col_type',
        "par_ce_unit": 'mock_ce_unit',
        "par_accession": 'mock_accession',
        "par_ces": 'mock_ces',
        "par_exact_mass": 'mock_exact_mass'
    }]
    return pd.DataFrame(data)


@pytest.fixture
def mock_format_data():
    """Mocks the formatted data (DataFrame) used in process workflows."""
    data = {
        "dummy_i": ['mock_dummy'],
        "form_err_flag": [False],
        "form_warn_flag": [False]
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_entry_df():
    """Mocks the data entry (that includes the formatted data) used in csl queries in process workflows."""
    data = {
        "par_comp": 'mock_compound',
        "par_mz": '900',
        "par_ce": '40',
        "par_ionization": 'mock_ionization',
        "par_ion_mode": 'mock_ion_mode',
        "par_rt": '22',
        "par_inchikey": 'mock_inchikey',
        "par_formula": 'mock_formula',
        "par_cas": 'mock_cas',
        "par_smiles": 'mock_smiles',
        "par_peak": ['9.9 99.9', '7.7 77.7'],
        "file_path": 'mock_file_path',
        "par_chrom_method": 'mock_chrom_method',
        "par_instrument": 'mock_instrument',
        "par_instrument_type": 'mock_instrument_type',
        "par_isotope": 'mock_isotope',
        "par_col_type": 'mock_col_type',
        "par_ce_unit": 'mock_ce_unit',
        "par_accession": 'mock_accession',
        "par_authors": 'mock_authors',
        "par_affiliation": 'mock_affiliation',
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
        "par_data_source": 'mock_dsrc',
        "instrument_i": 'mock_instrument',
        "experiment_id_i": 'mock_experiment_id',
        "form_err_flag": False,
        "form_warn_flag": False
    }
    return pd.Series(data)


@pytest.fixture
def mock_dsrc_method_pairs():
    """Mocks the mapping of data sources to chromatographic methods."""
    return {
        'dsrc_a': 'method_a',
        'dsrc_b': 'method_b',
        'dsrc_c': 'method_c',
        'dsrc_d': 'method_d'
    }


@pytest.fixture
def mock_models_to_bfg():
    """Mocks the models for predicting BfG RTs from other RTs."""
    return {
        'dsrc_b': MagicMock(return_value=22.5),
        'dsrc_c': MagicMock(return_value=7.0)
    }


@pytest.fixture
def mock_models_from_bfg():
    """Mocks the models for predicting RTs from BfG RTs."""
    return {
        'dsrc_b': MagicMock(return_value=12.5),
        'dsrc_c': MagicMock(return_value=15.0)
    }


@pytest.fixture
def mock_formatted_data_mbank():
    """Mocks a FormattedData dataclass required for building final text chunks in the MassBank export workflow."""
    mock_f_data = MagicMock()
    mock_f_data.accession = 'MSBNK-BAFG-CSL250109103'
    mock_f_data.title = 'Compound; Instr; MS2; 140 V'
    mock_f_data.date = '2025.01.09'
    mock_f_data.authors = 'Person A; Person B; Person C'
    mock_f_data.dsrc_license = 'CC BY 4.0'
    mock_f_data.dsrc_copyright = 'Copyright 2025 Data source'
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
    mock_f_data.data_proc_chunk = f"MS$DATA_PROCESSING: COMMENT Export with csl-tools 1.0.0 and CSL 25.0.0\n"
    mock_f_data.nr_peaks = 2
    mock_f_data.spectrum = [
        (100.0, 150.0, 10.0),
        (200.0, 250.0, 20.0),
    ]
    return mock_f_data


@pytest.fixture
def mock_formatted_data_mzvault():
    """Mocks a FormattedData dataclass required for building final text chunks in the mzvault export workflow."""
    mock_f_data = MagicMock()
    mock_f_data.compound_name = 'Compound'
    mock_f_data.accession = 'BAFG-CSL2501225'
    mock_f_data.title = 'Compound; Instr; MS2; 140 V'
    mock_f_data.date = '2025.01.09'
    mock_f_data.authors = 'Person A; Person B; Person C'
    mock_f_data.dsrc_license = 'dl-de/by-2-0'
    mock_f_data.dsrc_copyright = 'Copyright 2025 Data source'
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
    mock_f_data.pred = 'FALSE'
    mock_f_data.precursor_charge = 1
    mock_f_data.splash_code = 'splash10-0i-900-755'
    mock_f_data.nr_peaks = 2
    mock_f_data.spectrum = [
        (100.0, 150.0),
        (200.0, 250.0),
    ]
    return mock_f_data
