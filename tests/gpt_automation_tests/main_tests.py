import os
import pytest
import tempfile
import shutil
import subprocess
import sys





def setup_directory_structure(base_dir, structure):
    """
    Creates a directory structure with files and their contents based on the provided structure dictionary.
    """
    for path, content in structure.items():
        if content is None:  # Create directory
            os.makedirs(os.path.join(base_dir, *path), exist_ok=True)
        else:  # Create file with content
            dir_path = os.path.join(base_dir, *path[:-1])
            os.makedirs(dir_path, exist_ok=True)
            with open(os.path.join(dir_path, path[-1]), 'w') as file:
                file.write(content)




def test_init_with_multiple_profiles(initialized_temp_project_dir):
    """
    Tests the initialization of multiple profiles to ensure profiles are set up correctly.
    """
    profile_names = ["profile1", "profile2"]
    stdout, stderr = run_gpt_command(initialized_temp_project_dir, f"init {' '.join(profile_names)}")
    print("STDOUT:", stdout)
    print("STDERR:", stderr)
    for profile in profile_names:
        profile_dir = os.path.join(initialized_temp_project_dir, ".gpt2", profile)  # Adjusted path
        assert os.path.exists(profile_dir), f"Profile directory {profile_dir} does not exist"
        assert os.path.isfile(os.path.join(profile_dir, "black_list.txt")), "Blacklist file is missing"
        assert os.path.isfile(os.path.join(profile_dir, "white_list.txt")), "Whitelist file is missing"



def test_prompt_dir_only(initialized_temp_project_dir):
    """
    Tests generating a directory structure prompt to verify that directories are correctly listed.
    """
    stdout, stderr = run_gpt_command(initialized_temp_project_dir, "prompt --dir")
    assert "src/" in stdout, "Directory 'src/' should be listed in the prompt"
    assert "tests/" in stdout, "Directory 'tests/' should be listed in the prompt"
    assert "error" not in stderr.lower(), "There should be no errors"




def test_error_on_nonexistent_profile(initialized_temp_project_dir):
    """
    Tests error handling when a non-existent profile is specified.
    """
    stdout, stderr = run_gpt_command(initialized_temp_project_dir, "prompt --dir --profiles non_existent_profile")
    assert "error" in stderr.lower(), "An error message should be displayed for a non-existent profile"




def create_symlink(source, link_name):
    """
    Creates a symbolic link pointing to source named link_name.
    """
    os.symlink(source, link_name)

def create_junction(source, link_name):
    """
    Creates a junction point from link_name to source.
    Requires Windows.
    """
    subprocess.run(f'cmd /c mklink /J "{link_name}" "{source}"', shell=True, check=True)

@pytest.fixture
def initialized_temp_project_dir():
    temp_dir = tempfile.mkdtemp()
    project_structure = {
        (("src",), None),
        (("tests",), None),
        (("src", "main.py"), "# Main application file\n"),
        (("tests", "test_main.py"), "# Main test file\n"),
    }
    setup_directory_structure(temp_dir, dict(project_structure))
    run_gpt_command(temp_dir, 'init')
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def temp_project_dir_with_symlink_loop():
    temp_dir = tempfile.mkdtemp()
    project_structure = {
        (("dir1", "nested"), None),
        (("dir2", "subdir1"), None),
        (("dir2", "subdir2"), None),
        (("dir3",), None),
        (("dir1", "file1.txt"), "File 1 content\n"),
        (("dir1", "nested", "file_nested.txt"), "Nested file content\n"),
        (("dir2", "subdir1", "file_subdir1.txt"), "Subdir 1 file content\n"),
        (("dir3", "file_dir3.txt"), "Dir 3 file content\n"),
        (("dir2", ".gitignore"), "symlink_loop_dir\n"),
    }
    setup_directory_structure(temp_dir, dict(project_structure))
    create_symlink(os.path.join(temp_dir, "dir2"), os.path.join(temp_dir, "dir2", "subdir2", "symlink_loop_dir"))
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def temp_project_dir_with_junction_loop():
    temp_dir = tempfile.mkdtemp()
    project_structure = {
        (("dir1", "nested"), None),
        (("dir2", "subdir1"), None),
        (("dir2", "subdir2"), None),
        (("dir3",), None),
        (("dir1", "file1.txt"), "File 1 content\n"),
        (("dir1", "nested", "file_nested.txt"), "Nested file content\n"),
        (("dir2", "subdir1", "file_subdir1.txt"), "Subdir 1 file content\n"),
        (("dir3", "file_dir3.txt"), "Dir 3 file content\n"),
        (("dir2", ".gitignore"), "junction_loop_dir\n"),
    }
    setup_directory_structure(temp_dir, dict(project_structure))
    if sys.platform == "win32":
        junction_path = os.path.join(temp_dir, "dir2", "subdir2", "junction_loop_dir")
        create_junction(os.path.join(temp_dir, "dir2"), junction_path)
    yield temp_dir
    shutil.rmtree(temp_dir)

def run_gpt_command(project_dir, command):
    """
    Executes a command in the context of project_dir using the gpt_automation tool,
    capturing and returning the command's output.
    """
    original_cwd = os.getcwd()
    os.chdir(project_dir)
    try:
        result = subprocess.run([sys.executable, '-m', 'gpt_automation.main'] + command.split(),
                                capture_output=True, text=True, check=True)
    finally:
        os.chdir(original_cwd)
    return result.stdout, result.stderr

@pytest.mark.parametrize("fixture", [
    "temp_project_dir_with_symlink_loop",
    pytest.param("temp_project_dir_with_junction_loop",
                 marks=pytest.mark.skipif(sys.platform != "win32", reason="Junction loops are specific to Windows")),
])
def test_prompt_dir_structure_with_loops(fixture, request):
    project_dir = request.getfixturevalue(fixture)

    # Initialize the directory using the gpt_automation tool
    stdout_init, stderr_init = run_gpt_command(project_dir, "init")
    assert "error" not in stderr_init.lower(), "Initialization failed with an error"

    stdout, stderr = run_gpt_command(project_dir, "prompt --dir")

    # Expected elements to verify in the stdout
    expected_elements = ["file1.txt", "file_nested.txt",
                          "file_subdir1.txt",
                          "file_dir3.txt"]

    # Verify expected elements are present in the command output
    for element in expected_elements:
        assert element in stdout, f"Expected '{element}' to be part of the output: {stdout}"

    # Verify no unexpected errors are present
    assert "error" not in stderr.lower(), f"Unexpected errors found in stderr: {stderr}"



