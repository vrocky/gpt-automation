import fnmatch
import re


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