"""
File Utilities Module.

This module provides general utilities for handling file operations.
"""


def validate_file_path(fpath):
    """
    Validates if a file exists at the specified path. If the file does not exist, it raises a `FileNotFoundError`.

    Args:
        fpath (str) : Path to the file for validation.
    """
    import os.path
    if not os.path.exists(fpath):
        raise FileNotFoundError(f"File at {fpath} does not exist.")


def update_version_filename(filename, update_type):
    """
    Updates the filename based on update type and current year.
    The filename needs to contain the version identifier 'v' and a version number ('year.major.minor')
    (the minor release can be dropped).
    Depending on the update type, the major or minor release number is updated by 1.
    Examples:
        - CSL_v24.1.db
        - CSL_v25.0.3.db

    Args:
        filename (string)    : Current filename.
        update_type (string) : Possible release types: 'major', 'minor'.

    Returns:
        updated_filename (string) : Updated filename.
    """
    import re
    from datetime import datetime
    import os

    # Make sure it's the basename
    filename = os.path.basename(filename)

    # Extract the version number
    version_pattern = r"CSL_v(\d+)\.(\d+)(?:\.(\d+))?.db"
    match = re.match(version_pattern, filename)

    if match:
        year_version = int(match.group(1))
        major_version = int(match.group(2))
        minor_version = match.group(3)  # Might be None

        # Determine next version
        current_year = datetime.now().strftime("%y")
        if year_version != current_year:
            year_version = current_year
            major_version = 0
            if minor_version is not None:
                minor_version = None
        elif year_version == current_year and update_type == 'major':
            major_version += 1  # Increment major version
            minor_version = None  # Reset minor version
        elif year_version == current_year and update_type == 'minor':
            if minor_version is not None:
                minor_version = int(minor_version) + 1  # Increment minor version
            else:
                minor_version = 1  # Was None before

        # Assemble version string
        new_version = f"{year_version}.{major_version}"
        if minor_version is not None:
            new_version += f".{minor_version}"

        updated_filename = f'CSL_v{new_version}.db'

    else:  # If the version number couldn't be recognized
        updated_filename = \
            f'{os.path.splitext(filename)[0]}_{update_type}_edit{os.path.splitext(filename)[-1]}'

    return updated_filename


def get_csl_version(csl_path):
    """Extracts the CSL version from the file path of the CSL."""
    import os
    import re

    # Make sure it's the basename
    filename = os.path.basename(csl_path)

    # Extract the CSL version number
    version_pattern = r"^.*CSL_v(?P<version>\d+(?:\.\d+)*)(?=[-_a-zA-Z]|\.db).*\.db$"
    match = re.match(version_pattern, filename)

    if match:
        csl_version = match.group(1)
    else:
        raise ValueError(f"Filename '{filename}' does not match the expected pattern 'CSL_v<version>.db'.")

    return csl_version
