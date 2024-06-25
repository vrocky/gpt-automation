# gpt_automation/visitor/ignore_visitor.py
from gpt_automation.filters import should_ignore_by_ignore_files
from gpt_automation.visitor.basevisitor import BaseVisitor
from gpt_automation.ignore_file_parser import collect_patterns_from_ignore_files


class IgnoreVisitor(BaseVisitor):
    def __init__(self, ignore_filenames=None, profile_names=None):
        self.ignore_filenames = ignore_filenames or ['.gitignore', '.gptignore']
        self.profile_names = profile_names
        self.ignore_patterns_stack = []

    def enter_directory(self, directory_path):
        local_ignore_patterns = collect_patterns_from_ignore_files(directory_path, self.ignore_filenames,
                                                                   self.profile_names)
        self.ignore_patterns_stack.append(local_ignore_patterns if local_ignore_patterns else [])

    def leave_directory(self, directory_path):
        self.ignore_patterns_stack.pop()

    def should_visit_file(self, file_path):
        return not should_ignore_by_ignore_files(file_path, self.ignore_patterns_stack)

    def should_visit_subdirectory(self, subdir_path):
        return not should_ignore_by_ignore_files(subdir_path, self.ignore_patterns_stack)

    def before_traverse_directory(self, directory_path):
        # Potential pre-processing before entering a directory
        print(f"Preparing to traverse {directory_path}")

    def visit_file(self, file_path):
        # Handle visiting a file
        print(f"Visiting file: {file_path}")

