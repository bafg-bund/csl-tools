# Python package for the Collective Spectral Library (CSL)

## Name
py-csl

## Description
Import, export and curation of spectral data for the Collective Spectral Library (CSL).

## Installation
1. Clone the GitLab repository to your local computer (with HTTPS)  
   - Open a terminal in the directory where you want to clone the project
   - Run the following command to clone the repository:   
   `git clone https://gitlab.lan.bafg.de/nts/collective-spectral-library.git`
   - Enter your GitLab username and password when prompted  
   
   More help: [Clone a Git repository to your local computer](https://docs.gitlab.com/ee/topics/git/clone.html)
2. Set up virtual environment
   - Navigate to project directory
   - Create a virtual environment in the project root:  
   `python -m venv .venv`
   - Alternatively, use your IDE (e.g. PyCharm) to set up the virtual environment: 
   1. File - Open - Select project directory - Ok
   2. Settings - Project - Python Interpreter - Add Interpreter - Add Local Interpreter - 
   Virtualenv Environment - Environment: _New_ - Location: _Select Project root directory_ - 
   Base interpreter: _Select installed python interpreter; e.g.: Python 3.12 C:/Python312/python.exe_ - Ok   
   - Confirm that the environment is active by checking the terminal for a `(.venv)` prefix
   
   More help: [Configure a virtualenv environment with PyCharm](https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html)
3. Install dependencies
   - Install the package and its dependencies in editable mode for development:  
   `pip install -e .`
   - Re-run this command after pulling updates
   > Editable mode: Changes to the code are reflected directly in the installed package, making development and testing easier.

## Update package
To update the package to the latest version follow these steps:
1. Navigate to the project directory  
`cd /path/to/collective-spectral-library`
2. Pull the latest changes from the remote repository:  
`git pull`
3. Update dependencies (if necessary):  
`pip install -e .`

## Issues / Ideas / Code changes
If you run into issues or have ideas for improvement, 
please create a GitLab Issue in the Wiki [Issue-Board](https://gitlab.lan.bafg.de/nts/collective-spectral-library/-/boards)  

If you need to make changes to the code, please do not directly modify the main branch and push your changes. 
Instead, create a new branch for your work.

For detailed instructions on creating and managing branches, refer to the GitLab documentation:
[GitLab Branches Documentation](https://docs.gitlab.com/ee/user/project/repository/branches/)

## Usage
The main.py script is the main entry point for the Collective Spectral Library (CSL) Operations Program. 
It provides a Command-Line Interface (CLI) for processing MS2 data files, exporting the CSL in various formats, 
and curation of retention time data.

### General Syntax

```bash
python main.py [command] [options]
```

### Commands:  

### `process`
Processes MS2 data files from a specified format (currently institutions) and imports data into the CSL.
```bash
python main.py process [institution] [data_path] [--csl_path <path>]
```

#### Arguments
- [institutions]: Choose from `lfuby`, `bfg`, `lubw`, `uba`, `lanuv`.  
(Currently only `lfuby` and `lubw` working)
- [data_path]: (Optional) Path to data file or directory (Default: Opens dialog to select files)').
- [--csl_path _path_]: (Optional) Path to CSL file (Default: Specified in `config.py`).

#### Example
```bash
python main.py process lubw C:\path\to\data.msp --csl_path C:\path\to\csl.db
```

### `export`
Exports the CSL to a specified format.  
```bash
python main.py export [format] [out_path] [csl_path]
```

#### Arguments
- [format]: Specify the export format. Choose from `txt`, `envi`, `mbank` (Needs to be updated)
- [out_path]: Path to the directory where the exported file will be saved.
- [csl_path]: (Optional) Path to CSL file (Default: Specified in `config.py`).

#### Example
```bash
python main.py export txt C:\path\to\output_dir C:\path\to\csl.db
```

### `rtscan`
 Operates on retention time stored in the CSL.  
```bash
python main.py rtscan [operation] [csl_path]
```

#### Arguments
- [operation]: Specify the operation. Choose from:
  - `check`: Checks the consistency of non-experimental retention time data. (not implemented)
  - `update`: Calculates missing non-experimental retention times based on available experimental data.
  - `recalc`: Re-calculates all non-experimental retention times based on available experimental data. (not implemented)
- [csl_path]: (Optional) Path to CSL file (Default: Specified in `config.py`).

#### Example
```bash
python main.py rtscan update C:\path\to\csl.db
```

### Notes
- For file paths with spaces, enclose them in quotes, e.g., "C:\My Documents\data.msp".
- Use the --help/--h flag with any command to see additional usage information: `python main.py [command] --help`

## Roadmap

Planned for release v0.1:
- Import LfU (mzVault/ThermoFisher) -> done
- Import LUBW (mzVault/ThermoFisher) -> testing
- Import MassBank documents
- Modeling and correction of retention times -> done
- Export MSP documents (mzVault/ThermoFisher)

Planned for future release:
- Export enviMass "target list"
- Import LibraryView documents (SCIEX)


## Contributing with spectral data
Todo: Add SOPs for formats of spectral data files

## Authors and acknowledgments
Ole Lessmann, BfG, lessmann@bafg.de  
Björn Ehlig, BfG, ehlig@bafg.de  
Kevin Jewell, BfG, jewell@bafg.de  

## License
Todo

## Project status
_Under development_
