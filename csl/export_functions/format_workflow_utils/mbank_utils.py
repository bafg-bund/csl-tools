from .mbank_config import *
from utils.sql_utils import inst_code_csl_mapping
from utils.sql_utils import Experiment, Compound, Parameter, Fragment, expGroupExp, CompoundGroup, RetentionTime
from config import DEFAULT_PAIRS_INST_CHROM
from dataclasses import dataclass
from typing import Optional, Union, List

def extract_experiment_chunk(session, exp_id, chrom_method, csl_version, pycsl_version):
    """
    Extracts data for a specific experiment id and formats data to meet MassBank requirements.

    Args:
        session (obj)       : SQLAlchemy session object connected to the CSL database.
        exp_id (int)        : Experiment ID used to query the database.
        chrom_method (str)  : Chromatographic method identifier.
        csl_version (str)   : Current version of the CSL database.
        pycsl_version (str) : Current version of the python package.

    Returns:
        export_chunk (str) : Text chunk formatted to fit MassBank requirements for a single txt file.
    """

    # SQL queries based on experiment ID and chromatographic method
    SqlQueryResult = sql_queries_export(session, exp_id, chrom_method)

    # Skip internal standards
    skip_comp = skip_compounds_mbank()
    if SqlQueryResult.compound.name in skip_comp:
        return None

    # Format data to meet MassBank format requirements
    FormattedData = extract_and_format_mbank_data(exp_id, chrom_method, SqlQueryResult)

    # Assemble text chunk for the MassBank document
    export_chunk = build_export_chunk(FormattedData, csl_version, pycsl_version)

    return export_chunk


@dataclass
class SqlQueryResult:
    experiment: Experiment
    compound: Compound
    parameter: Parameter
    fragments: Fragment
    exp_groups: expGroupExp
    compound_groups: CompoundGroup
    retention_time: RetentionTime

@dataclass
class FormattedData:
    accession: str
    title: str
    date: str
    authors: str
    inst_license: Optional[str]
    inst_copyright: str
    comment_chunk: str
    compound_name: str
    compound_class: Optional[Union[str, List[str]]]  # Can be a single str, a list of str, or None
    formula: str
    exact_mass: float
    smiles: str
    inchi: str
    cas: str
    inchikey: str
    instrument_name: str
    instrument_type: str
    def_mslevel: str
    ion_mode: str
    ce: int
    frag_mode: str
    ionization: str
    chrom_chunk: str
    precursor_mz: float
    adduct: str
    splash_code: str
    nr_peaks: int
    spectrum: list


def sql_queries_export(session, exp_id, chrom_method):
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
    exp_groups = [group.name for group in exp_groups]
    if len(exp_groups) > 1:
        raise ValueError(
            f"Experiment groups > 1 not allowed. Check experiment ID {exp_id}")

    # Get compound groups
    compound_groups = session.query(CompoundGroup.name).join(compGroupComp) \
        .filter(compGroupComp.c.compound_id == compound.compound_id).all()

    # Get retention times
    retention_time = session.query(RetentionTime).filter_by(compound_id=compound.compound_id,
                                                            chrom_method=chrom_method).first()

    return SqlQueryResult(experiment, compound, parameter, fragments, exp_groups, compound_groups, retention_time)


