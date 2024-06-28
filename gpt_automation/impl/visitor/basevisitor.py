from abc import ABC, abstractmethod


class BaseVisitor(ABC):
    @abstractmethod
    def before_traverse_directory(self, directory_path):
        """
        Hook called before traversing a directory.
        """
        pass

    @abstractmethod
    def enter_directory(self, directory_path):
        """
        Hook called when entering a directory.
        """
        pass

    @abstractmethod
    def visit_file(self, file_path):
        """
        Hook called for each file visited.
        """
        pass

    @abstractmethod
    def leave_directory(self, directory_path):
        """
        Hook called when leaving a directory.
        """
        pass

    @abstractmethod
    def should_visit_file(self, file_path):
        """
        Determine if a file should be visited.
        """
        pass

    @abstractmethod
    def should_visit_subdirectory(self, subdir_path):
        """
        Determine if a subdirectory should be traversed.
        """
        pass
