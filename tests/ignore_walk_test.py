import os
import pytest
from gpt_automation import ignore_walk
from tempfile import TemporaryDirectory
import pathlib


# Fixture to create a temporary directory structure
@pytest.fixture
def setup_directory_structure():
    with TemporaryDirectory() as tmpdirname:
        print(f"Temporary directory created at: {tmpdirname}")
        os.makedirs(os.path.join(tmpdirname, "dir1"))
        os.makedirs(os.path.join(tmpdirname, "dir2"))
        pathlib.Path(os.path.join(tmpdirname, "dir1", ".gitignore")).write_text("*.log\n")
        pathlib.Path(os.path.join(tmpdirname, "dir1", "file1.txt")).touch()
        pathlib.Path(os.path.join(tmpdirname, "dir1", "file2.log")).touch()
        pathlib.Path(os.path.join(tmpdirname, "dir2", "file3.txt")).touch()
        yield tmpdirname


# Test to check if .gitignore rules are respected
def test_gitignore_rules(setup_directory_structure):
    root = setup_directory_structure

    black_list = []
    white_list = ["*.txt"]

    files = []
    for dirpath, dirnames, filenames in ignore_walk.ignore_walk(root, black_list, white_list):
        for filename in filenames:
            files.append(os.path.relpath(os.path.join(dirpath, filename), root).replace("\\","/"))

    print(files)
    assert "dir1/file1.txt" in files
    assert "dir1/file2.log" not in files
    assert "dir2/file3.txt" in files

# Additional tests for black_list and white_list can be implemented in a similar way



# Test to verify .gitignore rules in nested directories
def test_nested_gitignore_rules(setup_directory_structure):
    root = setup_directory_structure
    # Create a nested directory structure with its own .gitignore
    nested_dir = os.path.join(root, "dir2", "nested")
    os.makedirs(nested_dir)
    pathlib.Path(os.path.join(nested_dir, ".gitignore")).write_text("*.txt\n")
    pathlib.Path(os.path.join(nested_dir, "file4.txt")).touch()
    pathlib.Path(os.path.join(nested_dir, "file5.md")).touch()

    black_list = []
    white_list = []

    files = []
    for dirpath, dirnames, filenames in ignore_walk.ignore_walk(root, black_list, white_list):
        for filename in filenames:
            files.append(os.path.relpath(os.path.join(dirpath, filename), root).replace("\\", "/"))

    assert "dir2/nested/file4.txt" not in files  # Should be ignored due to nested .gitignore
    assert "dir2/nested/file5.md" in files  # Should not be ignored



# Test to ensure a deeply nested and dense subtree is ignored according to .gitignore rules
def test_ignore_deeply_nested_subtree(setup_directory_structure):
    root = setup_directory_structure
    # Create a deeply nested directory structure
    nested_dir = os.path.join(root, "dir3")
    deep_nesting_path = os.path.join(nested_dir, "level1", "level2", "level3", "level4")
    os.makedirs(deep_nesting_path)

    # Place a .gitignore in 'level1' to ignore a deep subtree starting from 'level3'
    pathlib.Path(os.path.join(nested_dir, "level1", ".gitignore")).write_text("level2/level3/\n")

    # Populate directories with files to test ignore functionality
    pathlib.Path(os.path.join(nested_dir, "file_at_root.txt")).touch()
    pathlib.Path(os.path.join(nested_dir, "level1", "file_at_level1.txt")).touch()
    pathlib.Path(os.path.join(nested_dir, "level1", "level2", "file_at_level2.txt")).touch()
    # This file should be ignored based on .gitignore rules
    pathlib.Path(os.path.join(deep_nesting_path, "file_to_be_ignored.txt")).touch()

    black_list = []
    white_list = []

    files = []
    for dirpath, dirnames, filenames in ignore_walk.ignore_walk(root, black_list, white_list):
        for filename in filenames:
            files.append(os.path.relpath(os.path.join(dirpath, filename), root).replace("\\", "/"))

    print("done checking now")
    # Verify the file in the ignored deeply nested subtree is not included
    assert "dir3/level1/level2/level3/level4/file_to_be_ignored.txt" not in files
    # Verify other files are included
    assert "dir3/file_at_root.txt" in files
    assert "dir3/level1/file_at_level1.txt" in files
    assert "dir3/level1/level2/file_at_level2.txt" in files


@pytest.fixture
def setup_symlink_loop_structure_with_gitignore():
    with TemporaryDirectory() as tmpdirname:
        print(f"Temporary directory created at: {tmpdirname}")
        # Directory structure:
        # tmpdirname/
        #   dir1/
        #     file1.txt
        #     nested/
        #       file_nested.txt
        #   dir2/
        #     .gitignore  # This file will ignore the symlink_loop_dir
        #     subdir1/
        #       file_subdir1.txt
        #     subdir2/  # This directory contains the symlink pointing back to dir2, creating a potential loop
        #       symlink_loop_dir -> ../..
        #   dir3/
        #     file_dir3.txt

        # Create directories
        os.makedirs(os.path.join(tmpdirname, "dir1", "nested"))
        os.makedirs(os.path.join(tmpdirname, "dir2", "subdir1"))
        os.makedirs(os.path.join(tmpdirname, "dir2", "subdir2"))
        os.makedirs(os.path.join(tmpdirname, "dir3"))

        # Create files
        pathlib.Path(os.path.join(tmpdirname, "dir1", "file1.txt")).touch()
        pathlib.Path(os.path.join(tmpdirname, "dir1", "nested", "file_nested.txt")).touch()
        pathlib.Path(os.path.join(tmpdirname, "dir2", "subdir1", "file_subdir1.txt")).touch()
        pathlib.Path(os.path.join(tmpdirname, "dir3", "file_dir3.txt")).touch()

        # Create symlinks
        symlink_loop_dir = os.path.join(tmpdirname, "dir2", "subdir2", "symlink_loop_dir")
        os.symlink(os.path.join(tmpdirname, "dir2"), symlink_loop_dir)

        # Add .gitignore in dir2 to ignore symlink_loop_dir
        gitignore_path = os.path.join(tmpdirname, "dir2", ".gitignore")
        with open(gitignore_path, 'w') as f:
            f.write("subdir2/symlink_loop_dir\n")

        yield tmpdirname

def test_symlink_loop_with_gitignore(setup_symlink_loop_structure_with_gitignore):
    root = setup_symlink_loop_structure_with_gitignore
    black_list = []
    white_list = []

    visited = set()
    try:
        for dirpath, dirnames, filenames in ignore_walk.ignore_walk(root, black_list, white_list):
            # Normalize path to handle symlinks and avoid duplicates
            normalized_path = os.path.normpath(dirpath)
            if normalized_path in visited:
                continue
            visited.add(normalized_path)
            for filename in filenames:
                assert os.path.isfile(os.path.join(dirpath, filename))
        # If the loop completes without error, the symlink loop and .gitignore handling are successful
        assert True
    except RecursionError:
        # If a RecursionError is caught, it means ignore_walk entered an infinite loop due to symlinks
        assert False, "RecursionError caught: Symlink loop handling failed."