"""
Directory traversal using injected path provider.

Domain logic for walking directories. No filesystem calls—uses injected PathProvider.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from gpt_automation.domain.filters.file_filter import FileFilter


class PathProvider(ABC):
    """
    Infrastructure abstraction: "How do we know which files exist?"

    Injected into domain so domain can be tested without real filesystem.
    This is the ONLY way domain communicates with I/O layer.
    """

    @abstractmethod
    def file_exists(self, path: Path) -> bool:
        """Check if path exists as a file."""
        ...

    @abstractmethod
    def is_file(self, path: Path) -> bool:
        """Check if path is a regular file."""
        ...

    @abstractmethod
    def is_directory(self, path: Path) -> bool:
        """Check if path is a directory."""
        ...

    @abstractmethod
    def list_entries(self, dir_path: Path) -> list[Path]:
        """Return all entries in directory (files and subdirectories)."""
        ...


class DirectoryReader:
    """
    Recursively read directory tree, filtering with FileFilter.

    Does NOT do I/O itself—uses injected PathProvider.
    Does NOT know about JSON, plugins, or settings.
    Pure business logic: given filesystem info, apply filter.
    """

    def __init__(self, path_provider: PathProvider):
        self._paths = path_provider

    def collect_files(self, root_dir: Path, file_filter: FileFilter) -> list[Path]:
        """
        Recursively collect files that filter accepts.

        Returns list of absolute paths.
        """
        collected: list[Path] = []
        self._traverse(root_dir, file_filter, collected)
        return collected

    def _traverse(self, current_dir: Path, file_filter: FileFilter, collected: list[Path]) -> None:
        """Recursively traverse directory, respecting filter decisions."""
        if not self._paths.is_directory(current_dir):
            return

        if not file_filter.should_traverse_directory(current_dir):
            return

        try:
            entries = self._paths.list_entries(current_dir)
        except (OSError, PermissionError):
            return  # Silently skip unreadable directories

        for entry in sorted(entries):
            if self._paths.is_file(entry):
                if file_filter.accepts(entry):
                    collected.append(entry)

            elif self._paths.is_directory(entry):
                self._traverse(entry, file_filter, collected)
