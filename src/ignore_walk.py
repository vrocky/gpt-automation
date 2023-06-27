import os
import pathlib
import igittigitt
import fnmatch

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

def matches_list_pattern(file_path, pattern_list):
    file_path = file_path.replace("\\", "/")
    file_path = file_path.lstrip("/")
    return any(fnmatch.fnmatchcase(file_path, pattern.strip()) for pattern in pattern_list)

def ignore_walk(path, black_list, white_list):

    gitignores = [file_path for file_path in pathlib.Path(path).rglob('.gitignore')]

    matches_collection = [load_gitignore(g) for g in gitignores]

    for dirpath, dirnames, filenames in os.walk(path):
        dirnames[:] = [d for d in dirnames if not matches_any_pattern(os.path.join(dirpath, d), matches_collection)
                        and not matches_list_pattern(os.path.join(dirpath, d), black_list)]
        filenames = [f for f in filenames if not matches_any_pattern(os.path.join(dirpath, f), matches_collection)
                        and (not white_list or matches_list_pattern(os.path.join(dirpath, f), white_list))]
        yield dirpath, dirnames, filenames
