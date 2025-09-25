from csl.config import DEFAULT_PAIRS_INST_CHROM
from csl.utils.sql_utils import (Experiment, Compound, Parameter, Fragment, expGroupExp,
                             ExperimentGroup, CompoundGroup, RetentionTime, compGroupComp)

from dataclasses import dataclass
from splash import Spectrum, SpectrumType, Splash

@dataclass
class SqlQueryResult:
    experiment: Experiment
    compound: Compound
    parameter: Parameter
    fragments: list[Fragment]
    exp_groups: list[str]
    compound_groups: list[str]
    retention_time: RetentionTime | None


def get_chrom_methods(data_source):
    """Get chromatographic methods by data source(s)."""
    all_methods = DEFAULT_PAIRS_INST_CHROM
    if 'all' in data_source:
        chrom_methods = list(all_methods.values())
    else:
        # Normalize to list
        if isinstance(data_source, str):
            data_source = [data_source]
        chrom_methods = [all_methods[k] for k in data_source]
    return chrom_methods


def get_experiment_ids_by_exp_group(session, data_source):
    """
    Get experiment IDs from the CSL. Can be subset by data source.

    Args:
        session (obj)                  : SQLAlchemy session object connected to the CSL database.
        data_source (str or list[str]) : One or more data sources (e.g., ['bfg', 'uba'] or 'all').
                                         Corresponds to ExperimentGroup in CSL.

    Returns:
        experiment_ids (list of int) : Experiment IDs of the data entries (experiments) in the CSL.
    """
    from sqlalchemy import select

    if 'all' in data_source:
        # Get all experiment IDs
        experiment_ids = session.query(Experiment.experiment_id).all()
        experiment_ids = [exp_id[0] for exp_id in experiment_ids]  # Convert to a flat list
    else:
        # Normalize to list
        if isinstance(data_source, str):
            data_source = [data_source]

        # Get experiment IDs based on subset (query at specific ExperimentGroup name)
        stmt = (
            select(Experiment.experiment_id)
            .join(expGroupExp, Experiment.experiment_id == expGroupExp.c.experiment_id)
            .join(ExperimentGroup, expGroupExp.c.experimentGroup_id == ExperimentGroup.experimentGroup_id)
            .where(ExperimentGroup.name.in_(data_source))
        )

        # Execute the query
        experiment_ids = session.execute(stmt).scalars().all()
    return experiment_ids


def get_experiment_ids_by_chrom_method(session, chrom_method, predicted=None):
    """
    Get experiment IDs from the CSL subset by chromatographic method and predicted value.

    Args:
        session (obj)             : SQLAlchemy session object connected to the CSL database.
        chrom_method (str)        : Chromatographic method (e.g., 'uba_nts_rp1').
                                    Corresponds to chrom_method in retentionTime table in CSL.
        predicted (str|bool|None) : Filter for predicted column in retentionTime table in CSL.
                                    Use "TRUE"/True, "FALSE"/False, or None (default) to not filter on prediction.

    Returns:
        experiment_ids (list of int) : Experiment IDs of the data entries (experiments) in the CSL.
    """
    from sqlalchemy import select

    stmt = (
        select(Experiment.experiment_id)
        .join(Experiment.compound)
        .join(Compound.retention_times)
        .where(RetentionTime.chrom_method == chrom_method)
    )

    # Add prediction filter if specified
    if isinstance(predicted, bool):
        predicted = {True: "TRUE", False: "FALSE"}[predicted]
    elif isinstance(predicted, str):
        predicted = predicted.upper()
        if predicted not in ("TRUE", "FALSE"):
            raise ValueError(f"Invalid predicted value '{predicted}'. Must be True, False, 'TRUE', 'FALSE', or None.")
    if predicted in ("TRUE", "FALSE"):
        stmt = stmt.where(RetentionTime.predicted == predicted)

    # Execute the query
    experiment_ids = session.execute(stmt).scalars().all()
    return experiment_ids


def sql_queries_by_exp_id_chrom_method(session, exp_id, chrom_method):
    """
    Queries the CSL database for experiment data and related metadata based on the experiment ID and method.

    Args:
        session (obj)      : SQLAlchemy session object connected to the CSL database.
        exp_id (int)       : Experiment ID used to query the database.
        chrom_method (str) : Chromatographic method identifier.

    Returns:
        SqlQueryResult (dataclass) : Dataclass containing the queried experiment data and metadata.
    """
    from sqlalchemy.orm import joinedload

    # Get experiment table and preload related tables
    experiment = session.query(Experiment).filter_by(experiment_id=exp_id) \
        .options(joinedload(Experiment.compound),
                 joinedload(Experiment.parameter),
                 joinedload(Experiment.fragments)) \
        .one()
    compound = experiment.compound
    parameter = experiment.parameter
    fragments = experiment.fragments

    # Get experiment groups
    exp_groups = session.query(ExperimentGroup.name).join(expGroupExp) \
        .filter(expGroupExp.c.experiment_id == exp_id).all()

    # Get compound groups
    compound_groups = session.query(CompoundGroup.name).join(compGroupComp) \
        .filter(compGroupComp.c.compound_id == compound.compound_id).all()

    # Get retention times
    retention_time = session.query(RetentionTime).filter_by(compound_id=compound.compound_id,
                                                            chrom_method=chrom_method).first()

    return SqlQueryResult(experiment, compound, parameter, fragments, exp_groups, compound_groups, retention_time)


