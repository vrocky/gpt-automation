import os
import pathlib
import igittigitt
import fnmatch
import re
class IgnoreMatch:
    def __init__(self, gitignore_path):
        self.gitignore_path = gitignore_path
        self.parser = igittigitt.IgnoreParser()
        self.parser.parse_rule_file(gitignore_path)

    def match(self, path):
        path = pathlib.Path(path)
        return self.parser.match(path)

def load_gitignore(gitignore_path):
    return IgnoreMatch(gitignore_path)

def matches_any_pattern(file_path, matches_collection):
    for match in matches_collection:
        if match.match(file_path):
            return True
    return False

def compile_patterns(patterns_list):
    compiled_patterns = [re.compile(fnmatch.translate(pattern)) for pattern in patterns_list]
    return compiled_patterns
def matches_list_pattern( file_path, patterns):
    file_path = file_path.replace("\\", "/")
    file_path = file_path.lstrip("/")
    for pattern in patterns:
        if pattern.fullmatch(file_path):
            return True
    return False


def ignore_walk(path, black_list, white_list):
    black_list_patterns = compile_patterns(black_list)
    white_list_patterns = compile_patterns(white_list) if white_list else None

    visited = set()
    matches_stack = [[]]  # Use a stack to manage matches_collections for each directory depth

    def should_ignore(file_path, current_matches_collection):
        return any(match.match(file_path) for match in current_matches_collection) or matches_list_pattern(file_path, black_list_patterns)

    def walk(dirpath, depth):
        if dirpath in visited:
            return
        visited.add(dirpath)

        local_gitignore_path = os.path.join(dirpath, '.gitignore')
        if os.path.exists(local_gitignore_path):
            # When entering a directory, add its .gitignore rules to a new level in the stack
            matches_stack.append(matches_stack[-1] + [load_gitignore(local_gitignore_path)])
        else:
            # If no .gitignore, still add a new level to stack for consistent depth management
            matches_stack.append(list(matches_stack[-1]))

        dirnames, filenames = [], []
        for entry in os.scandir(dirpath):
            if entry.is_dir(follow_symlinks=False):
                dirnames.append(entry.name)
            elif entry.is_file():
                filenames.append(entry.name)

        yield dirpath, dirnames, filenames

        for dirname in dirnames:
            full_dir_path = os.path.join(dirpath, dirname)
            if not should_ignore(full_dir_path, matches_stack[-1]):
                yield from walk(full_dir_path, depth + 1)

        # After walking a directory, remove its matches_collection from the stack
        matches_stack.pop()

    return walk(path, 0)