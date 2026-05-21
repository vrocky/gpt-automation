"""
Core file filtering domain logic.

Purely business rules: "Should a file be processed?"
No filesystem I/O, no JSON loading, no external dependencies.
"""

from abc import ABC, abstractmethod
from pathlib import Path


class FileFilter(ABC):
    """
    Decides whether a file should be included in processing.

    Pure business logic: same input → same output, no side effects.
    Fully testable without any mocks.
    """

    @abstractmethod
    def should_include_file(self, file_path: Path) -> bool:
        """Return True if file should be processed, False to skip it."""
        ...

    @abstractmethod
    def should_include_directory(self, dir_path: Path) -> bool:
        """Return True if directory contents should be traversed."""
        ...


class AllFilters(FileFilter):
    """
    Combine multiple filters: ALL must agree to include.

    AND logic — if any filter says "exclude", file is excluded.
    """

    def __init__(self, filters: list[FileFilter]):
        if not filters:
            raise ValueError("AllFilters requires at least one filter")
        self._filters = filters

    def should_include_file(self, file_path: Path) -> bool:
        """Include only if every filter agrees."""
        return all(f.should_include_file(file_path) for f in self._filters)

    def should_include_directory(self, dir_path: Path) -> bool:
        """Traverse only if every filter agrees."""
        return all(f.should_include_directory(dir_path) for f in self._filters)


class IncludeEverythingFilter(FileFilter):
    """
    Pass-through filter that includes all files and directories.

    Use when filtering is disabled. Explicit Null Object pattern —
    better than None checks everywhere.
    """

    def should_include_file(self, file_path: Path) -> bool:
        return True

    def should_include_directory(self, dir_path: Path) -> bool:
        return True