def sql_bulk_queries_by_exp_ids_chrom_method(session, exp_ids, chrom_method):
    """
    Queries the CSL for experiment data and related metadata based on all experiment IDs for a chromatographic method.

    Args:
        session (obj)       : SQLAlchemy session object connected to the CSL database.
        exp_ids (list[int]) : List of experiment IDs.
        chrom_method (str)  : Chromatographic method identifier.

    Returns:
        sql_data_dict (dict[int, SqlQueryResult(dataclass)]) : Mapping of exp_id to SqlQueryResult
    """
    from collections import defaultdict
    from sqlalchemy.orm import joinedload

    # Get all experiments with compound/parameter/fragments
    experiments = session.query(Experiment).filter(
        Experiment.experiment_id.in_(exp_ids)
    ).options(
        joinedload(Experiment.compound),
        joinedload(Experiment.parameter),
        joinedload(Experiment.fragments)
    ).all()

    # Get experiment groups
    exp_group_map = defaultdict(list)
    rows = (
        session.query(expGroupExp.c.experiment_id, ExperimentGroup.name)
        .join(ExperimentGroup)
        .filter(expGroupExp.c.experiment_id.in_(exp_ids))
        .all()
    )
    for eid, group_name in rows:
        exp_group_map[eid].append(group_name)

    # Get compound IDs
    compound_ids = [exp.compound.compound_id for exp in experiments]

    # Get compound groups
    compound_group_map = defaultdict(list)
    rows = (
        session.query(compGroupComp.c.compound_id, CompoundGroup.name)
        .join(CompoundGroup)
        .filter(compGroupComp.c.compound_id.in_(compound_ids))
        .all()
    )
    for cid, group_name in rows:
        compound_group_map[cid].append(group_name)

    # Get retention times
    retention_time_map = {}
    rows = (
        session.query(RetentionTime)
        .filter(
            RetentionTime.compound_id.in_(compound_ids),
            RetentionTime.chrom_method == chrom_method
        ).all()
    )
    for rt in rows:
        retention_time_map[rt.compound_id] = rt

    # Assemble dictionary
    sql_data_dict = {}
    for exp in experiments:
        compound = exp.compound
        cid = compound.compound_id
        # Mapping experiment ID to sql data
        sql_data_dict[exp.experiment_id] = SqlQueryResult(
            experiment=exp,
            compound=compound,
            parameter=exp.parameter,
            fragments=exp.fragments,
            exp_groups=exp_group_map.get(exp.experiment_id, []),
            compound_groups=compound_group_map.get(cid, []),
            retention_time=retention_time_map.get(cid)
        )

    return sql_data_dict


def get_precursor_charge(adduct_form):
    """Extract the precursor charge number from a formatted adduct name, e.g., [M+H]+ returns 1; [M-2H]2- returns 2."""
    import re

    # Check if string ends with a digit and either `-` or `+`
    match = re.search(r"(\d)[-+]$", adduct_form)
    if not match:
        precursor_charge = 1
    else:
        precursor_charge = int(match.group(1))
    return precursor_charge


def get_spectrum(fragments):
    """Extracts m/z and intensity values from fragments and sorts them by ascending m/z values."""
    # Extract m/z and intensity values from fragments
    spectrum = [(frag.mz, frag.int) for frag in fragments]

    # Sort by ascending m/z values
    spectrum = sorted(spectrum, key=lambda x: x[0])
    return spectrum


def get_splash_code(spectrum):
    """
    Generate a spectral hash code using Spectrum:
    Wohlgemuth, G, et al., SPLASH, a Hashed Identifier for Mass Spectra. Nature Biotechnology 34, 1099-101 (2016).
    doi:10.1038/nbt.3689

    Intensity values are multiplied by 1000 before spectral hash code generation to avoid splash code issues.
    """
    # Multiply intensities by 1000 to avoid splash code issues
    temp_spectrum = []
    for entry in spectrum:
        temp_spectrum.append((entry[0], entry[1] * 1000))

    # Generate a spectral hash code
    spec = Spectrum(temp_spectrum, SpectrumType.MS)
    splash_code = Splash().splash(spec)
    return splash_code


def get_compound_classes(compound_groups):
    """Extracts the non-institute compound classes from a list of compound groups."""
    if not isinstance(compound_groups[0], str):
        compound_groups = [group.name for group in compound_groups]  # normalize to list of str

    compound_groups_filtered = [cg for cg in compound_groups if cg not in DEFAULT_PAIRS_INST_CHROM.keys()]

    if compound_groups_filtered:
        compound_classes = "; ".join(compound_groups_filtered)
    else:
        compound_classes = None
    return compound_classes


def get_contributors_copyright(exp_group):
    """
    Returns legal information based on experiment group.

    Args:
        exp_group (str) : Experiment group.

    Returns:
        authors (str) : Contributors.
        inst_copyright (str) : Copyright statement.
        contrib_prefix (str) : Contributor prefix in MassBank format.
        inst_license (str) : Type of licence for the institute's data.
    """
    from datetime import datetime

    current_year = datetime.now().strftime('%Y')
    if 'bfg' == exp_group:
        authors = 'Ole Lessmann; Kevin S. Jewell; Björn Ehlig; Arne Wick'
        inst_copyright = f'Copyright {current_year} Federal Institute of Hydrology, Koblenz, Germany'
        contrib_prefix = 'BAFG'
        inst_license = 'CC BY 4.0'
    elif 'lfuby' == exp_group:
        authors = 'André Macherius; Uwe Kunkel'
        inst_copyright = f'Copyright {current_year} Bavarian Environment Agency, Augsburg, Germany'
        contrib_prefix = 'LFUBY'
        inst_license = 'CC BY 4.0'
    elif 'uba' == exp_group:
        authors = 'Eric Winter'
        inst_copyright = f'Copyright {current_year} German Environment Agency, Berlin, Germany'
        contrib_prefix = 'UBA'
        inst_license = 'CC BY 4.0'
    else:
        authors = None; inst_copyright = None; contrib_prefix = None; inst_license = None
    return authors, inst_copyright, contrib_prefix, inst_license
