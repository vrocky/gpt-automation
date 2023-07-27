import os
import pathlib
import igittigitt
import fnmatch
import re
import time

class IgnoreMatch:
    def __init__(self, gitignore_path, pattern_list=None):
        self.gitignore_path = gitignore_path
        self.parser = igittigitt.IgnoreParser()
        self.parser.parse_rule_file(gitignore_path)
        self.patterns = self.compile_patterns(pattern_list) if pattern_list else []

    def match(self, path):
        path = pathlib.Path(path)
        return self.parser.match(path) or self.matches_list_pattern(str(path))

    @staticmethod
    def compile_patterns(pattern_list):
        return [re.compile(fnmatch.translate(pattern.strip())) for pattern in pattern_list]

    def matches_list_pattern(self, file_path):
        file_path = file_path.replace("\\", "/")
        file_path = file_path.lstrip("/")
        for pattern in self.patterns:
            if pattern.fullmatch(file_path):
                return True
        return False

def load_gitignore(gitignore_path, pattern_list=None):
    return IgnoreMatch(gitignore_path, pattern_list)

def matches_any_pattern(file_path, matches_collection):
    for match in matches_collection:
        if match.match(file_path):
            return True
    return False

def ignore_walk(path, black_list, white_list):
    start_time = time.time()

    gitignores = [file_path for file_path in pathlib.Path(path).rglob('.gitignore')]
    elapsed_time = time.time() - start_time
    #print(f"Time taken for creating gitignores: {elapsed_time:.4f} seconds")

    matches_collection = [load_gitignore(g, black_list) for g in gitignores]
    elapsed_time = time.time() - start_time
    #print(f"Time taken for creating matches_collection: {elapsed_time:.4f} seconds")

    start_time = time.time()

    for dirpath, dirnames, filenames in os.walk(path):
        dirnames[:] = [d for d in dirnames if not matches_any_pattern(os.path.join(dirpath, d), matches_collection)]
        filenames = [f for f in filenames if not matches_any_pattern(os.path.join(dirpath, f), matches_collection)]

        # Print the current directory being traversed
        #print(f"Processing directory: {dirpath}")

        # Print the elapsed time for each directory traversal
        elapsed_time = time.time() - start_time
        #print(f"Time taken for directory traversal: {elapsed_time:.4f} seconds")
        start_time = time.time()

        yield dirpath, dirnames, filenames

    # Print the overall elapsed time for the ignore_walk function
    elapsed_time = time.time() - start_time
    #print(f"Total time taken for ignore_walk: {elapsed_time:.4f} seconds")



"""
def ignore_walk_hold(path, black_list, white_list):

    gitignores = [file_path for file_path in pathlib.Path(path).rglob('.gitignore')]

    matches_collection = [load_gitignore(g) for g in gitignores]

    for dirpath, dirnames, filenames in os.walk(path):
        dirnames[:] = [d for d in dirnames if not matches_any_pattern(os.path.join(dirpath, d), matches_collection)
                        and not matches_list_pattern(os.path.join(dirpath, d), black_list)]
        filenames = [f for f in filenames if not matches_any_pattern(os.path.join(dirpath, f), matches_collection)
                        and (not white_list or matches_list_pattern(os.path.join(dirpath, f), white_list))]
        yield dirpath, dirnames, filenames
"""