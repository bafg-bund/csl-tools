# Set configurations and constant for the envimass export workflow in this file

def default_config_envi():
    """
    Provides the default configuration for the envimass export workflow. The values are used as filters when querying
    the CSL data.

    Returns:
        dict: Dictionary containing default values.
    """
    envi_default_config = {
        'fragment_cutoff_percent_def': 20,  # Intensity cutoff as a percentage of the maximum intensity (%)
        'ce_def': [35, 40],  # Collision energy filter range
        'ces_def': 0,  # Collision energy spread lower threshold
        'instrument_def':
            ['LC-ESI-QTOF TripleTOF 5600 SCIEX', 'LC-ESI-QTOF TripleTOF 6600 SCIEX'],  # Instrument type filter
        'chrom_method_def': 'dx.doi.org/10.1016/j.chroma.2015.11.014'  # Chromatographic method filter
    }
    return envi_default_config


def adduct_name_pairs_envi():
    """
    Provides pairs of adduct notations for conversion from CSL format to EnviMass target list format.

    Returns:
        dict: Dictionary mapping CSL adduct notations (keys) to EnviMass target list notations (values).
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


def column_name_pairs_envi():
    """
    Provides pairs of column names for conversion from CSL format to EnviMass target list format.

    Returns:
        dict: Dictionary mapping CSL column names (keys) to EnviMass target list column names (values).
    """
    envi_column_pairs = {
        'name': 'Name',
        'formula': 'Formula',
        'rt': 'RT',
        'polarity': 'ion_mode',
        'adduct': 'main_adduct',
        'inchi': 'InChI'
    }
    return envi_column_pairs


def polarity_pairs_envi():
    """
    Provides pairs of polarity identifiers for conversion from CSL format to EnviMass target list format.

    Returns:
        dict: Dictionary mapping CSL polarity identifiers (keys) to EnviMass target list identifiers (values).
    """
    envi_polarity_pairs = {
        'pos': 'positive',
        'neg': 'negative',
    }
    return envi_polarity_pairs


def additional_columns_with_def_values_envi():
    """
    Provides additional columns and their default values that need to be added to the EnviMass target list.

    Returns:
        dict: Dictionary containing column names as keys and their respective default values as values.
    """
    envi_add_col_def_value = {
        'ID': 0,
        'RT_tolerance': 'FALSE',
        'ID_internal_standard': 'FALSE',
        'use_for_recalibration': 'TRUE',
        'use_for_screening': 'TRUE',
        'restrict_adduct': 'FALSE',
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
        'NIST': 'FALSE',
        'RTI': 'FALSE'
    }
    return envi_add_col_def_value


def remove_name_rows_envi():
    """Provides a list of substance names to be removed from the EnviMass target list."""
    envi_rm_name_rows = ['Bezafibrate-d4', 'Olmesartan-d6', 'Iopromide-d3']
    return envi_rm_name_rows


def column_order_envi():
    """Provides a list of column names in the desired order as they should appear in the target list."""
    envi_column_order = [
        'ID', 'Name', 'Formula', 'RT', 'RTI', 'RT_tolerance', 'ID_internal_standard',
        'main_adduct', 'ion_mode', 'use_for_recalibration', 'use_for_screening',
        'restrict_adduct', 'Fragments', 'Remark', 'tag1', 'tag2', 'tag3', 'from', 'to',
        'warn_1', 'warn_2', 'Quant_adduct', 'Quant_peak', 'Quant_rule', 'homol_units',
        'CAS', 'InChI', 'SMILES', 'NIST'
    ]
    return envi_column_order
