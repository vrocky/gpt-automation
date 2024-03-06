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
    matches_collection = []

    def should_ignore(file_path):
        return any(match.match(file_path) for match in matches_collection) or matches_list_pattern(file_path, black_list_patterns)

    def walk(dirpath):
        if dirpath in visited:
            return
        visited.add(dirpath)

        local_gitignore_path = os.path.join(dirpath, '.gitignore')
        if os.path.exists(local_gitignore_path):
            matches_collection.append(load_gitignore(local_gitignore_path))

        dirnames, filenames = [], []
        for entry in os.scandir(dirpath):
            if entry.is_dir(follow_symlinks=False):
                dirnames.append(entry.name)
            elif entry.is_file():
                filenames.append(entry.name)

        yield dirpath, dirnames, filenames

        for dirname in dirnames:
            full_dir_path = os.path.join(dirpath, dirname)
            if not should_ignore(full_dir_path):
                yield from walk(full_dir_path)

    return walk(path)