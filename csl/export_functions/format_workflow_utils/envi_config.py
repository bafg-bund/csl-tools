# Set configurations for the envi export (enviMass) workflow here

def skip_compounds_envi():
    """These compounds will be skipped and not exported."""
    envi_skip_comp = ['Bezafibrate-d4','Olmesartan-d6','Iopromide-d3']
    return envi_skip_comp


def default_sql_query_filter_envi():
    """
    Provides the default filter configuration for querying the CSL database for the enviMass export workflow.

    Returns:
        envi_default_filter_config (dict) : Dictionary containing default filter configuration.
    """
    envi_default_filter_config = {
        'fragment_cutoff_percent_def': 20,              # Intensity cutoff as a percentage of the maximum intensity (%)
        'ce_def': [35, 40],                             # Collision energy filter range
        'ces_def': 0,                                   # Collision energy spread lower threshold
        'instrument_def':                               # Instrument type filter
            ['LC-ESI-QTOF TripleTOF 5600 SCIEX', 'LC-ESI-QTOF TripleTOF 6600 SCIEX'],
        'chrom_method_def': 'dx.doi.org/10.1016/j.chroma.2015.11.014'  # Chromatographic method filter
    }
    return envi_default_filter_config


def adduct_name_pairs_envi():
    """
    Provides pairs of adduct notations for conversion from CSL format to enviMass target list format.

    Returns:
        envi_adduct_pairs (dict) : Dictionary mapping CSL adduct notations (keys) to enviMass target list notations (values).
    Todo: See issue: nts/collective-spectral-library#30
    """
    envi_adduct_pairs = {
        '[M+H]+': 'M+H',
        '[M]+': 'M+',
        '[M+Na]+': 'FALSE',
        '[M+NH4]+': 'FALSE',
        '[M-H]-': 'M-H',
        '[M+H2CO2-H]-': 'FALSE',
        '[M+HCOO-]-': 'FALSE',
        '[M-H2O+H]-': 'FALSE',
        '[M-H2O+H]+': 'FALSE'
    }
    return envi_adduct_pairs


def additional_columns_with_def_values_envi():
    """
    Provides additional columns and their default values that need to be added to the enviMass target list.

    Returns:
        envi_add_col_def_value (dict) : Dictionary containing column names as keys and their respective default values.
    """
    envi_add_col_def_value = {
        'RTI': 'FALSE',
        'RT_tolerance': 'FALSE',
        'ID_internal_standard': 'FALSE',
        'use_for_recalibration': 'TRUE',
        'use_for_screening': 'TRUE',
        'Remark': 'none',
        'tag1': 'none',
        'tag2': 'none',
        'tag3': 'none',
        'from': 'FALSE',
        'to': 'FALSE',
        'warn_1': 'FALSE',
        'warn_2': 'FALSE',
        'Quant_adduct': 'FALSE',
        'Quant_peak': 1,
        'Quant_rule': 'most intense peak',
        'homol_units': 'FALSE',
        'NIST': 'FALSE'
    }
    return envi_add_col_def_value


def column_names_order_envi():
    """
    Provides a list of column names in the desired order as they should appear in the target list.

    Returns:
        envi_column_names_order (list) : Columns names in the desired order.
    """
    envi_column_names_order = [
        'ID', 'Name', 'Formula', 'RT', 'RTI', 'RT_tolerance', 'ID_internal_standard',
        'main_adduct', 'ion_mode', 'use_for_recalibration', 'use_for_screening',
        'restrict_adduct', 'Fragments', 'Remark', 'tag1', 'tag2', 'tag3', 'from', 'to',
        'warn_1', 'warn_2', 'Quant_adduct', 'Quant_peak', 'Quant_rule', 'homol_units',
        'CAS', 'InChI', 'SMILES', 'NIST'
    ]
    return envi_column_names_order
