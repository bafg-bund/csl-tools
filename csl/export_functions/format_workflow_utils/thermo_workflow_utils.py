def extract_experiment_text_chunk(session, exp_id, chrom_method):
    """
    Extracts and formats the experiment data into a text chunk for export.

    This function queries the database to retrieve relevant experiment data and constructs
    a formatted text string. The output is formatted according to a specific export
    standard.
    Todo: Format couldn't be reproduced 100% and needs to be checked by importing and testing with mzVault.
    Todo: Check:
    Todo: - Splash code second+third block differs sometimes (Probably due to slightly different functions in R and py)
    Todo: - Check point 1 from Marco Scheurers mail (Compound vs Spectra)
    Todo: - Different number of decimals; problem in mzVault?
    Todo: - No comment (and other) lines; problem in mzVault?

    Args:
        session (obj): SQLAlchemy session object connected to the CSL database.
        exp_id (int): Experiment ID used to query the database.
        chrom_method (str): Chromatographic method identifier.

    Returns:
        export_chunk (str): Formatted text chunk for the document.
    """

    from utils.sql_utils import (Experiment, Fragment, RetentionTime, ExperimentGroup, expGroupExp,
                                 CompoundGroup, compGroupComp)

    from sqlalchemy.orm import joinedload
    from datetime import datetime
    from splash import Spectrum, SpectrumType, Splash
    from rdkit import Chem
    from rdkit.Chem import Descriptors

    # Defaults and export format configurations:
    def_mslevel = 'MS2'
    def_centroided = 'TRUE'
    entry_prefix = 'CSL'
    massbank_prefix = 'MSBNK'

    # Get experiment table and preload related tables (compound and parameter)
    experiment = session.query(Experiment).filter_by(experiment_id=exp_id) \
        .options(joinedload(Experiment.compound), joinedload(Experiment.parameter)) \
        .one()
    # Get respective details for the compound and parameter table
    compound = experiment.compound
    parameter = experiment.parameter

    # Get retention time for specified method
    rt_query_res = session.query(RetentionTime).filter_by(compound_id=compound.compound_id,
                                                           chrom_method=chrom_method).first()
    if rt_query_res:
        retention_time = force_mb_nr_format(rt_query_res.rt, 'rt')  # RT in min
    else:
        retention_time = None

    # Get polarity
    polarity = extract_polarity(parameter.polarity)

    # Get precursor charge
    precursor_charge = extract_precursor_charge(experiment.adduct)

    # get collision energy
    collision_energy = int(parameter.CE)

    # Construct title
    title = f"{compound.name}; {parameter.instrument.split()[0]}; MS2; {int(parameter.CE)} {parameter.ce_unit}"

    # Compute exact mass using RDKit
    mol = Chem.MolFromSmiles(compound.SMILES)
    exact_mass = round(Descriptors.ExactMolWt(mol), 4)

    # Get instrument type and name
    instrument_type = parameter.instrument.split()[0]
    instrument_name = " ".join(parameter.instrument.split()[1:])

    # Get fragmentation data
    fragments = session.query(Fragment).filter_by(experiment_id=exp_id).all()
    spectrum = [(frag.mz, frag.int) for frag in fragments]

    # Generate a spectral hash code
    # Wohlgemuth, G, et al., SPLASH, a Hashed Identifier for Mass Spectra. Nature Biotechnology 34, 1099-101 (2016).
    # doi:10.1038/nbt.3689
    spec = Spectrum(spectrum, SpectrumType.MS)
    splash_code = Splash().splash(spec)

    # Get compound_class
    compound_groups = session.query(CompoundGroup.name).join(compGroupComp) \
        .filter(compGroupComp.c.compound_id == compound.compound_id).all()
    compound_class = extract_compound_class(compound_groups)

    # Get contributors
    exp_groups = session.query(ExperimentGroup.name).join(expGroupExp) \
        .filter(expGroupExp.c.experiment_id == exp_id).all()
    exp_groups = [group.name for group in exp_groups]
    if len(exp_groups) > 1:
        raise ValueError(f"length exp_groups > 1. Check following function for experiment ID {exp_id}")

    authors, inst_copyright, contrib_prefix, inst_license = extract_contributors_copyright(exp_groups)
    if not authors:
        raise ValueError(f"Unknown contributor for experiment ID {exp_id}")

    # Get date now
    date_str1 = datetime.now().strftime("%Y.%m.%d")
    date_str2 = datetime.now().strftime("%y%m%d")

    # Construct chunk identifier
    chunk_identifier = f"{massbank_prefix}-{contrib_prefix}-{entry_prefix}{date_str2}{exp_id}"

    # Creating export text chunk
    export_chunk = \
        (f"NAME: {compound.name}\n"
         f"msLevel: {def_mslevel}\n"
         f"RETENTIONTIME: {retention_time}\n"
         f"centroided: {def_centroided}\n"
         f"IONMODE: {polarity}\n"
         f"PRECURSORMZ: {experiment.mz}\n"
         f"precursorCharge: {precursor_charge}\n"
         f"collisionEnergy: {collision_energy}\n"
         f"title: {title}\n"
         f"INCHI: {compound.inchi}\n"
         f"INCHIKEY: {compound.inchikey}\n"
         f"FORMULA: {compound.formula}\n"
         f"PRECURSORTYPE: {experiment.adduct}\n"
         f"EXACTMASS: {exact_mass}\n"
         f"ms_ms_type: {parameter.col_type}\n"
         f"ms_ionization: {parameter.ionisation}\n"
         f"instrument_type: {instrument_type}\n"
         f"INSTRUMENT: {instrument_name}\n"
         f"splash: {splash_code}\n"
         f"authors: {authors}\n"
         f"copyright: {inst_copyright}\n"
         )
    # Add compound class only if a value exists  # Todo: check if ok to leave empty (mzvault)
    if compound_class:
        export_chunk += f"compound_class: {compound_class}\n"

    export_chunk += f"date: {date_str1}\n"

    if not compound.CAS == 'NA':  # Todo: check if ok to leave empty (mzvault)
        export_chunk += f"cas: {compound.CAS}\n"

    export_chunk += \
         (f"license: {inst_license}\n"
         f"pknum: {len(spectrum)}\n"
         f"DB#: {chunk_identifier}\n"
         f"Num Peaks: {len(spectrum)}\n"
         )

    # Add the spectrum data
    for mz, intensity in spectrum:
        # export_chunk += f"{mz} {intensity}\n"
        export_chunk += f"{force_mb_nr_format(mz, 'mz')} {force_mb_nr_format(intensity, 'intensity')}\n"

    return export_chunk


