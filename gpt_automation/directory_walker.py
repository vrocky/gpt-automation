import logging
import os
import pathlib

from gpt_automation.ignore_file_parser import collect_patterns_from_ignore_files, generate_pattern_pairs
from gpt_automation.utils.git_tools import find_git_root
from gpt_automation.filters import (
    should_ignore_by_ignore_files,
    filter_with_white_list,
    should_ignore_by_black_list,
    should_include_by_include_only_list
)
from gpt_automation.utils.pattern_utils import compile_patterns


class DirectoryWalker:
    def __init__(self, path, blacklist=None, whitelist=None, profile_names=None, ignore_filenames=None,
                 include_only_filenames=None):
        """
        Initialize the DirectoryWalker with necessary configurations.
        """
        self.path = path
        self.profile_names = profile_names
        self.ignore_filenames = ignore_filenames or ['.gitignore', '.gptignore']
        self.include_only_filenames = include_only_filenames or ['.gptincludeonly']

        # Compile patterns from provided lists
        self.blacklist_patterns = compile_patterns(blacklist or [])
        self.whitelist_patterns = compile_patterns(whitelist) if whitelist else None
        self.include_only_patterns = compile_patterns(include_only_filenames) if include_only_filenames else None

    def walk(self):
        """
        Walk through directories and apply filters based on patterns and stacks.
        """
        visited_dirs = set()
        ignore_patterns_stack = self.initialize_ignore_patterns_stack(self.path)
        include_only_patterns_stack = self.initialize_ignore_patterns_stack(self.path)

        return self._walk(self.path, visited_dirs, ignore_patterns_stack, include_only_patterns_stack)

    def _walk(self, directory_path, visited_dirs, ignore_patterns_stack, include_only_patterns_stack):
        """
        Recursively walk through directories, filtering files and subdirectories based on ignore and include patterns.
        """
        if directory_path in visited_dirs:
            return
        visited_dirs.add(directory_path)

        local_ignore_patterns = collect_patterns_from_ignore_files(directory_path, self.ignore_filenames,
                                                                   self.profile_names)
        ignore_patterns_stack.append(local_ignore_patterns if local_ignore_patterns else None)

        local_include_only_patterns = collect_patterns_from_ignore_files(directory_path, self.include_only_filenames,
                                                                         self.profile_names)
        include_only_patterns_stack.append(
            local_include_only_patterns if local_include_only_patterns else generate_pattern_pairs(directory_path,
                                                                                                   ["*"]))

        entries = list(os.scandir(directory_path))
        subdirectories, file_names = self._organize_directory_contents(entries)

        filtered_filenames = self._filter_files(directory_path, file_names, ignore_patterns_stack,
                                                include_only_patterns_stack)
        filtered_subdirectories_yield = self._filter_directories(directory_path, subdirectories, ignore_patterns_stack,
                                                                 include_only_patterns_stack)

        yield directory_path, filtered_subdirectories_yield, filtered_filenames

        for subdir in filtered_subdirectories_yield:
            full_subdir_path = os.path.join(directory_path, subdir)
            if self._can_traverse(full_subdir_path, ignore_patterns_stack):
                yield from self._walk(full_subdir_path, visited_dirs, ignore_patterns_stack,
                                      include_only_patterns_stack)

        ignore_patterns_stack.pop()
        include_only_patterns_stack.pop()

    def initialize_ignore_patterns_stack(self, start_path):
        """
        Initialize ignore patterns stack from the git root path to the start path.
        """
        git_root_path = find_git_root(start_path)
        patterns_stack = []
        if git_root_path:
            relative_path = os.path.relpath(start_path, git_root_path)
            current_path = git_root_path
            for part in pathlib.Path(relative_path).parts:
                current_path = os.path.join(current_path, part)
                pattern_pairs = collect_patterns_from_ignore_files(current_path, self.ignore_filenames,
                                                                   self.profile_names)
                patterns_stack.append(pattern_pairs if pattern_pairs else [])
        else:
            patterns_stack.append([])
        return patterns_stack

    def _organize_directory_contents(self, entries):
        subdirectories, file_names = [], []
        for entry in entries:
            if entry.is_dir(follow_symlinks=False):
                subdirectories.append(entry.name)
            elif entry.is_file():
                file_names.append(entry.name)
        return subdirectories, file_names

    def _filter_files(self, directory_path, file_names, ignore_patterns_stack, include_only_patterns_stack):
        return [
            filename for filename in file_names
            if not should_ignore_by_ignore_files(os.path.join(directory_path, filename), ignore_patterns_stack)
               and not should_ignore_by_black_list(os.path.join(directory_path, filename), self.blacklist_patterns)
               and should_include_by_include_only_list(os.path.join(directory_path, filename),
                                                       include_only_patterns_stack)
        ]

    def _filter_directories(self, directory_path, subdirectories, ignore_patterns_stack, include_only_patterns_stack):
        return [
            subdir for subdir in subdirectories
            if self._can_traverse(os.path.join(directory_path, subdir + "/"), ignore_patterns_stack)
               and should_include_by_include_only_list(os.path.join(directory_path, subdir + "/"),
                                                       include_only_patterns_stack)
        ]

    def _can_traverse(self, path, ignore_patterns_stack):
        """
        Check if a path can be traversed based on ignore patterns.
        """
        return not should_ignore_by_ignore_files(path, ignore_patterns_stack) \
            and not should_ignore_by_black_list(path, self.blacklist_patterns)
