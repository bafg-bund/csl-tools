from .format_utils import *
# from utils.sql_utils import inst_code_csl_mapping
from dataclasses import dataclass
from typing import Optional, Union, List


def extract_experiment_chunk_thermo(session, exp_id, chrom_method, csl_version, pycsl_version):
    """."""

    # SQL queries based on experiment ID and chromatographic method
    SqlQueryResult = sql_queries_by_exp_id_chrom_method(session, exp_id, chrom_method)

    # Format data to meet MSP/NIST format requirements
    FormattedDataThermo = extract_and_format_thermo_data(exp_id, chrom_method, csl_version, pycsl_version, SqlQueryResult)

    # Assemble text chunk for the MSP/NIST document
    export_chunk = build_export_chunk_thermo(FormattedDataThermo)

    return export_chunk


@dataclass
class FormattedDataThermo:
    accession: str
    adduct: str
    authors: str
    cas: str
    ce: int
    comment_chunk: str
    compound_classes: Optional[Union[str, List[str]]]  # Can be a single str, a list of str, or None
    compound_name: str
    date: str
    def_centroided: str
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
    precursor_charge: int
    precursor_mz: float
    rt: float
    spectrum: list
    splash_code: str
    smiles: str
    title: str


def extract_and_format_thermo_data(exp_id, chrom_method, csl_version, pycsl_version, sql_data: SqlQueryResult):
    """
    Extracts, processes, and formats experimental data into a structured format for MSP/NIST documents.

    Args:
        exp_id (int)         : Experiment ID used to query the database.
        chrom_method (str)   : Chromatographic method identifier.
        csl_version (str)    : Current version of the CSL database.
        pycsl_version (str)  : Current version of the python package.
        sql_data (dataclass) : Dataclass containing experiment data and metadata.

    Returns:
          FormattedData (dataclass) : Dataclass containing the formatted data required for constructing the MassBank
                                      document.
    """

    from datetime import datetime
    from rdkit import Chem
    from rdkit.Chem import Descriptors

    # Default configuration
    def_centroided = 'TRUE'
    def_mslevel = 'MS2'

    # Fragmentation data / Spectrum
    spectrum = get_spectrum(sql_data.fragments)  # Includes rel. intensities
    spectrum = format_spectrum_thermo(spectrum)  # Rounding and removing zeros in intensity (adjusting to MassBank Format)
    nr_peaks = len(spectrum)
    splash_code = get_splash_code(spectrum)

    # Experiment related
    precursor_mz = sql_data.experiment.mz
    adduct = sql_data.experiment.adduct
    precursor_charge = get_precursor_charge(sql_data.experiment.adduct)

    # Compute exact mass using RDKit
    mol = Chem.MolFromSmiles(sql_data.compound.SMILES)
    exact_mass = round(Descriptors.ExactMolWt(mol), 4)

    # Compound related
    compound_name = sql_data.compound.name
    cas = sql_data.compound.CAS
    smiles = sql_data.compound.SMILES
    inchi = sql_data.compound.inchi
    inchikey = sql_data.compound.inchikey
    formula = sql_data.compound.formula
    compound_classes = get_compound_classes(sql_data.compound_groups)

    # Retention time
    rt = sql_data.retention_time.rt  # Todo: what happens if rt does not exist?

    # Parameter related
    ce = int(sql_data.parameter.CE)
    instrument_type = sql_data.parameter.instrument.split()[0]
    instrument_name = " ".join(sql_data.parameter.instrument.split()[1:])
    ionization = sql_data.parameter.ionisation
    ce_unit = sql_data.parameter.ce_unit
    ion_mode = get_ion_mode_thermo(sql_data.parameter.polarity)
    frag_mode = sql_data.parameter.col_type

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
    title = f"{sql_data.compound.name}; {sql_data.parameter.instrument.split()[0]}; {def_mslevel}; {ce} {ce_unit}"

    # Current date
    date = datetime.now().strftime('%Y.%m.%d')

    # Unique experiment identifier
    accession = f"{exp_id}"

    # Comments
    inst_notation_pairs = inst_code_csl_mapping()
    comment_chunk = "".join(filter(None, [
        f"COMMENT: CONFIDENCE Reference Standard (Level 1)\n",
        f"COMMENT: Chromatography method: {chrom_method}\n",
        f"COMMENT: Acquisition method: 10.1002/rcm.8541\n" if inst_notation_pairs['bfg'] in sql_data.exp_groups else None,
        f"COMMENT: Export with pycsl {pycsl_version} and CSL {csl_version}\n"
        ]))

    return FormattedDataThermo(accession, adduct, authors, cas, ce, comment_chunk, compound_classes, compound_name,
                               date, def_centroided, def_mslevel, exact_mass, formula, frag_mode, inchi, inchikey,
                               inst_copyright, inst_license, instrument_name, instrument_type, ion_mode, ionization,
                               nr_peaks, precursor_charge, precursor_mz, rt, spectrum, splash_code, smiles, title)


