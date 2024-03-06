import os
import pytest
import tempfile
import shutil
import subprocess
import sys


@pytest.fixture
def initialized_temp_project_dir():
    # Create a temporary directory as the project root
    temp_dir = tempfile.mkdtemp()

    # Setup dummy project structure
    os.makedirs(os.path.join(temp_dir, "src"))
    os.makedirs(os.path.join(temp_dir, "tests"))
    with open(os.path.join(temp_dir, "src", "main.py"), "w") as f:
        f.write("# Main application file\n")
    with open(os.path.join(temp_dir, "tests", "test_main.py"), "w") as f:
        f.write("# Main test file\n")

    # Initialize the directory using the gpt_automation tool
    original_cwd = os.getcwd()
    os.chdir(temp_dir)  # Change to temporary directory
    try:
        subprocess.check_call([sys.executable, '-m', 'gpt_automation.main', 'init'])
    finally:
        os.chdir(original_cwd)  # Restore original working directory

    yield temp_dir
    shutil.rmtree(temp_dir)  # Cleanup


def run_gpt_command(project_dir, command):
    original_cwd = os.getcwd()
    os.chdir(project_dir)  # Change to project directory
    try:
        # Using subprocess.run() to capture output
        result = subprocess.run([sys.executable, '-m', 'gpt_automation.main'] + command.split(),
                                capture_output=True, text=True)
        # Print captured output to stdout/stderr so it can be captured by capsys
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
    finally:
        os.chdir(original_cwd)  # Restore original working directory

def test_prompt_dir_structure(initialized_temp_project_dir, capsys):
    run_gpt_command(initialized_temp_project_dir, "prompt-dir --path .")
    captured = capsys.readouterr()  # Now this should capture the output from the subprocess

    # Key elements to verify in the output
    expected_elements = ["src/", "main.py", "tests/", "test_main.py"]

    for element in expected_elements:
        assert element in captured.out, f"Expected '{element}' to be part of the output"

    # Optionally, verify the absence of certain elements
    unexpected_elements = ["ShouldNotBePresent"]
    for element in unexpected_elements:
        assert element not in captured.out, f"Unexpected '{element}' found in the output"


import os
import pytest
import tempfile
import shutil
import subprocess
import sys


@pytest.fixture
def temp_project_dir_with_symlink_loop():
    # Create a temporary directory as the project root
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
    temp_dir = tempfile.mkdtemp()
    print("temp_dir")
    print(temp_dir)

    # Setup a complex directory structure with a potential symlink loop
    os.makedirs(os.path.join(temp_dir, "dir1", "nested"))
    os.makedirs(os.path.join(temp_dir, "dir2", "subdir1"))
    os.makedirs(os.path.join(temp_dir, "dir2", "subdir2"))
    os.makedirs(os.path.join(temp_dir, "dir3"))

    with open(os.path.join(temp_dir, "dir1", "file1.txt"), "w") as f:
        f.write("File 1 content\n")

    with open(os.path.join(temp_dir, "dir1", "nested", "file_nested.txt"), "w") as f:
        f.write("Nested file content\n")

    with open(os.path.join(temp_dir, "dir2", "subdir1", "file_subdir1.txt"), "w") as f:
        f.write("Subdir 1 file content\n")

    with open(os.path.join(temp_dir, "dir3", "file_dir3.txt"), "w") as f:
        f.write("Dir 3 file content\n")

    with open(os.path.join(temp_dir, "dir2", ".gitignore"), "w") as f:
        f.write("symlink_loop_dir\n")

    # Creating a symlink loop
    os.symlink(os.path.join(temp_dir, "dir2"), os.path.join(temp_dir, "dir2", "subdir2", "symlink_loop_dir"))

    yield temp_dir
    shutil.rmtree(temp_dir)  # Cleanup after the test


def run_gpt_command(project_dir, command):
    original_cwd = os.getcwd()
    os.chdir(project_dir)  # Change to project directory
    try:
        result = subprocess.run([sys.executable, '-m', 'gpt_automation.main'] + command.split(),
                                capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
    finally:
        os.chdir(original_cwd)  # Restore original working directory



@pytest.fixture
def temp_project_dir_with_junction_loop():
    temp_dir = tempfile.mkdtemp()
    print("temp_dir")
    print(temp_dir)

    # Setup directory structure
    os.makedirs(os.path.join(temp_dir, "dir1", "nested"))
    os.makedirs(os.path.join(temp_dir, "dir2", "subdir1"))
    os.makedirs(os.path.join(temp_dir, "dir2", "subdir2"))
    os.makedirs(os.path.join(temp_dir, "dir3"))

    with open(os.path.join(temp_dir, "dir1", "file1.txt"), "w") as f:
        f.write("File 1 content\n")

    with open(os.path.join(temp_dir, "dir1", "nested", "file_nested.txt"), "w") as f:
        f.write("Nested file content\n")

    with open(os.path.join(temp_dir, "dir2", "subdir1", "file_subdir1.txt"), "w") as f:
        f.write("Subdir 1 file content\n")

    with open(os.path.join(temp_dir, "dir3", "file_dir3.txt"), "w") as f:
        f.write("Dir 3 file content\n")

    with open(os.path.join(temp_dir, "dir2", ".gitignore"), "w") as f:
        f.write("junction_loop_dir\n")

    # Creating a junction loop instead of symlink loop
    junction_path = os.path.join(temp_dir, "dir2", "subdir2", "junction_loop_dir")
    # Use cmd to create junction; note this command requires Windows
    subprocess.run(f'cmd /c mklink /J "{junction_path}" "{os.path.join(temp_dir, "dir2")}"', shell=True)

    yield temp_dir
    shutil.rmtree(temp_dir)  # Cleanup after the test



import pytest
import platform  # To check the operating system

@pytest.mark.parametrize("fixture", [
    ("temp_project_dir_with_symlink_loop"),
    pytest.param("temp_project_dir_with_junction_loop", marks=pytest.mark.skipif(platform.system() != "Windows", reason="Junction loops are specific to Windows")),
])
def test_prompt_dir_structure_with_loops(fixture, request, capsys):
    # Dynamically get the fixture based on the parameter
    project_dir = request.getfixturevalue(fixture)

    # Initialize the directory using the gpt_automation tool
    run_gpt_command(project_dir, "init")

    # Now run the `prompt-dir` command and expect it to handle the loop gracefully
    run_gpt_command(project_dir, "prompt-dir --path .")
    captured = capsys.readouterr()

    print(captured.out)

    # Verify the output contains the expected directories and files,
    # and it has successfully navigated the loop without getting stuck.
    expected_elements = ["dir1/", "nested/", "file1.txt", "file_nested.txt",
                         "dir2/", "subdir1/", "file_subdir1.txt",
                         "dir3/", "file_dir3.txt"]

    for element in expected_elements:
        assert element in captured.out, f"Expected '{element}' to be part of the output"

    # Ensure the loop did not cause any unexpected errors or infinite recursion
    assert "RecursionError" not in captured.out and "RecursionError" not in captured.err, "Unexpected RecursionError, indicating a potential loop issue."
