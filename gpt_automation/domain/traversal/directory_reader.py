"""
Directory traversal using injected filesystem query object.

Domain logic for walking directories. No filesystem calls — uses injected
FilesystemQuery abstraction so this code stays testable without real I/O.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from gpt_automation.domain.filters.file_filter import FileFilter


class FilesystemQuery(ABC):
    """
    Abstraction for asking questions about the filesystem.

    Injected into domain so it can be tested without real filesystem.
    This is the boundary between domain logic and I/O infrastructure.

    Domain uses this to ask: "is this a file?", "what's in this directory?"
    Infrastructure provides the real answers from the OS.
    """

    @abstractmethod
    def is_file(self, path: Path) -> bool:
        """True if path is a regular file."""
        ...

    @abstractmethod
    def is_directory(self, path: Path) -> bool:
        """True if path is a directory."""
        ...

    @abstractmethod
    def list_directory(self, dir_path: Path) -> list[Path]:
        """Return all entries inside a directory (files and subdirs combined)."""
        ...


class DirectoryWalker:
    """
    Walk a directory tree and collect files matching a filter.

    All filesystem queries go through injected FilesystemQuery.
    No I/O happens in this class—pure coordination logic.
    """

    def __init__(self, filesystem: FilesystemQuery):
        self._filesystem = filesystem

    def collect_matching_files(self, root_dir: Path, file_filter: FileFilter) -> list[Path]:
        """
        Recursively collect files that pass the filter.

        Returns sorted list of absolute paths.
        """
        collected: list[Path] = []
        self._walk(root_dir, file_filter, collected)
        return collected

    def _walk(self, current_dir: Path, file_filter: FileFilter, collected: list[Path]) -> None:
        """Recursively walk directory, applying filter at each step."""
        if not self._filesystem.is_directory(current_dir):
            return

        if not file_filter.should_include_directory(current_dir):
            return

        try:
            entries = self._filesystem.list_directory(current_dir)
        except (OSError, PermissionError):
            return  # Skip unreadable directories silently

        for entry in sorted(entries):
            if self._filesystem.is_file(entry):
                if file_filter.should_include_file(entry):
                    collected.append(entry)

            elif self._filesystem.is_directory(entry):
                self._walk(entry, file_filter, collected)
