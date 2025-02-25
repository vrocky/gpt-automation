import os
from abc import ABC, abstractmethod
from typing import Optional, Set


class ITraverseFilter(ABC):
    """Interface for filtering files and directories during traversal"""
    
    @abstractmethod
    def should_visit_file(self, file_path: str) -> bool:
        """Determine if a file should be visited"""
        pass

    @abstractmethod
    def should_visit_directory(self, directory_path: str) -> bool:
        """Determine if a directory should be visited"""
        pass


class IDirectoryTraverser(ABC):
    """Interface for directory traversal notifications"""
    
    @abstractmethod
    def on_enter_directory(self, directory_path: str) -> None:
        """Called when entering a directory"""
        pass

    @abstractmethod
    def on_leave_directory(self, directory_path: str) -> None:
        """Called when leaving a directory"""
        pass

    @abstractmethod
    def on_file_found(self, file_path: str) -> None:
        """Called when a file is found"""
        pass


class DefaultTraverseFilter(ITraverseFilter):
    """Default implementation that accepts all files and directories"""
    
    def should_visit_file(self, file_path: str) -> bool:
        return True

    def should_visit_directory(self, directory_path: str) -> bool:
        return True


class DefaultDirectoryTraverser(IDirectoryTraverser):
    """Default implementation that does nothing for traversal events"""
    
    def on_enter_directory(self, directory_path: str) -> None:
        pass

    def on_leave_directory(self, directory_path: str) -> None:
        pass

    def on_file_found(self, file_path: str) -> None:
        pass


class DirectoryWalker:
    def __init__(self, 
                 path: str,
                 traverser: Optional[IDirectoryTraverser] = None,
                 traverse_filter: Optional[ITraverseFilter] = None):
        """
        Initialize DirectoryWalker with optional traverser and filter
        
        Args:
            path: Root path to start traversal
            traverser: Optional IDirectoryTraverser implementation
            traverse_filter: Optional ITraverseFilter implementation
        """
        self.path = path
        self.traverser = traverser or DefaultDirectoryTraverser()
        self.traverse_filter = traverse_filter or DefaultTraverseFilter()

    def walk(self):
        """Walk through directory structure and yield file paths."""
        visited_dirs = set()
        yield from self._walk(self.path, visited_dirs)

    def _walk(self, directory_path: str, visited_dirs: Set[str]):
        if directory_path in visited_dirs:
            return
        visited_dirs.add(directory_path)

        self.traverser.on_enter_directory(directory_path)

        try:
            entries = list(os.scandir(directory_path))
            subdirectories = []
            
            # Process files first
            for entry in entries:
                if entry.is_file():
                    if self.traverse_filter.should_visit_file(entry.path):
                        self.traverser.on_file_found(entry.path)
                        yield entry.path
                elif entry.is_dir(follow_symlinks=False):
                    subdirectories.append(entry.path)

            # Process subdirectories
            for subdir in subdirectories:
                if self.traverse_filter.should_visit_directory(subdir):
                    yield from self._walk(subdir, visited_dirs)

        finally:
            self.traverser.on_leave_directory(directory_path)
