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

    gitignores = [file_path for file_path in pathlib.Path(path).rglob('.gitignore')]

    black_list_patterns = compile_patterns(black_list)
    white_list_patterns = compile_patterns(white_list) if white_list else None


    matches_collection = [load_gitignore(g) for g in gitignores]

    for dirpath, dirnames, filenames in os.walk(path):
        dirnames[:] = [d for d in dirnames if not matches_any_pattern(os.path.join(dirpath, d), matches_collection)
                        and not matches_list_pattern(os.path.join(dirpath, d), black_list_patterns)]
        filenames = [f for f in filenames if not matches_any_pattern(os.path.join(dirpath, f), matches_collection)
                        and (not white_list or matches_list_pattern(os.path.join(dirpath, f), white_list_patterns))]
        yield dirpath, dirnames, filenames
