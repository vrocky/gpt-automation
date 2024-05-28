import os
import subprocess
from pathlib import Path

def find_git_root(start_path):
    """
    Finds the git repository root starting from the given path.
    If the start_path is not in a git repository, returns None.
    """
    try:
        # Attempt to find the git repository root directory
        git_root = subprocess.check_output(['git', '-C', start_path, 'rev-parse', '--show-toplevel'], stderr=subprocess.STDOUT).strip().decode('utf-8')
        return git_root
    except subprocess.CalledProcessError:
        # Not in a git repository
        return None

def normalize_path(path, base_path):
    """
    Normalize a path to be relative to base_path and use forward slashes.
    """
    return Path(path).relative_to(base_path).as_posix()

def is_git_repository(path):
    """
    Check if the given path is within a git repository.
    """
    return find_git_root(path) is not None