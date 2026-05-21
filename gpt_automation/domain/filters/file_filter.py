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

    This is pure business logic: same input → same output, always.
    No side effects, no I/O, fully testable without mocks.
    """

    @abstractmethod
    def accepts(self, file_path: Path) -> bool:
        """Return True if file should be included, False to exclude."""
        ...

    @abstractmethod
    def should_traverse_directory(self, dir_path: Path) -> bool:
        """Return True if directory should be traversed."""
        ...


class ChainedFilter(FileFilter):
    """
    Combine multiple filters with AND logic.

    ALL filters must accept for file to be included (strict mode).
    If one says "no", the file is excluded.
    """

    def __init__(self, filters: list[FileFilter]):
        if not filters:
            raise ValueError("ChainedFilter requires at least one filter")
        self._filters = filters

    def accepts(self, file_path: Path) -> bool:
        """File accepted only if ALL filters accept it."""
        return all(f.accepts(file_path) for f in self._filters)

    def should_traverse_directory(self, dir_path: Path) -> bool:
        """Directory traversed only if ALL filters allow it."""
        return all(f.should_traverse_directory(dir_path) for f in self._filters)


class NullFilter(FileFilter):
    """
    Accept all files. Used when no filtering is needed.

    Better than None checks everywhere. Explicit Null Object pattern.
    """

    def accepts(self, file_path: Path) -> bool:
        return True

    def should_traverse_directory(self, dir_path: Path) -> bool:
        return True