def build_export_chunk_thermo(f_data: FormattedDataThermo):
    """
    Assembles the text chunk for the MSP/NIST document in the required order.

    Args:
        f_data (dataclass) : Dataclass containing the relevant formatted data.

    Returns:
        export_chunk (str) : Formatted text chunk for the MSP/NIST document.
    """

    # Creating export text chunk
    export_chunk = "".join(filter(None, [                   # Imported to mzVault (v2.3.64.0)?
         f"NAME: {f_data.compound_name}\n",                     # YES
         f"ACCESSION: {f_data.accession}\n",                            # NO
         f"RECORD_TITLE: {f_data.title}\n",                             # NO
         f"DATE: {f_data.date}\n",                                      # NO
         f"AUTHORS: {f_data.authors}\n",                                # NO
         f"LICENSE: {f_data.inst_license}\n",                           # NO
         f"COPYRIGHT: {f_data.inst_copyright}\n",                       # NO
         f"{f_data.comment_chunk}" if f_data.comment_chunk else None,   # NO
         f"COMPOUNDCLASS: {f_data.compound_classes}\n"          # YES
         if f_data.compound_classes else None,
         f"FORMULA: {f_data.formula}\n",                        # YES
         f"EXACT_MASS: {f_data.exact_mass}\n",                          # NO
         f"CENTROIDED: {f_data.def_centroided}\n",                      # NO
         f"SMILES: {f_data.smiles}\n",                          # YES
         f"INCHI: {f_data.inchi}\n",                                    # NO
         f"CASNO: {f_data.cas}\n",                              # YES
         f"INCHIKEY: {f_data.inchikey}\n",                      # YES
         f"INSTRUMENT: {f_data.instrument_name}\n",                     # NO
         f"INSTRUMENTTYPE: {f_data.instrument_type}\n",                 # NO
         f"MS_TYPE: {f_data.def_mslevel}\n",                            # NO
         f"ION_MODE: {f_data.ion_mode}\n",                      # YES
         f"COLLISION_ENERGY: {f_data.ce}\n",                    # YES
         f"FRAGMENTATION_MODE: {f_data.frag_mode}\n",                   # NO
         f"IONIZATION: {f_data.ionization}\n",                  # YES
         f"RETENTIONTIME: {f_data.rt}\n",                       # YES
         f"PRECURSORMZ: {f_data.precursor_mz}\n",               # YES
         f"PRECURSORTYPE: {f_data.adduct}\n",                   # YES
         f"PRECURSOR_CHARGE: {f_data.precursor_charge}\n",              # NO
         f"SPLASH: {f_data.splash_code}\n",                             # NO
         f"Num Peaks: {f_data.nr_peaks}\n",                     # YES (Spectrum data)
         ]))

    # Add the spectrum data
    for mz, intensity in f_data.spectrum:
        export_chunk += f"{mz} {intensity}\n"

    return export_chunk


def format_spectrum_thermo(spectrum):
    """Removes entries with intensity-values of zero and rounding values for m/z and intensity."""
    # Remove zeros in intensity
    spectrum_nozero = [entry for entry in spectrum if entry[1] != 0]
    # Round values to 4 decimals for mz and intensity.
    formatted_spectrum = [(round(mz,4), round(intensity,4)) for (mz, intensity) in spectrum_nozero]
    return formatted_spectrum


def get_ion_mode_thermo(pol):
    """Returns the MSP/NIST-specific format for polarity information based on the CSL-specific format."""
    if pol == 'pos':
        ion_mode = 'Positive'
    elif pol == 'neg':
        ion_mode = 'Negative'
    else:
        raise ValueError(f"Unknown polarity format {pol}.")
    return ion_mode
