# Tools for the Collective Spectral Library (CSL)

## Name
csl-tools

## Description
Import, export, and curate spectral data for the Collective Spectral Library (CSL).

![Image](https://github.com/user-attachments/assets/0e511e6c-89d6-4f8c-9f45-81a549f0bdb5)

## Background
The Collective Spectral Library (CSL) is a database containing a collection of reference spectra generated using tandem 
mass spectrometry (MS²). 

The CSL is built collaboratively and currently includes reference spectra provided by:
- [Federal Institute of Hydrology](https://www.bafg.de) (Bundesanstalt für Gewässerkunde, BfG), Koblenz, Germany
- [Bavarian Environment Agency](https://www.lfu.bayern.de) (Bayerisches Landesamt für Umwelt, LfU Bayern), Augsburg, Germany
- [German Environment Agency](https://www.umweltbundesamt.de) (Umweltbundesamt, UBA), Berlin, Germany

The CSL enables retrospective screening of environmental samples as part of Non-Target Screening (NTS) efforts. 
It is integrated into the open analysis workflow [ntsworkflow](https://github.com/bafg-bund/ntsworkflow) <sup>[1]</sup>, 
which supports matching of experimental MS² data with verified reference spectra. It is also connected to 
[NTSPortal](https://ntsportal.bafg.de) <sup>[2]</sup>, a platform for processing, archiving and visualizing NTS data to 
support the identification and assessment of trace contaminants in surface waters.

We continuously expand the CSL to improve its utility, for instance in the retrospective analysis 
of historical data in NTSPortal <sup>[3]</sup>.

For more information or to contribute spectral reference data, check out the section [Contribution (spectral data)](#contribution-spectral-data)
and feel free to contact us at `ntsportal@bafg.de`.

The latest CSL file is available at: https://doi.org/10.5281/zenodo.16901589.

><sup>**[1]** Jewell, K. S., et al. (2020). Rapid Commun. Mass Spectrom., 34, e8541. [https://doi.org/10.1002/rcm.8541](https://doi.org/10.1002/rcm.8541)  
**[2]** Jewell, K. S., et al. (2025). Online-Portal „Non-Target Screening für die Umweltüberwachung der Zukunft“, Umweltbundesamt, Dessau-Roßlau. [https://www.umweltbundesamt.de/sites/default/files/medien/11850/publikationen/21_2025_texte.pdf](https://www.umweltbundesamt.de/sites/default/files/medien/11850/publikationen/21_2025_texte.pdf)  
**[3]** Lessmann, O., et al. (2025, May). Development and Application of a Collective Spectral Library for Collaborative Non-Target Screening [Poster presentation], Wasser 2025, Münster, Germany. [Poster Download](https://github.com/user-attachments/files/20883434/poster_wasser_lessmann.pdf)</sup>

## Installation
```
pip install git+https://github.com/bafg-bund/csl-tools.git
```

## Development
To contribute to the development or to run the project in development mode:
1. Clone the repository
    ```
    git clone https://github.com/bafg-bund/csl-tools.git
    cd csl-tools
    ```
2. Create and activate a virtual environment (recommended)

3. Install the package and dependencies in editable mode
    ```
    pip install -e .
    ```
4. Run tests
    ```
    pytest
    ```


## Contribution (source code)
If you run into issues or have ideas for improvement, feel free to contact us.

To make changes, please create a new branch and open a pull request to the `dev` branch.

## Contribution (spectral data)
To contribute spectral data to the CSL, please follow the linked guidelines for the respective file formats.  
Currently, the package can read:

- mzVault-based export files (_Thermo Fisher Scientific; Version 2.3 SP1; Build 2.3.64.0; July 8, 2021_) &#8594; [Requirements for MSP/NIST files](/docs/SOP_msp_nist_import.md)
- MassBank documents &#8594; Please refer to the official [MassBank documentation](https://github.com/MassBank/MassBank-web/blob/main/Documentation/MassBankRecordFormat.md)

In the future we plan to support the file format:
- SCIEX / LibraryView files (SDF format) 


## Usage
The package provides both a Command-Line Interface (CLI) and a Python API for operations on the CSL.  

After installation, you can run the CLI using:
```
csl <command> <arguments>
```
Alternatively, use the functions directly in Python:
```python
import csl
csl.export_data(...)
csl.process_data(...)
csl.scan_rt(...)
```

### Available commands:
- [process](#process) &#8594; Processing of MS2 data files.
- [export](#export) &#8594; Exporting the CSL in various formats.
- [rtscan](#rtscan) &#8594; Curation of retention time data.

You can either run the tools via terminal commands or import and run the corresponding functions in a Python script.


### `process`
Processes MS2 data files from a specified format and imports data into the CSL.
```
csl process <format> <path_csl> <path_data>
```

#### Arguments
- `format`: Specify import format. Choose from:
  - `mbank`: MassBank documents.
  - `lfuby`: LfU Bayern import format (ThermoFisher/mzVault).
  - `lubw` : LUBW import format (ThermoFisher/mzVault).
  - `lanuk`: LANUK import format (SCIEX/LibraryView) (not implemented).
- `path_csl`: Path to the CSL file.
- `path_data`: (Optional) Path to the data file or directory (Default: Opens dialog to select files)').

#### Examples
Process data from the Bavarian Environment Agency (LfU).
```
csl process lfuby path/to/CSL.db path/to/data.txt
```
```python
from csl import process_data
process_data(format='thermo', path_csl='path/to/CSL.db', path_data='path/to/data.txt')
```


### `export`
Exports the CSL to the specified format.  
```
csl export <format> <path_csl> <path_out> <subset>
```

#### Arguments
- `format`: Specify the export format. Choose from:
  - `thermo`: MSP/NIST export format (e.g., for importing to mzVault).
  - `envi`  : enviMass export format.
  - `mbank` : MassBank export format.
  - `sqlite`: SQLite export format (used to subset the CSL by a specific data source).
- `path_csl`: Path to the CSL file.
- `path_out`: Path to the directory where the exported file(s) will be saved.
- `subset`: (Optional) Data source(s) for subsetting the CSL data before exporting. Choose one or more from:
  - `bfg`: BfG (Federal Institute of Hydrology)
  - `lfuby`: LfU Bayern (Bavarian Environment Agency)
  - `uba`: UBA (German Environment Agency)
  - `all`: No subsetting (Default)

#### Example
Exports CSL-files from the data sources 'bfg' and 'uba' into the MSP/NIST format.
```
csl export thermo path/to/CSL.db path/to/output_dir bfg uba
```
```python
from csl import export_data
export_data(format='thermo', path_csl='path/to/CSL.db', path_out='path/to/output_dir', subset=['bfg', 'uba'])
```

Exports all CSL-files into the MSP/NIST format.
```
csl export thermo path/to/CSL.db path/to/output_dir
```
```python
from csl import export_data
export_data(format='thermo', path_csl='path/to/CSL.db', path_out='path/to/output_dir')
```

Exports CSL-files from the data source 'bfg' into the MassBank format.
```
csl export mbank path/to/CSL.db path/to/output_dir bfg
```
```python
from csl import export_data
export_data(format='mbank', path_csl='path/to/CSL.db', path_out='path/to/output_dir', subset='bfg')
```


### `rtscan`
Operates on retention-time data stored in the CSL.  
```
csl rtscan <operation> <path_csl>
```

#### Arguments
- `operation`: Specify the operation. Choose from:
  - `update`: Adds missing non-experimental retention times using available experimental data and corrects errors in associated entries in the CSL.
  - `recalc`: Recalculates and replaces all non-experimental retention times using available experimental data in the CSL (not yet implemented).
- `path_csl`: Path to CSL file.

#### Example
```
csl rtscan check path/to/CSL.db
```
```python
from csl import scan_rt
scan_rt(operation='update', path_csl='path/to/CSL.db')
```

### Notes
- For file paths with spaces, enclose them in quotes, e.g., `"C:\My Documents\data.msp"`.
- Use the --help/--h flag with any command to see additional usage information, e.g., `csl export --help`

## Authors
Ole Lessmann, BfG, lessmann@bafg.de  
Björn Ehlig, BfG, ehlig@bafg.de  
Kevin S. Jewell, BfG, jewell@bafg.de  

## License
Copyright 2025 Federal Institute of Hydrology (Bundesanstalt für Gewässerkunde).

This package is licensed under the [GNU General Public License v3.0](LICENSE).
