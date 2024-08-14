# gpt_automation/visitor/ignore_visitor.py
import os

from gpt_automation.impl.filters import should_ignore_by_ignore_files
from gpt_automation.impl.visitor.basevisitor import BaseVisitor
from gpt_automation.impl.ignore_file_parser import collect_patterns_from_ignore_files


class IgnoreVisitor(BaseVisitor):
    def __init__(self, root_dir, prompt_dir, ignore_filenames=None, profile_names=None):
        self.root_dir = root_dir
        self.prompt_dir = prompt_dir
        self.ignore_filenames = ignore_filenames or ['.gitignore', '.gptignore']
        self.profile_names = profile_names
        self.ignore_patterns_stack = []
        self.initialize_ignore_patterns()

    def initialize_ignore_patterns(self):
        """
        Initializes the ignore pattern stack by walking from the root directory to the prompt directory
        and collecting ignore patterns along the way.
        """
        # Calculate the relative path from root_dir to prompt_dir
        relative_path = os.path.relpath(self.prompt_dir, self.root_dir)
        current_path = self.root_dir

        # Enter the root directory first
        self.enter_directory(self.root_dir)

        # Walk through each part of the path, adjusting the current_path and collecting patterns
        for part in relative_path.split(os.sep):
            if part not in ['', '.', '..']:
                current_path = os.path.join(current_path, part)
                self.enter_directory(current_path)

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
        pass
        # Handle visiting a file
        #print(f"Visiting file: {file_path}")
