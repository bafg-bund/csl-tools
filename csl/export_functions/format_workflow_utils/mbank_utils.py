from export_functions.format_workflow_utils import *
from utils.sql_utils import inst_code_csl_mapping
from config import DEFAULT_PAIRS_INST_CHROM
from dataclasses import dataclass
from typing import Optional, Union, List


def get_exp_ids_mbank(path_mbank_files):
    """
    Retrieve current MassBank experiment IDs (=accession numbers).

    Args:
        path_mbank_files (str) : Path to directory with existing MassBank files.

    Returns:
        dict_mbank_exp_id_fn (dict) : Pairs of existing of accession strings and experiment IDs.
    """
    import os
    import re
    from pathlib import Path

    # Get all filenames
    filenames = [file for file in os.listdir(path_mbank_files) if file.endswith(".txt")]

    # Pattern to extract the experiment ID after the date (YYMMDD)
    pattern = r"MSBNK-BAFG-CSL\d{6}(\d+)"

    # Create a dictionary with extracted experiment ID as keys and filenames as values
    dict_mbank_exp_id_fn = {
        int(re.search(pattern, fn).group(1)): Path(fn).stem
        for fn in filenames if re.search(pattern, fn)
    }
    return dict_mbank_exp_id_fn

def extract_experiment_chunk_mbank(session, exp_id, chrom_method, csl_version, pycsl_version, dict_mbank_exp_id_fn):
    """
    Extracts data for a specific experiment id and formats data for MassBank requirements.

    Args:
        session (obj)               : SQLAlchemy session object connected to the CSL database.
        exp_id (int)                : Experiment ID used to query the database.
        chrom_method (str)          : Chromatographic method identifier.
        csl_version (str)           : Current version of the CSL database.
        pycsl_version (str)         : Current version of the python package.
        dict_mbank_exp_id_fn (dict) : Pairs of existing of accession strings and experiment IDs.

    Returns:
        export_chunk (str) : Text chunk formatted to MassBank requirements for a single txt file.
    """

    # SQL queries based on experiment ID and chromatographic method
    SqlQueryResult = sql_queries_by_exp_id_chrom_method(session, exp_id, chrom_method)

    # Skip internal standards
    skip_comp = skip_compounds_mbank()
    if SqlQueryResult.compound.name in skip_comp:
        return None

    # Format data to meet MassBank format requirements
    FormattedData = extract_and_format_mbank_data(exp_id, chrom_method, csl_version, pycsl_version, SqlQueryResult, dict_mbank_exp_id_fn)

    # Assemble text chunk for the MassBank document
    export_chunk = build_export_chunk_mbank(FormattedData)

    return export_chunk


@dataclass
class FormattedDataMbank:
    accession: str
    adduct: str
    authors: str
    cas: str
    ce: int
    comment_chunk: str
    compound_classes: Optional[Union[str, List[str]]]  # Can be a single str, a list of str, or None
    compound_name: str
    chrom_chunk: str
    data_proc_chunk: str
    date: str
    def_mslevel: str
    exact_mass: float
    formula: str
    frag_mode: str
    inchi: str
    inchikey: str
    inst_copyright: str
    inst_license: Optional[str]
    instrument_name: str
    instrument_type: str
    ion_mode: str
    ionization: str
    nr_peaks: int
    precursor_mz: float
    spectrum: list
    splash_code: str
    smiles: str
    title: str


