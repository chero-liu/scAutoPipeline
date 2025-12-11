import os
import re
from typing import Dict, List, Optional, Pattern
from pathlib import Path


def scan_fastq_files(
    base_path: str, pattern_map: Optional[Dict[str, Pattern]] = None
) -> Dict[str, Dict[str, str]]:
    """
    Scan a directory structure for fastq files organized by sample folders.

    This function traverses the given base path, identifies all immediate subdirectories
    as sample folders, and within each sample folder, matches fastq files according
    to predefined patterns for cDNA and oligo fastq pairs.

    Parameters
    ----------
    base_path : str
        The root directory path containing sample folders.
        Example: '/nas/projects/scrna/standard_analysis/c4/KSXY-TJQK-DO25112701-1/data/20251204'

    pattern_map : Dict[str, Pattern], optional
        A dictionary mapping file type keys to compiled regex patterns.
        If not provided, uses default patterns for:
        - 'cDNAfastq1': Matches S[CN]C.*_1\\.f(?:ast)?q(?:\\.gz)?$
        - 'cDNAfastq2': Matches S[CN]C.*_2\\.f(?:ast)?q(?:\\.gz)?$
        - 'oligofastq1': Matches S[CN]O.*_1\\.f(?:ast)?q(?:\\.gz)?$
        - 'oligofastq2': Matches S[CN]O.*_2\\.f(?:ast)?q(?:\\.gz)?$

    Returns
    -------
    Dict[str, Dict[str, str]]
        A dictionary where:
        - Keys are sample folder names
        - Values are dictionaries with keys 'cDNAfastq1', 'cDNAfastq2',
          'oligofastq1', 'oligofastq2' mapping to file paths.
        If a file type is not found in a sample folder, its value will be an empty string.

    Raises
    ------
    ValueError
        If base_path does not exist or is not a directory.

    Examples
    --------
    >>> result = scan_fastq_files('/path/to/data')
    >>> result['sample1']['cDNAfastq1']
    '/path/to/data/sample1/SCC_sample1_1.fastq.gz'

    Notes
    -----
    - The function only scans immediate subdirectories of base_path.
    - File matching is case-sensitive.
    - If multiple files match a pattern in a folder, the first match is used.
    - The function logs warnings for missing file types but doesn't raise exceptions.
    """
    # Convert to Path object for better path handling
    base_dir = Path(base_path)

    # Validate input path
    if not base_dir.exists():
        raise ValueError(f"Base path does not exist: {base_path}")
    if not base_dir.is_dir():
        raise ValueError(f"Base path is not a directory: {base_path}")

    # Default patterns if not provided
    if pattern_map is None:
        pattern_map = {
            "cDNAfastq1": re.compile(r"S[CN]C.*_1\.f(?:ast)?q(?:\.gz)?$"),
            "cDNAfastq2": re.compile(r"S[CN]C.*_2\.f(?:ast)?q(?:\.gz)?$"),
            "oligofastq1": re.compile(r"S[CN]O.*_1\.f(?:ast)?q(?:\.gz)?$"),
            "oligofastq2": re.compile(r"S[CN]O.*_2\.f(?:ast)?q(?:\.gz)?$"),
        }

    # Expected file types
    file_types = ["cDNAfastq1", "cDNAfastq2", "oligofastq1", "oligofastq2"]

    result = {}

    # Iterate over immediate subdirectories
    for item in base_dir.iterdir():
        if item.is_dir():
            sample_name = item.name
            sample_files = {ft: "" for ft in file_types}

            # Scan files in the sample directory
            for file_path in item.iterdir():
                if file_path.is_file():
                    file_name = file_path.name

                    # Try to match against each pattern
                    for file_type, pattern in pattern_map.items():
                        if pattern.match(file_name):
                            # Use absolute path for consistency
                            sample_files[file_type] = str(file_path.absolute())
                            break  # A file can only match one pattern

            result[sample_name] = sample_files

    return result


def validate_fastq_structure(
    sample_dict: Dict[str, Dict[str, str]], required_types: Optional[List[str]] = None
) -> Dict[str, List[str]]:
    """
    Validate the structure of scanned fastq files.

    Parameters
    ----------
    sample_dict : Dict[str, Dict[str, str]]
        The dictionary returned by scan_fastq_files.

    required_types : List[str], optional
        List of file types that are required for each sample.
        Default: ['cDNAfastq1', 'cDNAfastq2', 'oligofastq1', 'oligofastq2']

    Returns
    -------
    Dict[str, List[str]]
        A dictionary where keys are sample names and values are lists of
        missing file types for that sample.
    """
    if required_types is None:
        required_types = ["cDNAfastq1", "cDNAfastq2", "oligofastq1", "oligofastq2"]

    validation_result = {}

    for sample_name, files in sample_dict.items():
        missing = []
        for file_type in required_types:
            if not files.get(file_type):
                missing.append(file_type)

        if missing:
            validation_result[sample_name] = missing

    return validation_result


# Convenience function with the exact signature requested
def scan_fastq_directory(path: str) -> Dict[str, Dict[str, str]]:
    """
    Convenience wrapper for scan_fastq_files with default patterns.

    This function provides the exact interface requested:
    - Input: path string
    - Output: dictionary with folder names as keys and file mappings as values

    Parameters
    ----------
    path : str
        The directory path to scan.

    Returns
    -------
    Dict[str, Dict[str, str]]
        Dictionary mapping folder names to fastq file dictionaries.
    """
    return scan_fastq_files(path)
