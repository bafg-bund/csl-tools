from csl.export_functions.utils.export_utils import *
from dataclasses import dataclass


def extract_experiment_chunk_libview(exp_id, chrom_method, csl_version, CSLTOOLS_VERSION, sql_data_dict):
    """
    Extracts data for a specific experiment id and formats data for LibraryView (SCIEX) documents (.sdf).

    Args:
        exp_id (int)           : Experiment ID used to query the database.
        chrom_method (str)     : Chromatographic method identifier.
        csl_version (str)      : Current version of the CSL database.
        CSLTOOLS_VERSION (str) : Current version of the python package.
        sql_data_dict (dict[int, SqlQueryResult(dataclass)]) : Mapping of exp_id to SqlQueryResult

    Returns:
        export_chunk (str) : Text chunk formatted for a single LibraryView entry.
    """
    # SQL queries based on experiment ID
    SqlQueryResult = sql_data_dict.get(exp_id)
    if not SqlQueryResult:
        return None

    # Format data to meet LibraryView format requirements
    FormattedDataLibview = extract_and_format_libview_data(exp_id, chrom_method, csl_version, CSLTOOLS_VERSION, SqlQueryResult)

    # Assemble text chunk for the LibraryView entry
    export_chunk = build_export_chunk_libview(FormattedDataLibview)

    return export_chunk


@dataclass
class FormattedDataLibview:
    authors: str
    cas: str
    ce: int
    ces: int
    comment_chunk: str
    compound_name: str
    csl_version: str
    exact_mass: float
    formula: str
    instrument_name: str
    instrument_type: str
    ion_mode: str
    ionization: str
    molblock: str
    nr_peaks: int
    precursor_mz: float
    spectrum: list
    time_spectrum: str


def extract_and_format_libview_data(exp_id, chrom_method, csl_version, CSLTOOLS_VERSION, sql_data: SqlQueryResult):
    """
    Extracts, processes, and formats experimental data into a structured format for LibraryView documents.

    Args:
        exp_id (int)           : Experiment ID used to query the database.
        chrom_method (str)     : Chromatographic method identifier.
        csl_version (str)      : Current version of the CSL database.
        CSLTOOLS_VERSION (str) : Current version of the python package.
        sql_data (dataclass)   : Dataclass containing experiment data and metadata.

    Returns:
          FormattedData (dataclass) : Dataclass containing the formatted data required for constructing the entry.
    """
    from datetime import datetime
    from rdkit import Chem
    from rdkit.Chem import Descriptors, inchi

    # Default configuration
    def_centroided = 'TRUE'
    def_mslevel = 'MS2'

    # Fragmentation data / Spectrum
    spectrum = get_spectrum(sql_data.fragments)  # Includes rel. intensities
    spectrum = format_spectrum_libview(spectrum)  # Rounding and removing zeros in intensity
    nr_peaks = len(spectrum)
    splash_code = get_splash_code(spectrum)

    # Experiment related
    precursor_mz = sql_data.experiment.mz
    adduct = sql_data.experiment.adduct
    precursor_charge = get_precursor_charge(sql_data.experiment.adduct)

    # Compute exact mass using RDKit
    mol = Chem.MolFromSmiles(sql_data.compound.smiles)
    exact_mass = round(Descriptors.ExactMolWt(mol), 4)

    # Compound related
    compound_name = sql_data.compound.name
    cas = sql_data.compound.cas
    smiles = sql_data.compound.smiles
    inchi_var = sql_data.compound.inchi
    inchikey = sql_data.compound.inchikey
    formula = sql_data.compound.formula
    compound_classes = get_compound_classes(sql_data.compound_groups)

    # Molblock
    mol = Chem.inchi.MolFromInchi(inchi_var.strip())
    molblock = Chem.MolToMolBlock(mol)

    # Retention time
    rt_entry = next(
        (entry for entry in sql_data.retention_time if entry.chrom_method == chrom_method),
        None
    )
    rt = rt_entry.rt
    pred = rt_entry.predicted

    # Parameter related
    ce = int(sql_data.parameter.ce)
    ces = int(sql_data.parameter.ces)
    instrument_type = sql_data.parameter.instrument.split()[0]
    instrument_name = " ".join(sql_data.parameter.instrument.split()[1:])
    ionization = sql_data.parameter.ionisation
    ce_unit = sql_data.parameter.ce_unit
    ion_mode = get_ion_mode_libview(sql_data.parameter.polarity)
    frag_mode = sql_data.parameter.collision_type

    # Legal stuff
    authors, dsrc_copyright, contrib_prefix, dsrc_license = get_contributors_copyright(sql_data.data_src)
    if not authors:
        raise ValueError(f"Unknown contributor for experiment ID {exp_id}. Check link to table data_source in CSL.")

    # Time when spectrum was added
    time_spectrum = sql_data.experiment.time_added.strftime('%Y-%m-%dT%H:%M:%S.%f')

    # Current date
    date = datetime.now().strftime('%Y.%m.%d')

    # Comments
    comment_chunk = "".join(filter(None, [
        f"Export with csl-tools {CSLTOOLS_VERSION} and CSL_v{csl_version}\n",
        f"Export date: {date}\n"
        f"CONFIDENCE Reference Standard (Level 1)\n",
        f"Chromatography method: {chrom_method}\n",
        f"Acquisition method: 10.1002/rcm.8541\n" if sql_data.data_src.name == 'bfg' else None,
        f"Retention time: {rt}\n",
        f"Predicted RT: {pred}\n",
        f"SMILES: {smiles}\n",
        f"InChI: {inchi_var}\n",
        f"InChIKey: {inchikey}\n",
        f"Compound class: {compound_classes}\n",
        f"Collision energy unit: {ce_unit}\n",
        f"Collision type: {frag_mode}\n",
        f"Unique experiment identifier: {exp_id}\n",
        f"Adduct: {adduct}\n",
        f"Precursor charge: {precursor_charge}\n",
        f"SPLASH code: {splash_code}\n",
        f"Centroided: {def_centroided}\n",
        f"MS type: {def_mslevel}\n",
        f"License: {dsrc_license}\n",
        f"Copyright: {dsrc_copyright}\n",
        ]))

    return FormattedDataLibview(authors, cas, ce, ces, comment_chunk, compound_name, csl_version, exact_mass, formula,
                               instrument_name, instrument_type, ion_mode, ionization, molblock, nr_peaks, precursor_mz,
                                spectrum, time_spectrum)


