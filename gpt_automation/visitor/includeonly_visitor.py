# gpt_automation/visitor/include_only_visitor.py
from gpt_automation.filters import should_include_by_include_only_list
from gpt_automation.visitor.basevisitor import BaseVisitor
from gpt_automation.ignore_file_parser import collect_patterns_from_ignore_files, generate_pattern_pairs


class IncludeOnlyVisitor(BaseVisitor):

    def __init__(self, include_only_filenames=None, profile_names=None):
        self.include_only_filenames = include_only_filenames or ['.gptincludeonly']
        self.profile_names = profile_names
        self.include_only_patterns_stack = []

    def enter_directory(self, directory_path):
        local_include_only_patterns = collect_patterns_from_ignore_files(directory_path,
                                                                         self.include_only_filenames,
                                                                         self.profile_names)
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
        # Handle visiting a file
        print(f"Visiting file: {file_path}")
