import pytest
import os
from pathlib import Path

# Assume the provided code has been placed in a file named `gitignore_parser.py`
from gitignore_parser import parse_gitignore, rule_from_pattern, _normalize_path

# Setup for testing environment
@pytest.fixture
def setup_test_files(tmp_path):
    base_dir = tmp_path / "base"
    base_dir.mkdir()
    (base_dir / "test.py").touch()
    (base_dir / "test.pyc").touch()
    (base_dir / "example.txt").touch()
    (base_dir / "ignore.me").touch()
    subdir = base_dir / "subdir"
    subdir.mkdir()
    (subdir / "test.py").touch()
    (subdir / "example.txt").touch()
    return base_dir

def write_gitignore(base_dir, patterns):
    gitignore_path = base_dir / ".gitignore"
    with open(gitignore_path, "w") as f:
        for pattern in patterns:
            f.write(pattern + "\n")
    return gitignore_path

# Test simple ignore
def test_simple_ignore(setup_test_files):
    base_dir = setup_test_files
    gitignore_path = write_gitignore(base_dir, ["*.pyc"])
    ignore_func = parse_gitignore(str(gitignore_path))

    assert ignore_func(str(base_dir / "test.pyc")) == True
    assert ignore_func(str(base_dir / "test.py")) == False

# Test directory-specific ignore
def test_directory_ignore(setup_test_files):
    base_dir = setup_test_files
    gitignore_path = write_gitignore(base_dir, ["subdir/"])
    ignore_func = parse_gitignore(str(gitignore_path))

    assert ignore_func(str(base_dir / "subdir")) == True
    assert ignore_func(str(base_dir / "subdir/test.py")) == True
    assert ignore_func(str(base_dir / "example.txt")) == False

# Test negation
def test_negation(setup_test_files):
    base_dir = setup_test_files
    gitignore_path = write_gitignore(base_dir, ["*.txt", "!example.txt"])
    ignore_func = parse_gitignore(str(gitignore_path))

    assert ignore_func(str(base_dir / "example.txt")) == False
    assert ignore_func(str(base_dir / "subdir/example.txt")) == True

# Test regex pattern matching
def test_regex_matching(setup_test_files):
    base_dir = setup_test_files
    gitignore_path = write_gitignore(base_dir, ["test.[p]*"])
    ignore_func = parse_gitignore(str(gitignore_path))

    assert ignore_func(str(base_dir / "test.py")) == True
    assert ignore_func(str(base_dir / "test.pyc")) == False  # Because it's not specified to ignore pyc files in this pattern

# Test nested directory handling
def test_nested_directory_handling(setup_test_files):
    base_dir = setup_test_files
    gitignore_path = write_gitignore(base_dir, ["**/*.txt"])
    ignore_func = parse_gitignore(str(gitignore_path))

    assert ignore_func(str(base_dir / "example.txt")) == True
    assert ignore_func(str(base_dir / "subdir/example.txt")) == True