def build_export_chunk_libview(f_data: FormattedDataLibview):
    """
    Assembles the text chunk in the required order.

    Args:
        f_data (dataclass) : Dataclass containing the relevant formatted data.

    Returns:
        export_chunk (str) : Formatted text chunk for the LibraryView document.
    """
    # Creating export text chunk
    export_chunk = "".join(filter(None, [
         f"{f_data.compound_name}\n\n",
         f"CAS rn = {f_data.cas}\n",
         f"{f_data.molblock}\n",
         f">  <NAME>\n{f_data.compound_name}\n\n",
         f">  <ION MODE>\n{f_data.ion_mode}\n\n",
         f">  <INSTRUMENT>\n{f_data.instrument_type} {f_data.instrument_name}\n\n",
         f">  <COLLISION ENERGY>\n{f_data.ce}\n\n",
         f">  <PRECURSOR M/Z>\n{f_data.precursor_mz}\n\n",
         f">  <CASNO>\n{f_data.cas}\n\n",
         f">  <MOLECULAR WEIGHT>\n\n\n",
         f">  <MONOISOTOPIC MASS>\n{f_data.exact_mass}\n\n",
         f">  <FORMULA>\n{f_data.formula}\n\n",
         f">  <COLLISION ENERGY SPREAD>\n{f_data.ces}\n\n",
         f">  <ION SOURCE>\n{f_data.ionization}\n\n",
         f">  <SCAN TYPE>\n\n\n",
         f">  <CAD GAS TYPE>\n\n\n",
         f">  <CAD GAS VALUE>\n\n\n",
         f">  <SPECTRUM CREATED DATE>\n{f_data.time_spectrum}\n\n",
         f">  <CONTRIBUTOR>\n{f_data.authors}\n\n",
         f">  <REGION-NAMES>\n\n\n",
         f">  <LIBRARYNAME>\nCSL_v{f_data.csl_version}\n\n",
         f">  <COMMENT>\n{f_data.comment_chunk}\n\n" if f_data.comment_chunk else None,
         f">  <NUM PEAKS>\n{f_data.nr_peaks}\n\n",
         ]))

    # Add the spectrum data
    export_chunk += f">  <MASS SPECTRAL PEAKS>\n"
    for mz, intensity in f_data.spectrum:
        export_chunk += f"{mz} {intensity}\n"

    # Add chunk identifier
    export_chunk += f"\n$$$$\n"

    return export_chunk


def format_spectrum_libview(spectrum):
    """Removes entries with intensity-values of zero and rounding values for m/z and intensity."""
    # Remove zeros in intensity
    spectrum_nozero = [entry for entry in spectrum if entry[1] != 0]
    # Round values to 4 decimals for mz and intensity.
    formatted_spectrum = [(round(mz,4), round(intensity,4)) for (mz, intensity) in spectrum_nozero]
    return formatted_spectrum


def get_ion_mode_libview(pol):
    """Returns the LibraryView-specific format for polarity information based on the CSL-specific format."""
    if pol == 'pos':
        ion_mode = 'P'
    elif pol == 'neg':
        ion_mode = 'N'
    else:
        raise ValueError(f"Unknown polarity format {pol}.")
    return ion_mode
