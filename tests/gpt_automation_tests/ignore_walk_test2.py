import pytest
from gpt_automation import ignore_walk
from tempfile import TemporaryDirectory
import os
import pathlib

@pytest.fixture
def setup_complex_directory_structure():
    with TemporaryDirectory() as tmpdirname:
        os.makedirs(os.path.join(tmpdirname, "project", "src"))
        os.makedirs(os.path.join(tmpdirname, "project", "build"))
        pathlib.Path(os.path.join(tmpdirname, "project", ".gptignore")).write_text("build/\n")
        pathlib.Path(os.path.join(tmpdirname, "project", "src", ".gptignore")).write_text("*.log\n")
        pathlib.Path(os.path.join(tmpdirname, "project", "src", "src.py")).touch()
        pathlib.Path(os.path.join(tmpdirname, "project", "src", "debug.log")).touch()
        pathlib.Path(os.path.join(tmpdirname, "project", "build", "output.o")).touch()
        yield tmpdirname

def test_ignore_directories(setup_complex_directory_structure):
    root = setup_complex_directory_structure
    files = []
    for dirpath, dirnames, filenames in ignore_walk.traverse_with_filters(root, [], []):
        for filename in filenames:
            files.append(os.path.relpath(os.path.join(dirpath, filename), root).replace("\\", "/"))
    assert "project/src/src.py" in files
    assert "project/src/debug.log" not in files
    assert "project/build/output.o" not in files  # Because 'build/' is ignored

def test_malformed_ignore_file(setup_complex_directory_structure):
    root = setup_complex_directory_structure
    # Introduce malformed ignore entry
    malformed_path = os.path.join(root, "project", "src", ".gptignore")
    with open(malformed_path, 'a') as f:
        f.write("???\n")
    files = []
    for dirpath, dirnames, filenames in ignore_walk.traverse_with_filters(root, [], []):
        for filename in filenames:
            files.append(os.path.relpath(os.path.join(dirpath, filename), root).replace("\\", "/"))
    # Even with malformed entry, other rules should still work
    assert "project/src/src.py" in files
    assert "project/src/debug.log" not in files

def test_no_ignore_file_handling(setup_complex_directory_structure):
    root = setup_complex_directory_structure
    # Remove ignore file
    os.remove(os.path.join(root, "project", ".gptignore"))
    files = []
    for dirpath, dirnames, filenames in ignore_walk.traverse_with_filters(root, [], []):
        for filename in filenames:
            files.append(os.path.relpath(os.path.join(dirpath, filename), root).replace("\\", "/"))
    # Now 'build/output.o' should be included as no ignore file present
    assert "project/build/output.o" in files

def test_symlink_handling(setup_symlink_loop_structure_with_gitignore):
    root = setup_symlink_loop_structure_with_gitignore
    files = []
    visited = set()
    for dirpath, dirnames, filenames in ignore_walk.traverse_with_filters(root, [], []):
        normalized_path = os.path.normpath(dirpath)
        if normalized_path in visited:
            continue
        visited.add(normalized_path)
        for filename in filenames:
            files.append(os.path.relpath(os.path.join(dirpath, filename), root).replace("\\", "/"))
    assert "dir2/subdir1/file_subdir1.txt" in files
    # The file in the symlinked directory should be ignored based on .gitignore
    assert "dir2/subdir2/symlink_loop_dir/dir2/subdir1/file_subdir1.txt" not in files
