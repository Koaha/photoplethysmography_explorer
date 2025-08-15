"""
File handling utilities for the PPG analysis tool.

This module provides functions for efficient file operations including:
- Quick row counting without loading entire files
- Column extraction for CSV files
- Handling of uploaded CSV content
- Windowed data reading for large datasets
- Automatic file detection
"""

import base64
import tempfile
from pathlib import Path

import pandas as pd


def count_rows_quick(path):
    """
    Quickly count rows in a CSV file without loading data into memory.

    This function reads the file line by line to count rows, which is
    much more memory-efficient than loading the entire file for large datasets.

    Args:
        path (str): Path to the CSV file

    Returns:
        int: Number of data rows (excluding header)

    Note:
        Returns max(0, total_lines - 1) to account for header row
    """
    with open(path, "rb") as f:
        total_lines = sum(1 for _ in f)
    return max(0, total_lines - 1)


def get_columns_only(path):
    """
    Get column names from a CSV file without loading data.

    This function reads only the header row to extract column names,
    making it efficient for large files where only column information is needed.

    Args:
        path (str): Path to the CSV file

    Returns:
        list: List of column names as strings
    """
    return list(pd.read_csv(path, nrows=0).columns)


def parse_uploaded_csv_to_temp(contents, filename):
    """
    Parse uploaded CSV content and save to temporary file.

    This function handles base64-encoded CSV content from web uploads
    and creates a temporary file for processing. The temporary file
    is automatically cleaned up by the system.

    Args:
        contents (str): Base64 encoded CSV content with data URL prefix
        filename (str): Original filename for determining file extension

    Returns:
        str: Path to the temporary file, or None if contents is empty

    Note:
        The temporary file will have a prefix "ppg_" and appropriate suffix
        based on the original filename extension.
    """
    if not contents:
        return None

    # Parse base64 content and decode
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    # Determine file extension
    suffix = ".csv" if not filename else f".{filename.split('.')[-1]}"

    # Create temporary file
    fd, tmp_path = tempfile.mkstemp(prefix="ppg_", suffix=suffix)
    with open(tmp_path, "wb") as f:
        f.write(decoded)

    return tmp_path


def read_window(path, cols, start_row, end_row):
    """
    Read a specific window of rows from a CSV file.

    This function efficiently reads only a subset of rows from a large CSV file,
    making it suitable for handling datasets that don't fit in memory.

    Args:
        path (str): Path to the CSV file
        cols (list): List of column names to read
        start_row (int): Starting row index (0-based, excluding header)
        end_row (int): Ending row index (inclusive, excluding header)

    Returns:
        pandas.DataFrame: DataFrame containing the specified window of data

    Note:
        - Row indices are 0-based but exclude the header row
        - The function automatically handles header skipping
        - Returns empty DataFrame if start_row > end_row
    """
    start_row = max(0, int(start_row))
    end_row = max(start_row, int(end_row))
    nrows = end_row - start_row + 1

    # Skip header and rows before start_row
    skip = range(1, 1 + start_row) if start_row > 0 else None

    return pd.read_csv(path, usecols=cols, skiprows=skip, nrows=nrows)


def get_auto_file_path(default_filename):
    """
    Get auto-file path if it exists in the current directory.

    This function checks if a default file exists and returns its resolved path.
    Useful for automatically loading common data files without user intervention.

    Args:
        default_filename (str): Default filename to look for

    Returns:
        str: Resolved absolute path to the file if it exists, None otherwise
    """
    path = Path(default_filename)
    if path.exists():
        return str(path.resolve())
    return None


def get_default_sample_data_path():
    """
    Get the path to the default sample data file.

    This function returns the path to the toy_PPG_data.csv file in the sample_data
    directory, which serves as a default dataset for users to explore the tool.

    Returns:
        str: Resolved absolute path to sample_data/toy_PPG_data.csv if it exists, None otherwise
    """
    # Try to find the sample data file
    sample_path = Path("sample_data/toy_PPG_data.csv")
    if sample_path.exists():
        return str(sample_path.resolve())

    # Fallback: try relative to current working directory
    sample_path = Path.cwd() / "sample_data" / "toy_PPG_data.csv"
    if sample_path.exists():
        return str(sample_path.resolve())

    # Fallback: try relative to the script location
    script_dir = Path(__file__).parent.parent.parent
    sample_path = script_dir / "sample_data" / "toy_PPG_data.csv"
    if sample_path.exists():
        return str(sample_path.resolve())

    return None
