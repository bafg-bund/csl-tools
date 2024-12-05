# Collective Spectral Library (CSL)

## Collaborate with your team

- [ ] [Invite team members and collaborators](https://docs.gitlab.com/ee/user/project/members/)
- [ ] [Create a new merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
- [ ] [Automatically close issues from merge requests](https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
- [ ] [Enable merge request approvals](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
- [ ] [Set auto-merge](https://docs.gitlab.com/ee/user/project/merge_requests/merge_when_pipeline_succeeds.html)


***

## Name
csl (Collective Spectral Library)

## Description
Import, export and curation of spectral data for the Collective Spectral Library (CSL).

## Installation
1. Clone the repository
2. Create virtual environment with `python -m venv .venv` or manually set up virtual environment in the settings 
   (https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html#new-virtual-environment)
3. Install all dependencies in editable mode (for development) with `pip install -e .`
   This allows for testing of the package during development, as code changes are directly reflected 
   in the installed package (package installed in .venv points at code).

## Usage
main.py is the entry point of the package. Run commands in the terminal.

Examples:

Process spectral data of LfU Bayern (format type)
```bash
python main.py process lfuby
```

Export all CSL entries to a Massbank document format
```bash
python main.py export mbank
```

Check all retention times of CSL entries and fill any missing values 
(if data for modeling is available)
```bash
python main.py rtscan update
```

## Roadmap

Planned for release v0.1:
- Import LfU (mzVault/ThermoFisher) -> done
- Import LUBW (mzVault/ThermoFisher) -> needs testing
- Import MassBank documents
- Modeling and correction of retention times -> done
- Export MSP documents (mzVault/ThermoFisher)

Planned for future release:
- Export enviMass "target list"
- Import LibraryView documents (SCIEX)


## Contributing

- SOPs for formats of spectral data files

## Authors and acknowledgment
Ole Lessmann, BfG, lessmann@bafg.de
Björn Ehlig, BfG, ehlig@bafg.de
Kevin Jewell, BfG, jewell@bafg.de

## License


## Project status
_Under development_