def extract_and_format_mbank_data(exp_id, chrom_method, csl_version, pycsl_version, sql_data: SqlQueryResult, dict_mbank_exp_id_fn):
    """
    Extracts, processes, and formats experimental data into a structured format for MassBank documents.

    Args:
        exp_id (int)                : Experiment ID used to query the database.
        chrom_method (str)          : Chromatographic method identifier.
        csl_version (str)           : Current version of the CSL database.
        pycsl_version (str)         : Current version of the python package.
        sql_data (dataclass)        : Dataclass containing experiment data and metadata.
        dict_mbank_exp_id_fn (dict) : Pairs of existing of accession strings and experiment IDs.

    Returns:
          FormattedData (dataclass) : Dataclass containing the formatted data required for constructing the MassBank
                                      document.
    """
    from datetime import datetime
    from rdkit import Chem
    from rdkit.Chem import Descriptors

    # Fragmentation data / Spectrum
    spectrum = get_spectrum(sql_data.fragments)  # Includes rel. intensities
    spectrum = format_spectrum_mbank(spectrum)  # Rounding and removing zeros in intensity (adjusting to MassBank Format)
    nr_peaks = len(spectrum)
    splash_code = get_splash_code(spectrum)

    # Experiment related
    precursor_mz = sql_data.experiment.mz
    adduct = sql_data.experiment.adduct

    # Compute exact mass using RDKit
    mol = Chem.MolFromSmiles(sql_data.compound.SMILES)
    exact_mass = round(Descriptors.ExactMolWt(mol), 4)

    # Compound related
    compound_name = sql_data.compound.name
    cas = sql_data.compound.CAS
    smiles = sql_data.compound.SMILES
    inchi = sql_data.compound.inchi
    inchikey = sql_data.compound.inchikey
    formula = format_formula_mbank(adduct, sql_data.compound.formula)
    compound_classes = get_compound_classes(sql_data.compound_groups)

    # Retention time
    rt = sql_data.retention_time.rt  # Todo: Currently: error and skip if no RT exists. How is it handled in RMassBank?

    # Parameter related
    ce = int(sql_data.parameter.CE)
    instrument_type = sql_data.parameter.instrument.split()[0]
    instrument_name = " ".join(sql_data.parameter.instrument.split()[1:])
    ionization = sql_data.parameter.ionisation
    ce_unit = sql_data.parameter.ce_unit
    ion_mode = get_ion_mode_mbank(sql_data.parameter.polarity)
    frag_mode = get_fragmentation_mode_mbank(sql_data.parameter.col_type)

    # Experiment groups
    exp_groups = [group.name for group in sql_data.exp_groups]
    if len(exp_groups) > 1:
        raise ValueError(
            f"Experiment groups > 1 not allowed. Check experiment ID {exp_id}")

    # Legal stuff
    authors, inst_copyright, contrib_prefix, inst_license = get_contributors_copyright(exp_groups[0])
    if not authors:
        raise ValueError(f"Unknown contributor for experiment ID {exp_id}")

    # Construct title
    def_mslevel = 'MS2'
    title = f"{sql_data.compound.name}; {sql_data.parameter.instrument.split()[0]}; {def_mslevel}; {ce} {ce_unit}"

    # Get accession string
    accession = get_accession_mbank(exp_id, contrib_prefix, dict_mbank_exp_id_fn)

    # Current date
    date = datetime.now().strftime('%Y.%m.%d')

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

    data_proc_chunk = f"MS$DATA_PROCESSING: COMMENT Export with pycsl {pycsl_version} and CSL {csl_version}\n"


    return FormattedDataMbank(accession, adduct, authors, cas, ce, comment_chunk, compound_classes, compound_name,
                              chrom_chunk, data_proc_chunk, date, def_mslevel, exact_mass, formula, frag_mode, inchi,
                              inchikey, inst_copyright, inst_license, instrument_name, instrument_type, ion_mode,
                              ionization, nr_peaks, precursor_mz, spectrum, splash_code, smiles, title)


