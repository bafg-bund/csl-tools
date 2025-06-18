# """
# Main entry point for the CSL Operations Program.
#
# This script provides command-line interface options for processing and importing MS2 data files from various
# formats and exporting the Collective Spectral Library (CSL) in different formats.
#
# Commands:
#     process : Processes MS2 data files based on the format and imports the data into the CSL database.
#     export  : Exports the CSL to the specified formats.
#     rtscan  : Operates on retention time data saved in the CSL.
#
# Usage:
#     python main.py <command> [options]
# """

from argparse import ArgumentParser, Namespace
from csl.main_functions.process import run_process_workflow
from csl.main_functions.export import run_export_workflow
from csl.main_functions.rtscan import run_rtscan_workflow
from tkinter import Tk
from tkinter.filedialog import askopenfilenames


def select_data_files():
    """Opens a file dialog to select one or more files."""
    root = Tk()
    root.withdraw()  # Hide the root window
    fpaths = askopenfilenames(title="Select one or more data files")
    root.destroy()
    return list(fpaths)


# Prepare the argument parser
parser = ArgumentParser(
    usage='python main.py <command> [options]',
    description='This program handles operations associated with the Collective Spectral Library (CSL).'
)

# Add subparsers to define various commands
subparsers = parser.add_subparsers(dest='command', help='Available commands')

# Define 'process' command and its arguments
process_parser = subparsers.add_parser('process', help='Processes MS2 data files from a specified format and imports the data into the CSL')

process_parser.add_argument('format', type=str, choices=['mbank', 'lfuby', 'lanuk', 'lubw'],  # Todo: change format to thermo and sciex
                            help='Specify format')
process_parser.add_argument('csl_path', type=str,
                            help='Path to CSL file')
process_parser.add_argument('data_path', type=str, nargs='?',
                            help='(Optional) Path to data file or directory (Default: Opens dialog to select files)')


# Define 'export' command and its arguments
export_parser = subparsers.add_parser('export', help='Exports the CSL to various formats')
export_parser.add_argument('format', type=str, choices=['thermo', 'envi', 'mbank'],
                           help='Specify export format',)
export_parser.add_argument('csl_path', type=str,
                           help='Path to CSL file')
export_parser.add_argument('out_path', type=str, help='Path to the directory where the exported file will be saved. '
                                                      'For mbank format: Use path of local clone of '
                                                      'https://github.com/MassBank/MassBank-data/tree/dev/BAFG '
                                                      'to check the existing MassBank ACCESSION strings from file names.')
export_parser.add_argument('subset', type=str, nargs='?', choices=['lfuby', 'bfg', 'uba', 'lanuk', 'lubw', 'all'],
                            default= 'all', help='(Optional) Data source (institution) for subsetting the CSL data '
                                                 'before exporting (choices: lfuby, bfg, uba, lanuk, lubw, all; '
                                                 'Default: all)')

# Define 'rtscan' command and its arguments
rtscan_parser = subparsers.add_parser('rtscan', help='Operates on retention time data saved in the CSL')  # todo descr
rtscan_parser.add_argument('operation', type=str, choices=['check', 'update', 'recalc'],
                           help='Specify operation type',)  # todo: where to describe each option?
rtscan_parser.add_argument('csl_path', type=str,
                           help='Path to CSL file')

def main():
    # Parse the command-line arguments
    args: Namespace = parser.parse_args()

    # Execute functions based on the command type
    if args.command == 'process':
        if not args.data_path:
            file_paths = select_data_files()
            if not file_paths:
                print("No files selected. Exiting.")
                exit(1)
            args.data_path = file_paths
        run_process_workflow(args.format, args.csl_path, args.data_path)

    elif args.command == 'export':
        run_export_workflow(args.format, args.csl_path, args.out_path, args.subset)

    elif args.command == 'rtscan':
        run_rtscan_workflow(args.operation, args.csl_path)

if __name__ == "__main__":
    main()