def extract_and_format_mbank_data(exp_id, chrom_method, sql_data: SqlQueryResult):
    """
    Extracts, processes, and formats experimental data into a structured format for MassBank.

    Args:
        exp_id (int)         : Experiment ID used to query the database.
        chrom_method (str)   : Chromatographic method identifier.
        sql_data (dataclass) : Dataclass containing experiment data and metadata.

    Returns:
          FormattedData (dataclass) : Dataclass containing the formatted data required for constructing the MassBank
                                      document.
    """

    from datetime import datetime
    from rdkit import Chem
    from rdkit.Chem import Descriptors

    # Fragmentation data / Spectrum
    spectrum = get_spectrum(sql_data.fragments)  # Includes rel. intensities
    splash_code = get_splash_code(spectrum)
    spectrum = format_spectrum(spectrum)  # Rounding and removing zeros in intensity (adjusting to MassBank Format)
    nr_peaks = len(spectrum)

    # Experiment related
    precursor_mz = sql_data.experiment.mz
    adduct = sql_data.experiment.adduct
    # precursor_charge = get_precursor_charge(adduct)  # Todo: not used?

    # Compute exact mass using RDKit
    mol = Chem.MolFromSmiles(sql_data.compound.SMILES)
    exact_mass = round(Descriptors.ExactMolWt(mol), 4)

    # Compound related
    compound_name = sql_data.compound.name
    cas = sql_data.compound.CAS
    smiles = sql_data.compound.SMILES
    inchi = sql_data.compound.inchi
    inchikey = sql_data.compound.inchikey
    formula = format_formula(adduct, sql_data.compound.formula)
    compound_class = get_compound_class(sql_data.compound_groups)

    # Retention time
    rt = sql_data.retention_time.rt  # Todo: Currently: error and skip if no RT exists. How is it handled in RMassBank?

    # Parameter related
    ce = int(sql_data.parameter.CE)
    # ces = sql_data.parameter.CES  # Todo: not used?
    instrument_type = sql_data.parameter.instrument.split()[0]
    instrument_name = " ".join(sql_data.parameter.instrument.split()[1:])
    ionization = sql_data.parameter.ionisation
    # ce_unit = sql_data.parameter.ce_unit  # Todo: not used?
    ion_mode = get_ion_mode(sql_data.parameter.polarity)
    frag_mode = get_fragmentation_mode(sql_data.parameter.col_type)

    # Legal stuff
    authors, inst_copyright, contrib_prefix, inst_license = get_contributors_copyright(sql_data.exp_groups)
    if not authors:
        raise ValueError(f"Unknown contributor for experiment ID {exp_id}")

    # Construct title and accession
    def_mslevel = 'MS2'
    entry_prefix = 'CSL'
    massbank_prefix = 'MSBNK'
    title = f"{sql_data.compound.name}; {sql_data.parameter.instrument.split()[0]}; {def_mslevel}; {int(sql_data.parameter.CE)} {sql_data.parameter.ce_unit}"
    date = datetime.now().strftime('%Y.%m.%d')
    date_prefix = datetime.now().strftime('%y%m%d')
    accession = f"{massbank_prefix}-{contrib_prefix}-{entry_prefix}{date_prefix}{exp_id}"

    # Comments
    inst_notation_pairs = inst_code_csl_mapping()
    all_methods = DEFAULT_PAIRS_INST_CHROM
    comment_chunk = \
        (f"COMMENT: CONFIDENCE Reference Standard (Level 1)\n"
         f"COMMENT: Chromatography method: {chrom_method}\n"
         )
    if inst_notation_pairs['bfg'] in sql_data.exp_groups:
        comment_chunk += f"COMMENT: Acquisition method: 10.1002/rcm.8541\n"

    # Chromatography
    if chrom_method == all_methods['bfg']:
        chrom_chunk = \
            (f"AC$CHROMATOGRAPHY: COLUMN_NAME Zorbax Eclipse Plus C18 2.1 mm x 150 mm, 3.5 um, Agilent\n"
             f"AC$CHROMATOGRAPHY: COLUMN_TEMPERATURE 40 °C\n"
             f"AC$CHROMATOGRAPHY: FLOW_GRADIENT 0 min min 98% A, 1 min 98% A, 2 min 80% A, 16.5 min 2% A, 22 min 2% A, 22.1 min 98% A, 27 min 98% A\n"
             f"AC$CHROMATOGRAPHY: FLOW_RATE 0.3 mL/min\n"
             f"AC$CHROMATOGRAPHY: RETENTION_TIME {rt} min\n"
             f"AC$CHROMATOGRAPHY: SOLVENT A: Water 0.1% Formic acid, B: Acetonitrile 0.1% Formic acid\n"
             )
    else:
        chrom_chunk = f"AC$CHROMATOGRAPHY: RETENTION_TIME {rt} min\n"

    return FormattedData(accession, title, date, authors, inst_license, inst_copyright,
                         comment_chunk, compound_name, compound_class, formula, exact_mass,
                         smiles, inchi, cas, inchikey, instrument_name, instrument_type,
                         def_mslevel, ion_mode, ce, frag_mode, ionization, chrom_chunk,
                         precursor_mz, adduct, splash_code, nr_peaks, spectrum)


