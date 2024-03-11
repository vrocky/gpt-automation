import fnmatch
import os
import pathlib
import gitignore_parser
import re

from gpt_automation import gitignore_parser2
from gpt_automation.git_tools import find_git_root  # Ensure this is defined somewhere in your code


class IgnoreMatch:
    def __init__(self, ignore_paths):
        self.ignore_paths = ignore_paths
        self.matches = [
            gitignore_parser2.parse_patterns_with_base_dir(pathlib.Path(path).parent, [open(path, 'r').read()]) for path
            in ignore_paths]

    def match(self, file_path):
        return any(match(file_path) for match in self.matches)

    def has_matches(self):
        for ignore_path in self.ignore_paths:
            if os.path.exists(ignore_path):
                if not self._is_file_effectively_empty(ignore_path):
                    return True

        return False


    @staticmethod
    def _is_file_effectively_empty(file_path):
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'r') as file:
                content = file.read().strip()
                return len(content) == 0
        return True



def load_ignore_matches(ignore_paths):
    if ignore_paths:
        return IgnoreMatch(ignore_paths)
    else:
        return None


def matches_any_pattern(file_path, ignore_match_collection):
    for match in ignore_match_collection:
        if match.match(file_path):
            return True
    return False


def compile_patterns(patterns_list):
    compiled_patterns = [re.compile(fnmatch.translate(pattern)) for pattern in patterns_list]
    return compiled_patterns


def matches_list_pattern(file_path, patterns):
    file_path = file_path.replace("\\", "/")
    file_path = file_path.lstrip("/")
    for pattern in patterns:
        if pattern.fullmatch(file_path):
            return True
    return False


def should_ignore_by_ignore_files(file_path, ignore_matches_stack):
    for ignore_paths in reversed(ignore_matches_stack):
        if ignore_paths:
            ignore_match = load_ignore_matches(ignore_paths)
            if ignore_match and ignore_match.match(file_path):
                return True
    return False


def should_ignore_by_black_list(file_path, black_list_patterns):
    return matches_list_pattern(file_path, black_list_patterns)


def should_include_by_include_only_list(file_path, include_only_matches_stack):
    # Pre-load IgnoreMatch objects from the stack to avoid repeated loading
    preloaded_include_matches = [
        load_ignore_matches(include_only_paths) for include_only_paths in include_only_matches_stack if include_only_paths
    ]

    # Determine if any IgnoreMatch object has matches
    active_include_only_rules = any(match.has_matches() for match in preloaded_include_matches if match)

    # If no active rules are found, the feature is not in use, so return True
    if not active_include_only_rules:
        return True

    for include_match in reversed(preloaded_include_matches):
        if include_match and include_match.match(file_path):
            # If the file matches any include_only pattern, it should be included
            return True

    # If the file does not match any include_only patterns, it should not be included
    return False






def filter_with_white_list(filtered_filenames, white_list_patterns):
    if white_list_patterns and len(white_list_patterns) > 0:
        return [filename for filename in filtered_filenames if matches_list_pattern(filename, white_list_patterns)]
    else:
        return filtered_filenames


def ignore_walk(path, black_list, white_list, ignore_file_names=['.gitignore', ".gptignore"],
                include_only_file_names=[".gptincludeonly"]):
    black_list_patterns = compile_patterns(black_list)
    white_list_patterns = compile_patterns(white_list) if white_list else None
    include_only_patterns = compile_patterns(include_only_file_names) if include_only_file_names else None

    visited = set()
    ignore_matches_stack = init_ignore_stack(path, ignore_file_names)
    include_only_matches_stack = init_ignore_stack(path, include_only_file_names)  # Initialize the include_only stack

    def walk(dirpath, depth):
        if dirpath in visited:
            return
        visited.add(dirpath)

        local_ignore_paths = find_ignore_files(dirpath, ignore_file_names)
        ignore_matches_stack.append(local_ignore_paths if local_ignore_paths else None)

        local_include_only_paths = find_ignore_files(dirpath, include_only_file_names)
        include_only_matches_stack.append(local_include_only_paths if local_include_only_paths else None)

        dirnames, filenames = [], []
        for entry in os.scandir(dirpath):
            if entry.is_dir(follow_symlinks=False):
                dirnames.append(entry.name)
            elif entry.is_file():
                filenames.append(entry.name)

        # Filter filenames based on ignore files, blacklist, and whitelist
        filtered_filenames = [filename for filename in filenames if
                              not should_ignore_by_ignore_files(os.path.join(dirpath, filename),
                                                                ignore_matches_stack) and not should_ignore_by_black_list(
                                  os.path.join(dirpath, filename), black_list_patterns)]
        filtered_filenames = filter_with_white_list(filtered_filenames, white_list_patterns)

        filtered_filenames = [filename for filename in filtered_filenames if
                              should_include_by_include_only_list(os.path.join(dirpath, filename),
                                                                  include_only_matches_stack)]

        yield dirpath, dirnames, filtered_filenames

        for dirname in dirnames:
            full_dir_path = os.path.join(dirpath, dirname)
            if not should_ignore_by_ignore_files(full_dir_path,
                                                 ignore_matches_stack) and not should_ignore_by_black_list(
                    full_dir_path, black_list_patterns):
                yield from walk(full_dir_path, depth + 1)

        ignore_matches_stack.pop()
        include_only_matches_stack.pop()  # Ensure to pop from this stack too

    return walk(path, 0)


def find_ignore_files(dirpath, ignore_file_names):
    ignore_paths = []
    for ignore_file_name in ignore_file_names:
        for entry in os.scandir(dirpath):
            if entry.is_file() and entry.name in ignore_file_names:
                ignore_paths.append(entry.path)
    return ignore_paths


def init_ignore_stack(start_path, ignore_file_names):
    git_root = find_git_root(start_path)
    ignore_matches_stack = []
    if git_root:
        relative_path = os.path.relpath(start_path, git_root)
        current_path = git_root
        for part in pathlib.Path(relative_path).parts:
            current_path = os.path.join(current_path, part)
            ignore_paths = find_ignore_files(current_path, ignore_file_names)
            if ignore_paths:
                ignore_matches_stack.append(ignore_paths)
            else:
                ignore_matches_stack.append(None)
    else:
        ignore_matches_stack.append(None)
    return ignore_matches_stack
