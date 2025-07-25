import os
import logging
from typing import Optional, Set
from gpt_automation.impl.visitor.basevisitor import BaseVisitor


class DefaultVisitor(BaseVisitor):
    """Default implementation that does nothing for traversal events"""
    
    def before_traverse_directory(self, directory_path):
        pass

    def enter_directory(self, directory_path):
        pass

    def visit_file(self, file_path):
        pass

    def leave_directory(self, directory_path):
        pass

    def should_visit_file(self, file_path):
        return True

    def should_visit_subdirectory(self, directory_path):
        return True


class DirectoryWalker:
    def __init__(self, 
                 path: str,
                 visitor: Optional[BaseVisitor] = None):
        """
        Initialize DirectoryWalker with optional visitor
        
        Args:
            path: Root path to start traversal
            visitor: Optional BaseVisitor implementation
        """
        self.path = path
        self.visitor = visitor or DefaultVisitor()
        self.logger = logging.getLogger(__name__)

    def walk(self):
        """Walk through directory structure and yield file paths."""
        visited_dirs = set()
        self.visitor.before_traverse_directory(self.path)
        yield from self._walk(self.path, visited_dirs)

    def _safe_visit(self, method, *args):
        """Safely execute visitor method, logging any errors"""
        try:
            return method(*args)
        except Exception as e:
            self.logger.error(f"Error in visitor {method.__name__}: {str(e)}")
            return True  # Continue traversal by default

    def _walk(self, directory_path: str, visited_dirs: Set[str]):
        if directory_path in visited_dirs:
            return
        visited_dirs.add(directory_path)

        self._safe_visit(self.visitor.enter_directory, directory_path)

        try:
            entries = list(os.scandir(directory_path))
            subdirectories = []
            
            # Process files first
            for entry in entries:
                if entry.is_file():
                    if self._safe_visit(self.visitor.should_visit_file, entry.path):
                        self._safe_visit(self.visitor.visit_file, entry.path)
                        yield entry.path
                elif entry.is_dir(follow_symlinks=False):
                    subdirectories.append(entry.path)

            # Process subdirectories
            for subdir in subdirectories:
                if self._safe_visit(self.visitor.should_visit_subdirectory, subdir):
                    yield from self._walk(subdir, visited_dirs)

        finally:
            self._safe_visit(self.visitor.leave_directory, directory_path)
