import fnmatch
import os
import pathlib
import gitignore_parser
import re

from gpt_automation.git_tools import find_git_root  # Ensure this is defined somewhere in your code

class IgnoreMatch:
    def __init__(self, ignore_paths):
        # Changed to support multiple ignore paths
        self.ignore_paths = ignore_paths
        self.matches = [gitignore_parser.parse_gitignore(path) for path in ignore_paths]

    def match(self, file_path):
        # Check against all provided ignore files
        return any(match(file_path) for match in self.matches)

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

def filter_with_white_list(filtered_filenames, white_list_patterns):
    if white_list_patterns:
        return [filename for filename in filtered_filenames if matches_list_pattern(filename, white_list_patterns)]
    else:
        return filtered_filenames

def ignore_walk(path, black_list, white_list, ignore_file_names=['.gitignore',".gptignore"]):
    black_list_patterns = compile_patterns(black_list)
    white_list_patterns = compile_patterns(white_list) if white_list else None

    visited = set()
    ignore_matches_stack = init_ignore_stack(path, ignore_file_names)

    def walk(dirpath, depth):
        if dirpath in visited:
            return
        visited.add(dirpath)

        local_ignore_paths = find_ignore_files(dirpath, ignore_file_names)
        ignore_matches_stack.append(local_ignore_paths if local_ignore_paths else None)

        dirnames, filenames = [], []
        for entry in os.scandir(dirpath):
            if entry.is_dir(follow_symlinks=False):
                dirnames.append(entry.name)
            elif entry.is_file():
                filenames.append(entry.name)

        # Filter filenames based on ignore files, blacklist, and whitelist
        filtered_filenames = [filename for filename in filenames if not should_ignore_by_ignore_files(os.path.join(dirpath, filename), ignore_matches_stack) and not should_ignore_by_black_list(os.path.join(dirpath, filename), black_list_patterns)]
        filtered_filenames = filter_with_white_list(filtered_filenames, white_list_patterns)

        yield dirpath, dirnames, filtered_filenames

        for dirname in dirnames:
            full_dir_path = os.path.join(dirpath, dirname)
            if not should_ignore_by_ignore_files(full_dir_path, ignore_matches_stack) and not should_ignore_by_black_list(full_dir_path, black_list_patterns):
                yield from walk(full_dir_path, depth + 1)

        ignore_matches_stack.pop()

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
