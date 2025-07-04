from csl.export_functions.utils.envi_export_config import *
from csl.utils.sql_utils import Experiment, RetentionTime, Compound, Parameter

def sql_query_with_filters_envi(session, chrom_method):
    """
    Queries CSL data based on the filters specified in envi_config and the specified chromatographic method.

    Args:
        session (obj) : SQLAlchemy session object connected to the CSL database.
        chrom_method (str) : Chromatographic method as defined in the CSL. Used to filter retention times.

    Returns:
        query_result (utils.sql_utils.Experiment) : All queried CSL data.
    """
    from sqlalchemy import and_
    from sqlalchemy.orm import selectinload

    # Load default sql query filter configuration
    envi_filter_def = default_sql_query_filter_envi()
    ce_filter = envi_filter_def['ce_def']
    ces_filter = envi_filter_def['ces_def']

    query_result = (
        session.query(Experiment)
        .options(
            selectinload(Experiment.compound),
            selectinload(Experiment.parameter),
            selectinload(Experiment.fragments),
        )
        .join(Compound, Experiment.compound_id == Compound.compound_id)
        .join(Parameter, Experiment.parameter_id == Parameter.parameter_id)
        .join(RetentionTime, RetentionTime.compound_id == Compound.compound_id)
        .filter(
            and_(
                Parameter.CE.between(ce_filter[0], ce_filter[1]),
                Parameter.CES.between(ces_filter[0], ces_filter[1]),
                # Parameter.instrument.in_(instrument_filter),  # Filtering by instrument not needed currently
                RetentionTime.chrom_method == chrom_method,
            )
        )
        .all()
    )
    return query_result


def process_data_entry_envi(csl_data, chrom_method):
    """
    Processes one experiment of the queried CSL data and formats it according to the enviMass target list format.
    Returns None if compound is indicated in envi_config as compound to be skipped.

    Args:
        csl_data (utils.sql_utils.Experiment) : One experiment of the queried CSL data.
        chrom_method (str) : Chromatographic method to filter retention times.

    Returns:
        processed_entry (list or None) : Processed and formatted list of values for one experiment.
    """
    # Default configuration
    envi_filter_def = default_sql_query_filter_envi()
    fragment_cutoff_percent = envi_filter_def['fragment_cutoff_percent_def']

    # Extract an format data to meet enviMass-specific requirements
    compound_name = get_compound_name_envi(csl_data.compound.name)
    if compound_name in skip_compounds_envi():
        return None  # Skip compounds defined in envi_config
    formula = csl_data.compound.formula
    rt = get_rt_by_method_envi(csl_data.compound.retention_times, chrom_method)
    adduct, restrict_adduct = get_adduct_info_envi(csl_data.adduct)
    ion_mode = get_ion_mode_envi(csl_data.parameter.polarity)
    fragments = get_fragments_int_cutoff(csl_data.fragments, fragment_cutoff_percent)
    cas = get_cas_envi(csl_data.compound.CAS)
    smiles = get_smiles_envi(csl_data.compound.SMILES)
    inchi = csl_data.compound.inchi

    # Build row entry in correct order using extracted data and default values for additional rows
    dv = additional_columns_with_def_values_envi()  # Additional columns with default values
    processed_entry = list([compound_name, formula, rt, dv['RTI'], dv['RT_tolerance'], dv['ID_internal_standard'], adduct, ion_mode,
         dv['use_for_recalibration'], dv['use_for_screening'], restrict_adduct, fragments, dv['Remark'], dv['tag1'],
         dv['tag2'], dv['tag3'], dv['from'], dv['to'], dv['warn_1'], dv['warn_2'], dv['Quant_adduct'], dv['Quant_peak'],
         dv['Quant_rule'], dv['homol_units'], cas, inchi, smiles, dv['NIST'] ])

    return processed_entry


def get_compound_name_envi(csl_compound_name):
    """Returns the enviMass-specific format for the compound name based on the CSL-specific format."""
    # Replace occurrences of single quote with "prime" in the 'Name' column
    compound_name =  csl_compound_name.replace("'", "prime")
    return compound_name


