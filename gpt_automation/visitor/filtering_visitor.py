from gpt_automation.filters import should_ignore_by_ignore_files, should_include_by_include_only_list
from gpt_automation.visitor.basevisitor import BaseVisitor
from gpt_automation.ignore_file_parser import collect_patterns_from_ignore_files, generate_pattern_pairs


class FilteringVisitor(BaseVisitor):
    def __init__(self, profile_names=None, ignore_filenames=None, include_only_filenames=None):
        self.profile_names = profile_names
        self.ignore_filenames = ignore_filenames or ['.gitignore', '.gptignore']
        self.include_only_filenames = include_only_filenames or ['.gptincludeonly']
        self.ignore_patterns_stack = []
        self.include_only_patterns_stack = []

    def before_traverse_directory(self, directory_path):
        # Potential pre-processing before entering a directory
        print(f"Preparing to traverse {directory_path}")

    def enter_directory(self, directory_path):
        # Handle entering a directory by updating pattern stacks
        print(f"Entering directory: {directory_path}")
        local_ignore_patterns = collect_patterns_from_ignore_files(directory_path, self.ignore_filenames, self.profile_names)
        self.ignore_patterns_stack.append(local_ignore_patterns if local_ignore_patterns else [])

        local_include_only_patterns = collect_patterns_from_ignore_files(directory_path, self.include_only_filenames, self.profile_names)
        self.include_only_patterns_stack.append(local_include_only_patterns if local_include_only_patterns else generate_pattern_pairs(directory_path, ["*"]))

    def visit_file(self, file_path):
        # Handle visiting a file
        print(f"Visiting file: {file_path}")

    def leave_directory(self, directory_path):
        # Cleanup when leaving a directory
        print(f"Leaving directory: {directory_path}")
        self.ignore_patterns_stack.pop()
        self.include_only_patterns_stack.pop()

    def should_visit_file(self, file_path):
        # Determine if a file should be visited based on ignore and include-only patterns
        return not should_ignore_by_ignore_files(file_path, self.ignore_patterns_stack) \
               and should_include_by_include_only_list(file_path, self.include_only_patterns_stack)

    def should_visit_subdirectory(self, subdir_path):
        # Determine if a subdirectory should be traversed
        return not should_ignore_by_ignore_files(subdir_path, self.ignore_patterns_stack) \
               and should_include_by_include_only_list(subdir_path, self.include_only_patterns_stack)
