import os
from gpt_automation.plugins.ignore_plugin.filters import should_include_by_include_only_list
from gpt_automation.impl.visitor.basevisitor import BaseVisitor
from gpt_automation.plugins.ignore_plugin.ignore_file_parser import collect_patterns_from_ignore_files, generate_pattern_pairs


class IncludeOnlyVisitor(BaseVisitor):
    def __init__(self, root_dir, prompt_dir, include_only_filenames=None, profile_names=None):
        self.root_dir = root_dir
        self.prompt_dir = prompt_dir
        self.include_only_filenames = include_only_filenames or ['.gptincludeonly']
        self.profile_names = profile_names
        self.include_only_patterns_stack = []

        self.initialize_include_only_patterns()

    def initialize_include_only_patterns(self):
        """
        Initializes the include-only pattern stack by walking from the root directory to the prompt directory
        and collecting include-only patterns along the way.
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
        local_include_only_patterns = collect_patterns_from_ignore_files(
            directory_path, self.include_only_filenames, self.profile_names)
        # Fallback to include all files if no specific patterns are found

        self.include_only_patterns_stack.append(
            local_include_only_patterns if local_include_only_patterns else generate_pattern_pairs(directory_path,
                                                                                                   ["*"]))

    def leave_directory(self, directory_path):
        self.include_only_patterns_stack.pop()

    def should_visit_file(self, file_path):

        return should_include_by_include_only_list(file_path, self.include_only_patterns_stack)

    def should_visit_subdirectory(self, subdir_path):
        return should_include_by_include_only_list(subdir_path, self.include_only_patterns_stack)

    def before_traverse_directory(self, directory_path):
        # Potential pre-processing before entering a directory
        print(f"Preparing to traverse {directory_path}")

    def visit_file(self, file_path):
        pass
        # Handle visiting a file
        #print(f"Visiting file: {file_path}")