def get_rt_by_method_envi(csl_retention_times, chrom_method):
    """Returns the first retention time associated with specified method. Returns None if no match is found."""
    retention_time = next(
        (entry.rt for entry in csl_retention_times if entry.chrom_method == chrom_method),
        None  # If no match is found
    )
    return retention_time


def get_adduct_info_envi(csl_adduct):
    """Returns the enviMass-specific format for the adduct name and additional adduct information."""
    # Format adduct name
    envi_adduct_name_pairs = adduct_name_pairs_envi()
    if csl_adduct in envi_adduct_name_pairs:
        adduct = envi_adduct_name_pairs[csl_adduct]
    else:
        adduct = 'FALSE'

    # Set 'restrict_adduct' to TRUE if adduct is 'M+'
    if adduct == 'M+':
        restrict_adduct = 'TRUE'
    else:
        restrict_adduct = 'FALSE'
    return adduct, restrict_adduct


def get_ion_mode_envi(pol):
    """Returns the enviMass-specific format for polarity information based on the CSL-specific format."""
    if pol == 'pos':
        ion_mode = 'positive'
    elif pol == 'neg':
        ion_mode = 'negative'
    else:
        raise ValueError(f"Unknown polarity format {pol}.")
    return ion_mode


def get_fragments_int_cutoff(csl_fragments, cutoff_percent):
    """
    Filters and returns fragments that have an intensity above a specified cutoff percentage of the maximum intensity.

    Args:
        csl_fragments (utils.sql_utils.Fragment) : List of Fragments with the following attributes:
                                                   - mz (float): The mass-to-charge ratio of the fragment.
                                                   - intensity (float): The intensity of the fragment.
        cutoff_percent (int or float)            : The intensity cutoff as a percentage of the maximum intensity.
                                                   Only fragments with an intensity above this percentage of the maximum
                                                   intensity will be included in the result.

    Returns:
        fragments_cutoff (list[tuple[float, float]]) : List of fragments as tuples (mz, intensity) that meet or exceed
                                                       the intensity cutoff. Returns None if no fragments meet the
                                                       criteria or if the input fragments list is empty.
    """
    if not csl_fragments:
        return None
    max_int = max([frag.int for frag in csl_fragments])
    fragments_cutoff = [(frag.mz, frag.int) for frag in csl_fragments if frag.int / max_int >= cutoff_percent/100]
    return fragments_cutoff


def get_cas_envi(csl_cas):
    """Returns 'FALSE' if the CAS does not exist."""
    if not csl_cas or csl_cas == '' or csl_cas == 'NA':
        cas = 'FALSE'
    else:
        cas = csl_cas
    return cas


def get_smiles_envi(csl_smiles):
    """Returns 'FALSE' if the SMILES-code contains the character '#'."""
    if '#' in csl_smiles:
        smiles = 'FALSE'
    else:
        smiles = csl_smiles
    return smiles

def deduplicate_fragments_envi(frags):
    """
    Removes duplicates of fragments by comparing mz values within a tolerance (specified in envi_export_config).

    Args:
        frags (list[tuple[float, float]]): Fragments (list of tuples with mz and intensity values).

    Returns:
        frag_str_deduped (str) : Formatted fragments (comma-separated mz-values) without duplicates.
    """
    # Load default tolerance
    tol = default_sql_query_filter_envi()['tolerance_def']

    # Sort fragments by ascending mz values
    frags_sorted = sorted(frags, key=lambda x: x[0])

    # Keep unique (within tolerance) fragments and drop the rest
    kept_frags = []
    i = 0
    while i < len(frags_sorted):
        group = [frags_sorted[i]]
        j = i + 1
        # Keep grouping fragments while consecutive mz values are within the tolerance
        while j < len(frags_sorted) and abs(frags_sorted[j][0] - frags_sorted[i][0]) <= tol:
            group.append(frags_sorted[j])
            j += 1
        # Keep the fragment with the highest intensity
        best_int_frag = max(group, key=lambda x: x[1])
        kept_frags.append(best_int_frag)
        i = j

    # Format to comma-separated string
    frag_str_deduped = ', '.join(f"{mz:.4f}" for mz, _ in kept_frags)

    return frag_str_deduped
