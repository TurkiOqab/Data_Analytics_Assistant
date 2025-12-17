"""Dataset handler for loading and validating datasets."""

import os
from pathlib import Path

import pandas as pd

from .config import SUPPORTED_EXTENSIONS


class DatasetError(Exception):
    """Custom exception for dataset-related errors."""
    pass


def load_dataset(file_path: str) -> pd.DataFrame:
    """
    Load a dataset from a file path.

    Supports CSV, Excel (.xlsx, .xls), and JSON files.

    Args:
        file_path: Path to the dataset file.

    Returns:
        A pandas DataFrame containing the dataset.

    Raises:
        DatasetError: If the file doesn't exist, has an unsupported extension,
                     or cannot be parsed.
    """
    path = Path(file_path)

    # Check if file exists
    if not path.exists():
        raise DatasetError(f"File not found: {file_path}")

    # Check file extension
    extension = path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(SUPPORTED_EXTENSIONS.keys())
        raise DatasetError(
            f"Unsupported file type: {extension}. "
            f"Supported types: {supported}"
        )

    file_type = SUPPORTED_EXTENSIONS[extension]

    try:
        if file_type == "csv":
            # Try different encodings for CSV files
            for encoding in ["utf-8", "latin-1", "cp1252"]:
                try:
                    return pd.read_csv(file_path, encoding=encoding)
                except UnicodeDecodeError:
                    continue
            # If all encodings fail, try with error handling
            return pd.read_csv(file_path, encoding="utf-8", errors="replace")

        elif file_type == "excel":
            return pd.read_excel(file_path)

        elif file_type == "json":
            return pd.read_json(file_path)

    except Exception as e:
        raise DatasetError(f"Failed to parse file: {str(e)}") from e


def get_file_info(file_path: str) -> dict:
    """
    Get basic file information.

    Args:
        file_path: Path to the file.

    Returns:
        Dictionary with file name, size, and extension.
    """
    path = Path(file_path)
    return {
        "name": path.name,
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "extension": path.suffix.lower(),
    }
