from dataclasses import dataclass
from utils.sql_utils import (inst_code_csl_mapping, Experiment, Compound, Parameter, Fragment, expGroupExp,
                             ExperimentGroup, CompoundGroup, RetentionTime)
from splash import Spectrum, SpectrumType, Splash

@dataclass
class SqlQueryResult:
    experiment: Experiment
    compound: Compound
    parameter: Parameter
    fragments: Fragment
    exp_groups: expGroupExp
    compound_groups: CompoundGroup
    retention_time: RetentionTime


def get_experiment_ids_by_exp_group(session, data_source):
    """
    Get experiment IDs from the CSL. Can be subset by data source.

    Args:
        session (obj)     : SQLAlchemy session object connected to the CSL database.
        data_source (str) : Corresponds to ExperimentGroup in CSL (e.g., 'bfg'), or 'all' for all experiment IDs.

    Returns:
        experiment_ids (list of int) :  Experiment IDs of the data entries (experiments) in the CSL.
    """
    from sqlalchemy import select

    if data_source == 'all':
        # Get all experiment IDs
        experiment_ids = session.query(Experiment.experiment_id).all()
        experiment_ids = [exp_id[0] for exp_id in experiment_ids]  # Convert to a flat list
    else:
        # Get experiment IDs based on subset (query at specific ExperimentGroup name)
        inst_notation_pairs = inst_code_csl_mapping()
        stmt = (
            select(Experiment.experiment_id)
            .join(expGroupExp, Experiment.experiment_id == expGroupExp.c.experiment_id)
            .join(ExperimentGroup, expGroupExp.c.experimentGroup_id == ExperimentGroup.experimentGroup_id)
            .where(ExperimentGroup.name == inst_notation_pairs[data_source])
        )
        # Execute the query
        experiment_ids = session.execute(stmt).scalars().all()
    return experiment_ids


def sql_queries_by_exp_id_chrom_method(session, exp_id, chrom_method):
    """
    Queries the CSL database for experiment data and related metadata based on the experiment ID and method.

    Args:
        session (obj)       : SQLAlchemy session object connected to the CSL database.
        exp_id (int)        : Experiment ID used to query the database.
        chrom_method (str)  : Chromatographic method identifier.

    Returns:
        SqlQueryResult (dataclass) : Dataclass containing the queried experiment data and metadata.
    """
    from utils.sql_utils import Experiment, RetentionTime, ExperimentGroup, expGroupExp, CompoundGroup, compGroupComp
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


def get_precursor_charge(adduct_form):
    """
    Extract the precursor charge number from a formatted adduct name.
    E.g.: [M+H]+ returns 1; [M-2H]2- returns 2.
    """
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
    inst_notation_pairs = inst_code_csl_mapping()

    compound_groups = [group.name for group in compound_groups]
    compound_groups_filtered = [cg for cg in compound_groups if cg not in inst_notation_pairs.values()]

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
    inst_notation_pairs = inst_code_csl_mapping()

    current_year = datetime.now().strftime('%Y')
    if inst_notation_pairs['bfg'] == exp_group or 'bfg' == exp_group:
        authors = 'Ole Lessmann; Kevin S. Jewell; Björn Ehlig; Arne Wick'
        inst_copyright = f'Copyright {current_year} Federal Institute of Hydrology, Koblenz, Germany'
        contrib_prefix = 'BAFG'  # Todo: change?
        inst_license = 'dl-de/by-2-0'
    elif inst_notation_pairs['lfuby'] == exp_group or 'lfuby' == exp_group:
        authors = 'André Macherius; Uwe Kunkel'
        inst_copyright = f'Copyright {current_year} Bavarian Environment Agency, Augsburg, Germany'
        contrib_prefix = 'LFUBY'
        inst_license = None  # Todo licence for lfuby?
    elif inst_notation_pairs['uba'] == exp_group or 'uba' == exp_group:
        authors = 'Eric Rosenheinrich; Anja Duffeck'
        inst_copyright = f'Copyright {current_year} Federal Environment Agency, Berlin, Germany'
        contrib_prefix = 'UBA'
        inst_license = 'dl-de/by-2-0'
    else:
        authors = None; inst_copyright = None; contrib_prefix = None; inst_license = None
    return authors, inst_copyright, contrib_prefix, inst_license
