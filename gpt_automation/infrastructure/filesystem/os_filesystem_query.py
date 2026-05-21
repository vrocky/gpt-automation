"""
Real filesystem implementation of FilesystemQuery.

All actual OS I/O happens in this file.
Domain layer never imports from here — only infrastructure does.
"""

import os
from pathlib import Path
from gpt_automation.domain.traversal.directory_reader import FilesystemQuery


class OsFilesystemQuery(FilesystemQuery):
    """
    Answers filesystem questions using the real OS.

    This is the production implementation injected at runtime.
    Tests inject a fake/mock instead.
    """

    def is_file(self, path: Path) -> bool:
        return Path(path).is_file()

    def is_directory(self, path: Path) -> bool:
        return Path(path).is_dir()

    def list_directory(self, dir_path: Path) -> list[Path]:
        """List all entries in directory, raising on failure."""
        try:
            return [Path(dir_path) / entry for entry in os.listdir(dir_path)]
        except (OSError, PermissionError) as e:
            raise FilesystemAccessError(f"Cannot read directory {dir_path}: {e}")


class FilesystemAccessError(Exception):
    """Raised when the OS denies a filesystem operation."""
    pass
