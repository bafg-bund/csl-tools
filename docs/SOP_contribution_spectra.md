# Guideline: Contribution of spectral data

Currently, processing of data export files of the following software are supported:

| Software               | Version           | Data file example                                                                                                                                        |
|------------------------|-------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| mzVault (ThermoFisher) | Version 2.3.64.0  | [example_export_mzvault_1.msp](example_files/example_export_mzvault_2.3.64.0.msp)                                                                        |
| mzVault (ThermoFisher) | Version 2.3.45.15 | [example_export_mzvault_2.msp](example_files/example_export_mzvault_2.3.45.15.msp)                                                                       |
| LibraryView (SCIEX)    | Version 1.8       | [example_export_libview.sdf](example_files/example_export_libview_1.8.sdf)                                                                               |
| MassBank               | Version 2.6.0     | [example_export_mbank_1.txt](example_files/example_export_mbank_3716.txt)<br> [example_export_mbank_2.txt](example_files/example_export_mbank_35237.txt) |

The direct data export from each software can be processed. Please check if it matches the format of the example files.
Additionally, you need to provide a [configuration file](#configuration-file) that contains other required (constant) 
parameters that are not provided in the data file. These parameters are applied to the whole processed batch.
The LibraryView-based data export files (.sdf) do not contain retention times. 
A [supplementary file](#supplementary-rt-file) is necessary that links compound names to retention times.

- Multiple data files can be processed at once (and each can contain multiple experiments except for MassBank documents).
- For MassBank documents refer to the official [MassBank Record Format](https://github.com/MassBank/MassBank-web/blob/main/Documentation/MassBankRecordFormat.md)

Full list of [required parameters](#parameter-requirements) with detailed description

>If your software is not supported, we are happy to implement a new workflow or find a solution. 
Feel free to contact us at `ntsportal@bafg.de`.


# Configuration file

Click to open an example [configuration file (.yaml)](example_files/example_config.yaml) or see below.  

Example configuration file with all possible parameters:
```yaml
# Example configuration
par_config:
  par_isotope: 'monoisotopic'             # Type of molecular mass
  par_ionization: 'ESI'                   # Ionization type
  par_col_type: 'Q'                       # Collision type
  par_ce_unit: 'V'                        # Unit for collision energy
  par_instrument: 'TripleTOF 5600 SCIEX'  # Instrument name
  par_instrument_type: 'LC-ESI-QTOF '     # Instrument type
  par_data_source: 'bfg'                  # Data source identifier
  par_authors: 'Björn Ehlig; Kevin S. Jewell; Ole Lessmann; Arne Wick'  # Author name(s)
  par_affiliation: 'Federal Institute of Hydrology (Bundesanstalt für Gewässerkunde), Koblenz, Germany'  # Author affiliation

# Special adduct notation rules (leave curly brackets empty if no special cases needed).
adduct_notation: {
  'cation': '[M]+',
  'Ethylamin': '[M+C2H7N+H]+',
  'FA': '[M+HCOO-]-',
  'NaFA': '[M+NaCOO-]-',
}
```

# Supplementary RT file
Needed additionally for LibraryView-based export files.

- Contains compound names and their retention times
- CSV file (UTF-8 encoded)
- Semicolon-separated (`;`)
- Header format: `Name;Retention Time (min)`

Click to open an example [supplementary file (.csv)](example_files/example_extrafile_libview.csv) or see below.  

Example supplementary file:
```
Name;Retention Time (min)
Bezafibrate;11.03300
3,6-Dimethyl-4-octyne-3,6-diol;7.70700
```

# Parameter requirements

| Parameter description                 | Required        | Subsection                                                           |
|---------------------------------------|-----------------|----------------------------------------------------------------------|
| Data source                           | Yes             | [Data source](#data-source)                                          |
| Author name(s)                        | Yes             | [Authors](#authors)                                                  |
| Author affiliation                    | Yes             | [Author affiliation](#author-affiliation)                            |
| Compound name                         | Yes             | [Compound name](#compound-name)                                      |
| Special adduct / source fragment      | No<sup>1</sup>  | [Special adduct / Source fragment](#adducts-and-in-source-fragments) |
| Compound class / category             | No              | [Compound class](#compound-class)                                    |
| Compound formula                      | Yes             | [Compound formula](#compound-formula)                                |
| SMILES code                           | Yes             | [SMILES code](#smiles)                                               |
| InChIKey                              | Yes<sup>2</sup> | [InChIKey](#inchikey)                                                |
| CAS Registry Number                   | Yes<sup>2</sup> | [CAS Registry Number](#cas-registry-number)                          |
| Instrument name                       | Yes             | [Instrument name and type](#instrument-name-and-type)                |
| Instrument type                       | No              | [Instrument name and type](#instrument-name-and-type)                |
| Ion mode                              | Yes             | [Ion mode](#ion-mode)                                                |
| Collision energy                      | Yes<sup>3</sup> | [Collision energy](#collision-energy)                                |
| Collision energy unit                 | Yes<sup>3</sup> | [Collision energy unit](#collision-energy-unit)                      |
| Collision type                        | Yes             | [Collision type](#collision-type)                                    |
| Electron energy                       | Yes<sup>3</sup> | [Electron energy](#electron-energy)                                  |
| Electron energy unit                  | Yes<sup>3</sup> | [Electron energy unit](#electron-energy-unit)                        |
| Ionization type                       | Yes             | [Ionization type](#ionization-type)                                  |
| Precursor m/z                         | Yes             | [Precursor m/z](#precursor-mz)                                       |
| Type of molecular mass / Isotopologue | Yes             | [Isotopologue](#isotopologue)                                        |
| Retention time                        | Yes             | [Retention time](#retention-time)                                    |
| Kovats retention index                | No              | [Kovats retention index](#kovats-retention-index)                    |
| Spectrum (m/z and intensity)          | Yes             | [Spectrum](#spectrum)                                                |

<sup>1</sup> No adduct information results in assumption of `[M+H]+` or `[M–H]–` based on the polarity.  
<sup>2</sup> At least one is required: InChIKey or CAS.  
<sup>3</sup> Exactly one is required: Collision energy and Collision energy unit or Electron energy and Electron energy unit.  

---

### Data source
A persistent identifier representing the contributors' affiliation.
- Set at the first contribution. 

Example in configuration file: 
```yaml
par_data_source: 'bfg'
```
[go back](#parameter-requirements)

---

### Authors
Contributor name(s).
- Names separated by `;` &rarr; `<FirstName LastName>; <FirstName LastName>;`

Example: 
```yaml
par_authors: 'Björn Ehlig; Kevin S. Jewell; Ole Lessmann; Arne Wick'
```

[go back](#parameter-requirements)

---

### Author affiliation
Full name of contributors affiliation.

Example in configuration file: 
```yaml
par_affiliation: 'Federal Institute of Hydrology (Bundesanstalt für Gewässerkunde), Koblenz, Germany'
```

[go back](#parameter-requirements)

---

### Compound name
Chemical name of the compound.

- The naming conventions are based on the entries in PubChem

Examples: 
```
Diclofenac
(2-dodecanoylamino-ethyl)-dimethyl-tetradecyl-ammonium
```

[go back](#parameter-requirements)

---

### Adducts and in-source fragments

Adduct ion notations can be directly provided via the precursor type parameter.

Examples:
```
Precursor_type: [M+NH4]+  # mzVault 2.3.64.0
Precursor_type: [M+NH4]+  # mzVault 2.3.45.15
MS$FOCUSED_ION: PRECURSOR_TYPE [M+H]+  # MassBank
```
As an alternative, adducts and in-source fragments can be indicated in the compound name by parsing the suffix after an underscore (`_`).
- **Adducts** follow the format `<CompoundName>_<AdductName>`
- **In-source fragments** follow the format `<CompoundName>_QF<number>`, 
where `<number>` is the nominal m/z value `QF` (Ger. **Quellenfragment** for "in-source fragment").

Examples:
```
Desmedipham_NH4
Diclofenac_QF250
Famoxadone_QF331
```
During processing, the extracted adduct names are converted into their corresponding ion notations.

Example: `CompoundName_NH4`
- Positive polarity: `[M+NH4]+`
- Negative polarity: `[M-NH4]-`

Ion notations of `[M+H]+` or `[M–H]–` are assumed when `<CompoundName>` is provided without `<AdductName>`.  

Example: `CompoundName`
- Positive polarity: `[M+H]+`
- Negative polarity: `[M-H]-`

Other special cases (examples below) that don't follow standard conventions can be indicated in the 
[configuration file](example_files/example_config.yaml).

| `<AdductName>` | Ion notation   |
|----------------|----------------|
| `cation`       | `[M]+`         |
| `Ethylamin`    | `[M+C2H7N+H]+` |
| `FA`           | `[M+HCOO-]-`   |
| `NaFA`         | `[M+NaCOO-]-`  |

Consequently, `CompoundName_FA` would lead to an adduct notation of `[M+HCOO-]-` instead of `[M+FA-]-` (negative polarity).

**Additional information**:  
- For MS<sup>2</sup> spectra of **special adducts** and **source fragments**, 
the associated entry must include the molecular formula, CAS number, SMILES code, and other metadata of the **neutral molecule**.
- For cations (`[M+]`), the SMILES code and the InChIKey are derived from the cation, i.e., the charged compound without its counterion.

[go back](#parameter-requirements)

---

### Compound class
Classification or use category of the compound.
- Multiple compound classes are separated by `;` or `,` &rarr; `<CompoundClass1>; <CompoundClass2>;`
- Need to match any of the existing compound classes defined in the CSL
- If left empty the default compound class will be `Uncategorized`

| Compound class          | Compound class                      |
|-------------------------|-------------------------------------|
| `Acaricide`             | `Personal_care_product`             |
| `Antimicrobial`         | `Pesticide`                         |
| `Biocide`               | `PFAS`                              |
| `Food_additive`         | `Pharmaceutical`                    |
| `Fungicide`             | `Pigment`                           |
| `Herbicide`             | `Rodenticide`                       |
| `Industrial_process`    | `Transformation_product-Metabolite` |
| `Insecticide`           | `Surrogate_standard`                |
| `Natural_product`       |                                     |

>Note: The compound class groups are planned to be reworked in the future.

[go back](#parameter-requirements)

---

### Compound formula
The molecular formula of the neutral compound.
- Standard Hill notation

Examples:
``` 
C14H11Cl2NO2
C16H16N2O4
```

[go back](#parameter-requirements)

---

### SMILES
Simplified Molecular Input Line Entry System (SMILES) string (canonical form).

Examples:
```
OC(Cc1c(Nc2c(Cl)cccc2Cl)cccc1)=O
CCOC(=O)Nc1cccc(c1)OC(=O)Nc2ccccc2
```

[go back](#parameter-requirements)

---

### InChIKey
Unique identifier for molecules, represented as hashed version of the International Chemical Identifier (InChI). 

There are several rules that need to be followed when defining the structure and therefore the InChIKey:
- If you are using the SMILES to generate the InChI, use the canonical SMILES
- If the molecule has one chiral center, we remove the stereorepresentation and represent both enantiomers with one entry (since this can not be distinguished with standard LC-HRMS/MS)
- If the molecule has two or more chiral centers, we keep the stereorepresentation, since diastereoisomers can (potentially) be distinguished by achiral phase HPLC 
<!-- paper: https://jcheminf.biomedcentral.com/articles/10.1186/s13321-018-0299-2 
 need better examples with structural formula of enantiomers and diastereomers and corresponding InChI-keys  -->
Examples:
``` 
WZJZMXBKUWKXTQ-UHFFFAOYSA-N
DCOPUUMXTXDBNB-UHFFFAOYSA-N
```

[go back](#parameter-requirements)

---

### CAS Registry Number
The Chemical Abstracts Service (CAS) registry number for the compound. 
- In the case of salts or hydrates, use the CAS number of the molecular ion or uncharged molecule

Examples:
``` 
15307-86-5
13684-56-5
```

[go back](#parameter-requirements)

---

### Instrument name and type
Instrument name and instrument type.
- Need to match the following whitelist: 

| Instrument name                  | Instrument type      |
|----------------------------------|----------------------|
| TripleTOF 5600 SCIEX             | LC-ESI-QTOF          |
| TripleTOF 6600 SCIEX             | LC-ESI-QTOF          |
| QExactive Thermo                 | LC-ESI-Orbitrap      |
| Agilent 6500 Series Q-TOF        | LC-ESI-QTOF          |
| TripleTOF X500R SCIEX            | LC-ESI-QTOF          |
| ZenoTOF 7600 SCIEX               | LC-ESI-QTOF          |
| Exploris 240 Thermo              | LC-ESI-Orbitrap      |
| Exploris 60K Thermo              | GC-EI-Orbitrap       |

- If no instrument type is provided, it will be matched automatically

[go back](#parameter-requirements)

---

### Ion mode
Mode of ionization.
- Format depends on the used export software

Example for each supported format:
```
IonMode: positive  # mzVault 2.3.64.0
IonMode: negative  # mzVault 2.3.64.0

MS:1000130|Positive scan  # mzVault 2.3.45.15
MS:1000130|Negative scan  # mzVault 2.3.45.15

>  <ION MODE>  # LibraryView 1.8
P
>  <ION MODE>  # LibraryView 1.8
N

AC$MASS_SPECTROMETRY: ION_MODE POSITIVE  # MassBank
AC$MASS_SPECTROMETRY: ION_MODE NEGATIVE  # MassBank
```

[go back](#parameter-requirements)

---

### Collision energy
Collision energy (CE) used for fragmentation.
- CE value can be `20` or `20.00`
- The collision energy spread will be calculated if multiple collision energies are provided
   + CE values separated by `,` (e.g., `20,30,40` or `20, 30, 40`)
   + CE values must be equidistant
- The CE unit is defined separately

[go back](#parameter-requirements)

---

### Collision energy unit
Collision energy unit. 
- Usually `V` for volts
- See [SOP_acquisition_spectra.md](SOP_acquisition_spectra.md) for more details

Example in configuration file: 
```yaml
par_ce_unit: 'V' 
```

[go back](#parameter-requirements)

---

### Collision type
Collision type description.
 + `HCD`: Fragmentation occurred in a higher-energy collisional dissociation (HCD) cell
 + `Q`: Fragmentation occurred in a quadrupole
 + `in-source`: Fragmentation occurred in the ion source (in-source fragmentation). Especially relevant for EI experiments.

Example in configuration file:
```yaml
par_col_type: 'HCD' 
```

[go back](#parameter-requirements)

---

### Ionization type
Ionization type (LC-MS interface).
 + `ESI`: Electrospray ionization
 + `APCI`: Atmospheric pressure chemical ionization
 + `APPI`: Atmospheric pressure photoionization
 + `EI`: Electron ionization
 + `CI`: Chemical ionization

Example in configuration file:
```yaml
par_ionization: 'ESI'
```

[go back](#parameter-requirements)

---

### Precursor m/z
Mass-to-charge ratio of the precursor ion selected for fragmentation (MS<sup>2</sup>).
If no ion was isolated before fragmentation (DIA), the precursor m/z is the m/z of the fragment ion with the highest intensity.
- Decimal separator: `.`

Example:
```
328.14312
```

[go back](#parameter-requirements)

---

### Isotopologue
Isotopologue description.
+ `monoisotopic`: All atoms are most abundant. The isotopologue with the highest abundance was isolated and fragmented.
+ `37Cl`: One Cl atom replaced with <sup>37</sup>Cl
+ `37Cl2`: Two Cl atoms replaced with <sup>37</sup>Cl
+ `37Cl81Br`: One Cl atom replaced with <sup>37</sup>Cl and one Br atom replaced with <sup>81</sup>Br
+ `polyisotopic`: All atoms are a mixture (the natural distribution) of isotopes. Relevant for DIA experiments.

Example: 
```yaml
par_isotope: 'monoisotopic' 
```

[go back](#parameter-requirements)

---

### Retention time
Retention time in minutes.
- Decimal separator: `.`

Examples:
```
12.24153
9.4
```

[go back](#parameter-requirements)

---

### Kovats retention index
Kovats retention index. Calculated for each compound based on the retention times of the n-alkanes in the same 
chromatographic run. Only relevant for GC data.
- Decimal separator: `.`

Examples:
```
1242.24153
908.4
```

[go back](#parameter-requirements)

---

### Electron energy
Kinetic energy of the electrons used for ionization in electron ionization (EI). Usually 70 eV.
- Value can be `70` or `70.00`
- The electron energy unit is defined separately

[go back](#parameter-requirements)

---

### Electron energy unit
Unit of the electron energy. 
- Usually `eV` for electron volts

Example in configuration file: 
```yaml
par_ce_unit: 'eV' 
```

[go back](#parameter-requirements)

---


### Spectrum
List of fragment peaks with m/z and intensity values.

- Decimal separator: `.`
- Format depends on the used export software
- MassBank with additional relative intensity values

Example for each supported format:
```
# mzVault 2.3.64.0
Num peaks: 3
74.0287 14613.86
136.0327 154562.81
152.0533 72739.36

# mzVault 2.3.45.15
MS:1009006|number of peaks = 4
77.0415 8.60
87.0463 6.90
91.0552 9.20
93.0713 14.20

# LibraryView 1.8
>  <NUM PEAKS>
5

>  <MASS SPECTRAL PEAKS>
66.011199999999999 5.3999999999999996
78.021500000000002 7.8000000000000004
89.012199999999999 9.2999999999999993
97.062299999999994 12.299999999999999
120.06249999999999 11.6

# MassBank
PK$NUM_PEAK: 12
PK$PEAK: m/z int. rel.int.
  39.0225 2.2 106
  41.0378 5.1 246
  43.0177 11.6 559
  55.0538 3.1 149
  65.0379 1.3 62
  67.053 1.9 91
  77.0376 10.1 487
  79.0534 4.8 231
  91.0533 20.7 999
  105.0693 8.6 415
  109.0639 7.2 347
  123.0795 1.5 72
```

[go back](#parameter-requirements)

---
