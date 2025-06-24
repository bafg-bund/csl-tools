# Import-file format documentation for contributors
This documentation applies to all contributor who wish to submit spectral data for inclusion in the **Collective Spectral Library (CSL)**. 
It describes the required format for submitting spectral data for successful processing and import using the **csl-tools** package.

**Table of Contents**
* [MSP/NIST Files](#mspnist-files)
  * [Parameter Reference Table](#parameter-reference-table)
    * [Compound name](#compound-name)
    * [Special adduct / Source fragment](#special-adduct--source-fragment)
      * [Additional information:](#additional-information)
    * [Precursor m/z](#precursor-mz)
    * [Collision energy (CE)](#collision-energy-ce)
    * [Ionization](#ionization)
    * [Ion mode](#ion-mode)
    * [Retention time](#retention-time)
    * [InChIKey](#inchikey)
    * [Compound formula](#compound-formula)
    * [CAS Registry Number](#cas-registry-number)
    * [SMILES code](#smiles-code)
    * [Compound class](#compound-class)
    * [Number of peaks](#number-of-peaks)
    * [Spectrum](#spectrum)
* [MassBank Files](#massbank-files)

# MSP/NIST Files
Default information that needs to be provided by the contributors separately:
- Authors
- License
- Method: 
   + Type of molecular mass (e.g., `monoisotopic`)
   + Collision type (e.g., `HCD`, `Q`)
   + Instrument type (e.g., `LC-ESI-Orbitrap`, `LC-ESI-QTOF`)
   + Instrument name (e.g., `TripleTOF 5600 SCIEX`, `QExactive`, `Agilent 6500 Series Q-TOF`)


## Parameter Reference Table
- Based on mzVault™ (_Thermo Fisher Scientific; Version 2.3 SP1; Build 2.3.64.0; July 8, 2021_)

| Parameter description             | Line identifier in file          | Required | Subsection                                                           |
|-----------------------------------|----------------------------------|-----|----------------------------------------------------------------------|
| Compound name                     | `Name`                           | Yes | [Compound name](#compound-name)                                      |
| Special adduct or source fragment | `Name`                           | No  | [Special adduct / Source fragment](#special-adduct--source-fragment) |
| Precursor m/z                     | `PrecursorMz`                    | Yes | [Precursor m/z](#precursor-mz)                                       |
| Collision energy                  | `Collision_energy`               | Yes | [Collision energy](#collision-energy)                                |
| Ionization                        | `Ionization`                     | Yes | [Ionization](#ionization)                                            |
| Ion mode                          | `IonMode`                        | Yes | [Ion mode](#ion-mode)                                                |
| Retention time                    | `RetentionTime`                  | Yes | [Retention time](#retention-time)                                    |
| InChIKey                          | `InChiKey`                       | Yes* | [InChIKey](#inchikey)                                                |
| Compound formula                  | `Formula`                        | Yes | [Compound formula](#compound-formula)                                |
| CAS Registry Number               | `CASNo`                          | Yes* | [CAS Registry Number](#cas-registry-number)                          |
| SMILES code                       | `Smiles`                         | Yes | [SMILES code](#smiles-code)                                          |
| Compound class / category         | `CompoundClass`                  | No  | [Compound class](#compound-class)                                    |
| Number of peaks                   | `Num peaks`                      | Yes | [Number of peaks](#number-of-peaks)                                  |
| Spectrum (m/z and intensity)      | Lines directly after `Num peaks` | Yes | [Spectrum](#spectrum)                                                |
<sup>*</sup> At least one of the following is required: InChIKey or CAS.


### Compound name
Chemical name of the compound.

Examples: 
```
Name: Diclofenac
Name: (2-dodecanoylamino-ethyl)-dimethyl-tetradecyl-ammonium
```

---

### Special adduct / Source fragment
Special adducts (i.e., not [M+H]+ or [M–H]–) and source fragments.

Special adducts and source fragments are indicated in the compound name by parsing the suffix after an underscore (`_`), 
where adducts follow the format `<CompoundName>_<AdductName>` and source fragments follow `<CompoundName>_QF<number>` 
with the nominal m/z as the number after "QF". 

Examples:
```
Name: Desmedipham_NH4
Name: Diclofenac_QF250
Name: Famoxadone_QF331
```

The extracted adduct names are then converted into their corresponding ion notations.

Example: `CompoundName_NH4`
- Positive polarity: `[M+NH4]+`
- Negative polarity: `[M-NH4]-`

Example: `CompoundName`
- Positive polarity: `[M+H]+`
- Negative polarity: `[M-H]-`

Some special cases don't follow standard conventions and are hardcoded:

| `<AdductName>` | Ion notation |
|----------------|---------------------------|
| `cation`       | `[M]+`                    |
| `Ethylamin`    | `[M+C2H7N+H]+`            |
| `FA`           | `[M+HCOO-]-`              |
| `NaFA`         | `[M+NaCOO-]-`             |


#### Additional information:
For MS2 spectra of **special adducts** and **source fragments**, 
the associated entry must include the molecular formula, CAS number, SMILES code, and other metadata of the **neutral molecule**.

For cations the SMILES code and the InChIKey are derived from the cation, i.e., the charged compound without its counterion.

---

### Precursor m/z
Mass-to-charge ratio of the precursor ion selected for fragmentation (MS2).


---

### Collision energy (CE)
Collision energy used for fragmentation.

- Can be written as `20` or `20.00`
- When using multiple CEs the order is important to determine the spread correctly: `20, 40, 60` and not `20, 60, 40`
- Multiple CEs must be equidistant. `20, 30, 50` can not be accepted.


---

### Ionization
Ionization method.

Example:
```
Ionization: ESI
```

---

### Ion mode
Mode of ionization.

- Either `positive` or `negative`

Examples:
````
IonMode: positive
IonMode: negative
````

---

### Retention time
Retention time in minutes.

Examples:
```
RetentionTime: 12.24153
RetentionTime: 9.4
```


---

### InChIKey
Unique identifier for molecules, represented as hashed version of the International Chemical Identifier (InChI).

Examples:
``` 
InChiKey: WZJZMXBKUWKXTQ-UHFFFAOYSA-N
InChiKey: DCOPUUMXTXDBNB-UHFFFAOYSA-N
```

---

### Compound formula
The molecular formula of the neutral compound, using standard Hill notation.

Examples:
``` 
Formula: C14H11Cl2NO2
Formula: C16H16N2O4
```

---

### CAS Registry Number
The Chemical Abstracts Service (CAS) registry number for the compound.

Examples:
``` 
CasNo: 15307-86-5
CASNo: 13684-56-5
```

---

### SMILES code
Simplified Molecular Input Line Entry System (SMILES) string.

Examples:
```
Smiles: OC(Cc1c(Nc2c(Cl)cccc2Cl)cccc1)=O
Smiles: CCOC(=O)Nc1cccc(c1)OC(=O)Nc2ccccc2
```


### Compound class
Classification or use category of the compound.

Examples:
``` 
CompoundClass: Pharmaceutical
CompoundClass: Herbicide;Pesticide
```

Currently, the following compound classes are defined in the CSL:

|    | Compound class                    |
|----|-----------------------------------|
| 1  | BfG                               |
| 2  | Pharmaceutical                    |
| 3  | Transformation_product            |
| 4  | Antimicrobial                     |
| 5  | Food_additive                     |
| 6  | Fungicide                         |
| 7  | Herbicide                         |
| 8  | Industrial_process                |
| 9  | Insecticide                       |
| 10 | Metabolite                        |
| 11 | Natural_product                   |
| 12 | Personal_care_product             |
| 13 | Pesticide                         |
| 14 | LfU                               |
| 15 | Pigment                           |
| 16 | Surrogate_standard                |
| 17 | Diclofenac-lactam                 |
| 18 | UBA                               |
| 19 | Acaricide                         |
| 20 | Biocide                           |
| 21 | Nitrification_inhibitor           |
| 22 | PFAS                              |
| 23 | Research                          |
| 24 | Rodenticide                       |
| 25 | Transformation_product-Metabolite |
| 26 | Urease_inhibitor                  |

---

### Number of peaks
Number of present fragment peaks.

Example:
``` 
Num peaks: 5
```

---

### Spectrum
List of fragment peaks with m/z and intensity values.

- Directly follows the line after `Num peaks`

Examples:
```
Num peaks: 3
74.0287 14613.86
136.0327 154562.81
152.0533 72739.36

Num peaks: 5
22.0556 965.43
31.0234 13067.11
69.2785 465.98
98.4724 1169.04
122.8026 1769.46
```

---

# MassBank Files

~

---