def build_export_chunk_mbank(f_data: FormattedDataMbank):
    """
    Assembles the text chunk for the MassBank document in the required order.

    Args:
        f_data (dataclass) : Dataclass containing the relevant formatted data.

    Returns:
        export_chunk (str) : Formatted text chunk for the MassBank document.
    """

    # Format export chunk in the correct order
    export_chunk = "".join(filter(None, [
        f"ACCESSION: {f_data.accession}\n",
        f"RECORD_TITLE: {f_data.title}\n",
        f"DATE: {f_data.date}\n",
        f"AUTHORS: {f_data.authors}\n",
        f"LICENSE: {f_data.inst_license}\n",
        f"COPYRIGHT: {f_data.inst_copyright}\n",
        f"{f_data.comment_chunk}" if f_data.comment_chunk else None,
        f"CH$NAME: {f_data.compound_name}\n",
        f"CH$COMPOUND_CLASS: {f_data.compound_classes}\n" if f_data.compound_classes else None,
        f"CH$FORMULA: {f_data.formula}\n",
        f"CH$EXACT_MASS: {f_data.exact_mass}\n",
        f"CH$SMILES: {f_data.smiles}\n",
        f"CH$IUPAC: {f_data.inchi}\n",
        f"CH$LINK: CAS {f_data.cas}\n",
        f"CH$LINK: INCHIKEY {f_data.inchikey}\n",
        f"AC$INSTRUMENT: {f_data.instrument_name}\n",
        f"AC$INSTRUMENT_TYPE: {f_data.instrument_type}\n",
        f"AC$MASS_SPECTROMETRY: MS_TYPE {f_data.def_mslevel}\n",
        f"AC$MASS_SPECTROMETRY: ION_MODE {f_data.ion_mode}\n",
        f"AC$MASS_SPECTROMETRY: COLLISION_ENERGY {f_data.ce}\n",
        f"AC$MASS_SPECTROMETRY: FRAGMENTATION_MODE {f_data.frag_mode}\n",
        f"AC$MASS_SPECTROMETRY: IONIZATION {f_data.ionization}\n",
        f"{f_data.chrom_chunk}" if f_data.chrom_chunk else None,
        f"MS$FOCUSED_ION: PRECURSOR_M/Z {f_data.precursor_mz}\n",
        f"MS$FOCUSED_ION: PRECURSOR_TYPE {f_data.adduct}\n",
        f"{f_data.data_proc_chunk}",
        f"PK$SPLASH: {f_data.splash_code}\n",
        f"PK$NUM_PEAK: {f_data.nr_peaks}\n",
        f"PK$PEAK: m/z int. rel.int.\n"
    ]))

    # Add the spectrum data
    for mz, intensity, rel_int in f_data.spectrum:
        export_chunk += f"  {mz} {intensity} {rel_int}\n"

    # Last line of a MassBank Record
    export_chunk += f"//\n"

    return export_chunk


def format_spectrum_mbank(spectrum):
    """Removes entries with intensity-values of zero and rounding values for m/z and intensity."""

    # Remove zeros in intensity
    spectrum_nozero = [entry for entry in spectrum if entry[1] != 0]

    intensities = [spec[1] for spec in spectrum_nozero]
    # Calculate relative intensities
    max_intensity = max(intensities)
    relative_intensities = [int((intensity / max_intensity) * 999) for intensity in intensities]
    spectrum_rel_int = [(mz, intensity, rel_int) for (mz, intensity), rel_int in zip(spectrum_nozero, relative_intensities)]

    # Round values to 4 decimals for mz and intensity.
    formatted_spectrum = [(round(mz,4), round(intensity,4), rel_int) for (mz, intensity, rel_int) in spectrum_rel_int]
    return formatted_spectrum


def format_formula_mbank(adduct, formula):
    """
    Returns MassBank-specific format for formula in case of permanent cations / anions
    based on CSL-specific adduct format.
    """
    if adduct == '[M]+':
        formula = f'[{formula}]+'
    elif adduct == '[M]-':
        formula = f'[{formula}]-'
    return formula


def get_ion_mode_mbank(pol):
    """Returns the MassBank-specific format for polarity information based on the CSL-specific format."""
    if pol == 'pos':
        ion_mode = 'POSITIVE'
    elif pol == 'neg':
        ion_mode = 'NEGATIVE'
    else:
        raise ValueError(f"Unknown polarity format {pol}.")
    return ion_mode


def get_fragmentation_mode_mbank(col_type):
    """Returns the MassBank-specific format for fragmentation mode based on the CSL-specific format."""
    if col_type == 'Q':
        frag_mode = 'CID'
    elif col_type == 'HCD':
        frag_mode = 'HCD'
    else:
        raise ValueError(f"Unknown fragmentation mode {col_type}")
    return frag_mode


def get_accession_mbank(exp_id, contrib_prefix , dict_mbank_exp_id_fn):
    """
    Determines accession string for an experiment ID.
    If accession already exists for the experiment ID, the accession remains unchanged.
    Otherwise, a new accession string is created.

    Args:
        exp_id (int)                : Experiment ID
        contrib_prefix (str)        : Contributor prefix in MassBank format.
        dict_mbank_exp_id_fn (dict) : Pairs of existing of accession strings and experiment IDs.

    Return:
        accession (str) : Unique MassBank-specific identifier for each txt file.
    """
    from datetime import datetime

    if exp_id in dict_mbank_exp_id_fn.keys():
        accession = dict_mbank_exp_id_fn[exp_id]
    else:
        massbank_prefix = 'MSBNK'
        entry_prefix = 'CSL'
        date_prefix = datetime.now().strftime('%y%m%d')
        accession = f"{massbank_prefix}-{contrib_prefix}-{entry_prefix}{date_prefix}{exp_id}"

    return accession