def build_export_chunk(f_data: FormattedData, csl_version, pycsl_version):
    """
    Assembles the text chunk for the MassBank document in the required order.

    Args:
        f_data (dataclass) : Dataclass containing the relevant formatted data.
        csl_version (str)   : Current version of the CSL database.
        pycsl_version (str) : Current version of the python package.

    Returns:
        export_chunk (str) : Formatted text chunk for the MassBank document.
    """

    # Format export chunk in the correct order
    export_chunk = \
        (f"ACCESSION: {f_data.accession}\n"
         f"RECORD_TITLE: {f_data.title}\n"
         f"DATE: {f_data.date}\n"
         f"AUTHORS: {f_data.authors}\n"
         f"LICENSE: {f_data.inst_license}\n"
         f"COPYRIGHT: {f_data.inst_copyright}\n"
         )
    export_chunk += f_data.comment_chunk

    export_chunk += f"CH$NAME: {f_data.compound_name}\n"

    if f_data.compound_class:
        export_chunk += f"CH$COMPOUND_CLASS: {f_data.compound_class}\n"

    export_chunk += \
        (f"CH$FORMULA: {f_data.formula}\n"
         f"CH$EXACT_MASS: {f_data.exact_mass}\n"
         f"CH$SMILES: {f_data.smiles}\n"
         f"CH$IUPAC: {f_data.inchi}\n"
         f"CH$LINK: CAS {f_data.cas}\n"
         f"CH$LINK: INCHIKEY {f_data.inchikey}\n"
         f"AC$INSTRUMENT: {f_data.instrument_name}\n"
         f"AC$INSTRUMENT_TYPE: {f_data.instrument_type}\n"
         f"AC$MASS_SPECTROMETRY: MS_TYPE {f_data.def_mslevel}\n"
         f"AC$MASS_SPECTROMETRY: ION_MODE {f_data.ion_mode}\n"
         f"AC$MASS_SPECTROMETRY: COLLISION_ENERGY {f_data.ce}\n"
         f"AC$MASS_SPECTROMETRY: FRAGMENTATION_MODE {f_data.frag_mode}\n"
         f"AC$MASS_SPECTROMETRY: IONIZATION {f_data.ionization}\n"
         )

    export_chunk += f_data.chrom_chunk

    export_chunk += \
        (f"MS$FOCUSED_ION: PRECURSOR_M/Z {f_data.precursor_mz}\n"
         f"MS$FOCUSED_ION: PRECURSOR_TYPE {f_data.adduct}\n"
         f"MS$DATA_PROCESSING: COMMENT Export with pycsl {pycsl_version} and CSL {csl_version}\n"
         f"PK$SPLASH: {f_data.splash_code}\n"
         f"PK$NUM_PEAK: {f_data.nr_peaks}\n"
         f"PK$PEAK: m/z int. rel.int.\n"
         )

    # Add the spectrum data
    for mz, intensity, rel_int in f_data.spectrum:
        export_chunk += f"  {mz} {intensity} {rel_int}\n"

    # Last line of a MassBank Record
    export_chunk += f"//"

    return export_chunk


def get_spectrum(fragments):
    """
    Extracts m/z and intensity values from fragments and sorts them by ascending m/z values.
    Calculates relative intensities (as integer) by normalizing to the maximum intensity, scaled by 999.
    (The same procedure as in the Spectra package of RMassBank)
    """

    # Extract m/z and intensity values from fragments
    spectrum = [(frag.mz, frag.int) for frag in fragments]
    intensities = [frag.int for frag in fragments]

    # Calculate relative intensities
    max_intensity = max(intensities)
    relative_intensities = [int((intensity / max_intensity) * 999) for intensity in intensities]
    spectrum = [(mz, intensity, rel_int) for (mz, intensity), rel_int in zip(spectrum, relative_intensities)]

    # Sort by ascending m/z values
    spectrum = sorted(spectrum, key=lambda x: x[0])
    return spectrum


