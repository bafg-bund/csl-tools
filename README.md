# Python package for the Collective Spectral Library (CSL)

## Name
csl-tools

## Description
Import, export and curation of spectral data for the Collective Spectral Library (CSL).

![Image](https://github.com/user-attachments/assets/0e511e6c-89d6-4f8c-9f45-81a549f0bdb5)

## Background
The CSL is a collection of spectral data (standards) that can be used by [ntsworkflow](https://github.com/bafg-bund/ntsworkflow) <sup>[1]</sup> to screen environmental data retrospectively and is integrated with [NTSPortal](https://ntsportal.bafg.de) <sup>[2]</sup>. 

Our goal is to grow this collection, making the retrospective analysis of historical data in NTSPortal more powerful and valuable for all users <sup>[3]</sup>.

If you wish to contribute spectral data, please see the section [Contribution (spectral data)](#contributing-spectral-data).

Currently, the CSL holds data from these institutions:
- [BfG](https://www.bafg.de) (Federal Institute of Hydrology)
- [LfU Bayern](https://www.lfu.bayern.de) (Bavarian Environment Agency)
- [UBA](https://www.umweltbundesamt.de) (Federal Environment Agency)

The most recent CSL file is available at **(will be uploaded to an open repository soon)** and will be regularly updated there.

><sup>**[1]** Jewell, K. S., et al. (2020). Rapid Commun. Mass Spectrom., 34, e8541. [https://doi.org/10.1002/rcm.8541](https://doi.org/10.1002/rcm.8541)  
**[2]** Jewell, K. S., et al. (2025). Online-Portal „Non-Target Screening für die Umweltüberwachung der Zukunft“, Umweltbundesamt, Dessau-Roßlau. [https://www.umweltbundesamt.de/sites/default/files/medien/11850/publikationen/21_2025_texte.pdf](https://www.umweltbundesamt.de/sites/default/files/medien/11850/publikationen/21_2025_texte.pdf)  
**[3]** Lessmann, O., et al. (2025, May). Development and Application of a Collective Spectral Library for Collaborative Non-Target Screening [Poster presentation], Wasser 2025, Münster, Germany. [Poster Download](https://github.com/user-attachments/files/20883434/poster_wasser_lessmann.pdf)</sup>

## Installation
```
pip install git+https://github.com/bafg-bund/csl-tools.git
```

## Development
To contribute or run the project in development mode:
1. Clone the repository
    ```
    git clone https://github.com/bafg-bund/csl-tools.git
    cd csl-tools
    ```
2. Create and activate a virtual environment (recommended)
   ```
   python -m venv .venv
   ```
    If using default command prompt (cmd):
    ```
    .\venv\Scripts\activate
    ```
    If using Windows PowerShell (PS):
    ```
    .\venv\Scripts\Activate.ps1
    ```
3. Install in editable mode
    ```
    pip install -e .
    ```
4. Run tests
    ```
    pytest
    ```
 

## Contribution (source code)
If you run into issues or have ideas for improvement, feel free to contact us.

If you want to make changes to the code, please do not directly push into the main branch. 
Instead, create a new branch for your work and open a pull request to the `dev` branch.

## Contributing (spectral data)
To contribute spectral data to the CSL, please follow the linked guidelines for the respective file formats.  
Currently, the package can read:

- mzVault-based export files (_Thermo Fisher Scientific; Version 2.3 SP1; Build 2.3.64.0; July 8, 2021_) &#8594; [Requirements for MSP/NIST files](/docs/SOP_msp_nist_import.md)
- MassBank documents &#8594; Please refer to the official [MassBank documentation](https://github.com/MassBank/MassBank-web/blob/main/Documentation/MassBankRecordFormat.md)

In the future we plan to support the file format:
- SCIEX / LibraryView files (SDF format) 


## Usage
The package provides both a Command-Line Interface (CLI) and Python API for operations on the CSL.

After installing the package, you can run the CLI using:
```
csl [command] [options]
```
During development, the CLI can also be run directly via:
```
python main.py [command] [options]
```

### Available commands:
- [process](#process) &#8594; Processing of MS2 data files.
- [export](#export) &#8594; Exporting the CSL in various formats.
- [rtscan](#rtscan) &#8594; Curation of retention time data.

You can either run the tools via terminal commands or import and run the corresponding functions in a Python script.


### `process`
Processes MS2 data files from a specified format and imports data into the CSL.
```
csl process [format] [csl_path] [data_path]
```

#### Arguments
- [format]: Specify import format. Choose from:
  - `mbank`: MassBank documents.
  - `lfuby`: LfU Bayern import format (ThermoFisher/mzVault).
  - `lubw`: LUBW import format (ThermoFisher/mzVault).
  - `lanuk`: LANUK import format (SCIEX/LibraryView) (not implemented).
- [csl_path]: Path to the CSL file.
- [data_path]: (Optional) Path to the data file or directory (Default: Opens dialog to select files)').

#### Examples
Process data from the Bavarian Environment Agency (LfU).
```
csl process lfuby C:\path\to\csl.db C:\path\to\data.txt 
```

### `export`
Exports the CSL to the specified format.  
```
csl export [format] [csl_path] [out_path]
```

#### Arguments
- [format]: Specify the export format. Choose from:
  - `thermo`: MSP/NIST export format (e.g., for mzVault).
  - `envi`: enviMass export format.
  - `mbank`: MassBank export format.
- [csl_path]: Path to the CSL file.
- [out_path]: Path to the directory where the exported file(s) will be saved.
- [subset]: (Optional) Data source (institution) for subsetting the CSL data before exporting. Choose from:
  - `bfg`: BfG (Federal Institute of Hydrology)
  - `lfuby`: LfU Bayern (Bavarian Environment Agency)
  - `uba`: UBA (Federal Environment Agency)
  - `lubw`: LUBW (Baden-Württemberg State Institute for the Environment)
  - `lanuk`: LANUK (North Rhine-Westphalia Office of Nature, Environment and Climate) 
  - `all`: No subsetting (Default) 


#### Example
Exports all BfG-files from the CSL into the MassBank format.
```
csl export mbank C:\path\to\csl.db C:\path\to\output_dir bfg
```

Exports all files from the CSL into the MSP/NIST format.
```
csl export thermo C:\path\to\csl.db C:\path\to\output_dir
```


### `rtscan`
 Operates on retention-time data stored in the CSL.  
```
csl rtscan [operation] [csl_path]
```

#### Arguments
- [operation]: Specify the operation. Choose from:
  - `update`: Calculates missing non-experimental retention times based on available experimental data (currently broken).
  - `recalc`: Re-calculates all non-experimental retention times based on available experimental data (not implemented yet).
- [csl_path]: Path to CSL file.

#### Example
```
csl rtscan update C:\path\to\csl.db
```

### Notes
- For file paths with spaces, enclose them in quotes, e.g., "C:\My Documents\data.msp".
- Use the --help/--h flag with any command to see additional usage information, e.g., `csl export --help`

## Authors
Ole Lessmann, BfG, lessmann@bafg.de  
Björn Ehlig, BfG, ehlig@bafg.de  
Kevin S. Jewell, BfG, jewell@bafg.de  

## License
This package is licensed under the [GNU General Public License v3.0](LICENSE).
