import fnmatch
import os
import pathlib
import gitignore_parser
import re

from gpt_automation.git_tools import find_git_root  # Ensure this is defined somewhere in your code

class IgnoreMatch:
    def __init__(self, gitignore_path):
        self.gitignore_path = gitignore_path
        self.match = gitignore_parser.parse_gitignore(gitignore_path)

def load_gitignore(gitignore_path):
    if gitignore_path is not None:
        return IgnoreMatch(gitignore_path)
    else:
        return None

def matches_any_pattern(file_path, gitignore_match_collection):
    for match in gitignore_match_collection:
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

def should_ignore_by_git(file_path, gitignore_matches_stack):
    for gitignore_path in reversed(gitignore_matches_stack):
        if gitignore_path is not None:
            ignore_match = load_gitignore(gitignore_path)
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

def ignore_walk(path, black_list, white_list):
    black_list_patterns = compile_patterns(black_list)
    white_list_patterns = compile_patterns(white_list) if white_list else None

    visited = set()
    gitignore_match_stack = init_gitignore_stack(path)

    def walk(dirpath, depth):
        if dirpath in visited:
            return
        visited.add(dirpath)

        local_gitignore_path = os.path.join(dirpath, '.gitignore')
        if os.path.exists(local_gitignore_path):
            gitignore_match_stack.append(local_gitignore_path)
        else:
            gitignore_match_stack.append(None)

        dirnames, filenames = [], []
        for entry in os.scandir(dirpath):
            if entry.is_dir(follow_symlinks=False):
                dirnames.append(entry.name)
            elif entry.is_file():
                filenames.append(entry.name)

        # Filter filenames based on gitignore and blacklist
        filtered_filenames = [filename for filename in filenames if not should_ignore_by_git(os.path.join(dirpath, filename), gitignore_match_stack) and not should_ignore_by_black_list(os.path.join(dirpath, filename), black_list_patterns)]
        # Filter filenames with white list patterns
        filtered_filenames = filter_with_white_list(filtered_filenames, white_list_patterns)

        yield dirpath, dirnames, filtered_filenames

        for dirname in dirnames:
            full_dir_path = os.path.join(dirpath, dirname)
            if not should_ignore_by_git(full_dir_path, gitignore_match_stack) and not should_ignore_by_black_list(full_dir_path, black_list_patterns):
                yield from walk(full_dir_path, depth + 1)

        gitignore_match_stack.pop()

    return walk(path, 0)

def init_gitignore_stack(start_path):
    git_root = find_git_root(start_path)
    gitignore_match_stack = []
    if git_root:
        relative_path = os.path.relpath(start_path, git_root)
        current_path = git_root
        for part in pathlib.Path(relative_path).parts:
            current_path = os.path.join(current_path, part)
            gitignore_path = os.path.join(current_path, '.gitignore')
            if os.path.exists(gitignore_path):
                gitignore_match_stack.append(gitignore_path)
            else:
                gitignore_match_stack.append(None)
    else:
        gitignore_match_stack.append(None)
    return gitignore_match_stack
