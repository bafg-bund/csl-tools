# Python package for the Collective Spectral Library (CSL)

## Name
csl-tools

## Description
Import, export and curation of spectral data for the Collective Spectral Library (CSL).

![Image](https://github.com/user-attachments/assets/0e511e6c-89d6-4f8c-9f45-81a549f0bdb5)

## Background
The CSL is a collection of spectral data (standards) that can be used by [ntsworkflow](https://github.com/bafg-bund/ntsworkflow) <sup>[1]</sup> to screen environmental data retrospectively and is integrated with [NTSPortal](https://ntsportal.bafg.de) <sup>[2]</sup>. 

Currently, the CSL holds data from these institutions:
- BfG (Federal Institute of Hydrology)
- LfU Bayern (Bavarian Environment Agency)
- UBA (Federal Environment Agency)

The newest CSL file is available at **(not yet uploaded)** and will be regularly updated there.

><sup>**[1]** K. S. Jewell et al., Rapid Commun. MassSpectrom. 2020, 34, e8541. [https://doi.org/10.1002/rcm.8541](https://doi.org/10.1002/rcm.8541)  
**[2]** K. S. Jewell et al., Online-Portal „Non-Target Screening für die Umweltüberwachung der Zukunft“, Umweltbundesamt, Dessau-Roßlau, 2025. [UBA report](https://www.umweltbundesamt.de/sites/default/files/medien/11850/publikationen/21_2025_texte.pdf)</sup>


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

[MSP/NIST files](/docs/SOP_import.md)

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
```bash
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
  - `recalc`: Re-calculates all non-experimental retention times based on available experimental data (not implemented).
- [csl_path]: Path to CSL file.

#### Example
```
csl rtscan update C:\path\to\csl.db
```

### Notes
- For file paths with spaces, enclose them in quotes, e.g., "C:\My Documents\data.msp".
- Use the --help/--h flag with any command to see additional usage information, e.g., `csl export --help`


## Authors and acknowledgments
Ole Lessmann, BfG, lessmann@bafg.de  
Björn Ehlig, BfG, ehlig@bafg.de  
Kevin S. Jewell, BfG, jewell@bafg.de  

## License
GPLv3

## Project status
_Under development_