def format_spectrum(spectrum):
    """Removes entries with intensity-values of zero and rounding values for m/z and intensity."""

    # Remove zeros in intensity
    spectrum_nozero = [entry for entry in spectrum if entry[1] != 0]
    # Round values to 4 decimals for mz and intensity.
    updated_spectrum = [(round(mz,4), round(intensity,4), rel_int) for (mz, intensity, rel_int) in spectrum_nozero]
    return updated_spectrum


def get_splash_code(spectrum):
    """
    Generate a spectral hash code using Spectrum:
    Wohlgemuth, G, et al., SPLASH, a Hashed Identifier for Mass Spectra. Nature Biotechnology 34, 1099-101 (2016).
    doi:10.1038/nbt.3689

    Intensity values are multiplied by 1000 before spectral hash code generation to avoid splash code issues.
    """
    from splash import Spectrum, SpectrumType, Splash

    # Multiply intensities by 1000 to avoid splash code issues
    temp_spectrum = []
    for entry in spectrum:
        temp_int = entry[1] * 1000
        temp_spectrum.append((entry[0], temp_int))

    # Generate a spectral hash code
    spec = Spectrum(temp_spectrum, SpectrumType.MS)
    splash_code = Splash().splash(spec)
    return splash_code


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


def format_formula(adduct, formula):
    """
    Returns MassBank-specific format for formula in case of permanent cations / anions
    based on CSL-specific adduct format.
    """
    if adduct == '[M]+':
        formula = f'[{formula}]+'
    elif adduct == '[M]-':
        formula = f'[{formula}]-'
    return formula


def get_compound_class(compound_groups):
    """Extracts the non-institute compound classes from a list of compound groups."""
    inst_notation_pairs = inst_code_csl_mapping()

    compound_groups = [group.name for group in compound_groups]
    compound_groups_filtered = [cg for cg in compound_groups if cg not in inst_notation_pairs.values()]

    if compound_groups:
        compound_class = "; ".join(compound_groups_filtered)
    else:
        compound_class = None
    return compound_class


def get_ion_mode(pol):
    """Returns the MassBank-specific format for polarity information based on the CSL-specific format."""
    if pol == 'pos':
        ion_mode = 'POSITIVE'
    elif pol == 'neg':
        ion_mode = 'NEGATIVE'
    else:
        raise ValueError(f"Unknown polarity format {pol}.")
    return ion_mode


def get_fragmentation_mode(col_type):
    """Returns the MassBank-specific format for fragmentation mode based on the CSL-specific format."""
    if col_type == 'Q':
        frag_mode = 'CID'
    elif col_type == 'HCD':
        frag_mode = 'HCD'
    else:
        raise ValueError(f"Unknown fragmentation mode {col_type}")
    return frag_mode


def get_contributors_copyright(exp_groups):
    """
    Returns legal information based on experiment groups. Todo: change to institute str.

    Returns:
        authors (str) : Contributors.
        inst_copyright (str) : Copyright statement.
        contrib_prefix (str) : Contributor prefix.
        inst_license (str) : Type of licence for the institutes data.
    """
    from datetime import datetime
    inst_notation_pairs = inst_code_csl_mapping()

    current_year = datetime.now().strftime('%Y')
    if inst_notation_pairs['bfg'] in exp_groups:
        authors = 'Ole Lessmann; Kevin S. Jewell; Björn Ehlig; Arne Wick'
        inst_copyright = f'Copyright {current_year} Federal Institute of Hydrology, Koblenz, Germany'
        contrib_prefix = 'BAFG'  # Todo: change?
        inst_license = 'dl-de/by-2-0'
    elif inst_notation_pairs['lfuby'] in exp_groups:
        authors = 'André Macherius; Uwe Kunkel'
        inst_copyright = f'Copyright {current_year} Bavarian Environment Agency, Augsburg, Germany'
        contrib_prefix = 'LFUBY'
        inst_license = None  # Todo licence for lfuby?
    elif inst_notation_pairs['uba'] in exp_groups:
        authors = 'Eric Rosenheinrich; Anja Duffeck'
        inst_copyright = f'Copyright {current_year} Federal Environment Agency, Berlin, Germany'
        contrib_prefix = 'UBA'
        inst_license = 'dl-de/by-2-0'
    else:
        authors = None; inst_copyright = None; contrib_prefix = None; inst_license = None
    return authors, inst_copyright, contrib_prefix, inst_license
