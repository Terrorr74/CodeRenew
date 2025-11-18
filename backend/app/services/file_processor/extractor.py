"""
File Extractor Service
Handles extraction and processing of uploaded files
"""
from typing import List
from pathlib import Path
import zipfile
import shutil


class FileExtractor:
    """Extract and process WordPress files"""

    def __init__(self, upload_dir: str):
        """
        Initialize file extractor

        Args:
            upload_dir: Directory for file uploads
        """
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)

    async def extract_zip(self, zip_path: Path, extract_to: Path) -> List[Path]:
        """
        Extract a zip file

        Args:
            zip_path: Path to zip file
            extract_to: Directory to extract to

        Returns:
            List of extracted file paths
        """
        extract_to.mkdir(exist_ok=True, parents=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

        # Get list of PHP files
        php_files = list(extract_to.rglob("*.php"))

        return php_files

    async def get_php_files(self, directory: Path) -> List[Path]:
        """
        Get all PHP files from a directory

        Args:
            directory: Directory to search

        Returns:
            List of PHP file paths
        """
        return list(directory.rglob("*.php"))

    async def read_file(self, file_path: Path) -> str:
        """
        Read file contents

        Args:
            file_path: Path to file

        Returns:
            File contents as string
        """
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def cleanup(self, directory: Path) -> None:
        """
        Clean up temporary files

        Args:
            directory: Directory to remove
        """
        if directory.exists():
            shutil.rmtree(directory)
