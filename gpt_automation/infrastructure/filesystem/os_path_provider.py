"""
Real filesystem implementation of PathProvider.

All actual I/O happens here. Domain never touches this file.
"""

import os
from pathlib import Path
from gpt_automation.domain.traversal.directory_reader import PathProvider


class OsPathProvider(PathProvider):
    """Implements PathProvider using Python's os module."""

    def file_exists(self, path: Path) -> bool:
        """Check if path exists as a file."""
        return path.exists() and path.is_file()

    def is_file(self, path: Path) -> bool:
        """Check if path is a regular file."""
        return path.is_file()

    def is_directory(self, path: Path) -> bool:
        """Check if path is a directory."""
        return path.is_directory()

    def list_entries(self, dir_path: Path) -> list[Path]:
        """List all entries in directory (files and subdirectories)."""
        try:
            return [dir_path / entry for entry in os.listdir(dir_path)]
        except (OSError, PermissionError) as e:
            raise FilesystemError(f"Cannot read directory {dir_path}: {e}")


class FilesystemError(Exception):
    """Raised when filesystem operations fail."""
    pass