def extract_polarity(pol_form):
    """Returns the polarity information in the required format."""
    if pol_form == 'pos':
        polarity = 'Positive'
    elif pol_form == 'neg':
        polarity = 'Negative'
    else:
        raise ValueError
    return polarity


def extract_precursor_charge(adduct_form):
    """
    Extract the precursor charge number from a formatted adduct name.
    E.g.: [M+H]+ returns 1; [M-2H]2- returns 2.

    Args:
        adduct_form (str) : Formatted adduct name.

    Returns:
        precursor_charge (int) : Precursor charge number.
    """
    import re

    match = re.search(r"(\d)[-+]$", adduct_form)  # Check if string ends with a digit and either `-` or `+`
    if not match:
        precursor_charge = 1
    else:
        precursor_charge = int(match.group(1))
    return precursor_charge


def extract_compound_class(compound_groups):

    compound_groups = [group.name for group in compound_groups]
    compound_groups_filtered = [cg for cg in compound_groups if cg not in ["BfG", "LfU", "UBA"]]

    if compound_groups:
        compound_class_str = "; ".join(compound_groups_filtered)
    else:
        compound_class_str = None
    return compound_class_str


def extract_contributors_copyright(exp_groups):

    if 'BfG' in exp_groups:
        authors = 'Björn Ehlig; Kevin S. Jewell; Arne Wick'
        inst_copyright = 'Copyright 2023 Federal Institute of Hydrology, Koblenz, Germany'
        contrib_prefix = 'BAFG'
        inst_license = 'dl-de/by-2-0'
    elif 'LfU' in exp_groups:
        authors = 'André Macherius; Uwe Kunkel'
        inst_copyright = 'Copyright 2023 Bavarian Environment Agency, Augsburg, Germany'
        contrib_prefix = 'LFUBY'
        inst_license = None  # Todo licence for lfuby?
    elif 'UBA' in exp_groups:
        authors = 'Eric Rosenheinrich; Anja Duffeck'
        inst_copyright = 'Copyright 2023 Federal Environment Agency, Berlin, Germany'
        contrib_prefix = 'UBA'
        inst_license = 'dl-de/by-2-0'
    else:
        authors = None; inst_copyright = None; contrib_prefix = None; inst_license = None
    return authors, inst_copyright, contrib_prefix, inst_license


def force_mb_nr_format(number, col_name):
    """
    Force the massbank number format on a mz, intensity or rt value.
    This is necessary to get exactly the same format as when using the Spectra package (R).
    """
    from decimal import Decimal

    if col_name == 'mz':
        number_form = "{:f}".format(Decimal(str(round(number, 4))).normalize())
    elif col_name == 'intensity':
        number_form = "{:f}".format(Decimal(str(round(number, 1))).normalize())
    elif col_name == 'rt':
        number_form = "{:f}".format(Decimal(str(round(number, 2))).normalize())
    else:
        raise ValueError
    return number_form
