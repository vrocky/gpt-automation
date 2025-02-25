import os
import pytest
from gpt_automation.ignore_walk import traverse_with_filters
from tempfile import TemporaryDirectory
import pathlib


@pytest.fixture
def setup_profile_directory_structure():
    with TemporaryDirectory() as tmpdirname:
        print(f"Temporary directory created at: {tmpdirname}")

        # Setup directories
        os.makedirs(os.path.join(tmpdirname, "project"))
        os.makedirs(os.path.join(tmpdirname, "project", "logs"))
        os.makedirs(os.path.join(tmpdirname, "project", "data"))

        # Create sample files
        pathlib.Path(os.path.join(tmpdirname, "project", "logs", "error.log")).touch()
        pathlib.Path(os.path.join(tmpdirname, "project", "data", "data1.csv")).touch()

        # Create a .gptignore file with profile-specific patterns
        gptignore_content = """*.tmp
      
        [dev]
        # Development-specific ignores
        logs/
        
        [prod]
        # Production-specific ignores
        data/
        """
        pathlib.Path(os.path.join(tmpdirname, "project", ".gptignore")).write_text(gptignore_content)

        yield tmpdirname


def test_ignore_with_profile_dev(setup_profile_directory_structure):
    project_root = os.path.join(setup_profile_directory_structure, "project")
    profile_name = "dev"

    files = []
    for dirpath, dirnames, filenames in traverse_with_filters(project_root, ["*.gpt2*"], ["*.csv","*.txt","*.log"], profile_names=[profile_name]):
        for filename in filenames:
            files.append(os.path.relpath(os.path.join(dirpath, filename), project_root).replace("\\", "/"))

    assert "logs/error.log" not in files, "Logs should be ignored in dev profile"
    assert "data/data1.csv" in files, "Data files should not be ignored in dev profile"


def test_ignore_with_profile_prod(setup_profile_directory_structure):
    project_root = os.path.join(setup_profile_directory_structure, "project")
    profile_name = "prod"

    files = []
    for dirpath, dirnames, filenames in traverse_with_filters(project_root, ["*.gpt2*"], ["*.csv","*.txt","*.log"], profile_names=[profile_name]):
        for filename in filenames:
            files.append(os.path.relpath(os.path.join(dirpath, filename), project_root).replace("\\", "/"))

    assert "data/data1.csv" not in files, "Data files should be ignored in prod profile"
    assert "logs/error.log" in files, "Logs should not be ignored in prod profile"


def test_ignore_without_profile(setup_profile_directory_structure):
    project_root = os.path.join(setup_profile_directory_structure, "project")

    files = []
    for dirpath, dirnames, filenames in traverse_with_filters(project_root, ["*.gpt2*"], ["*.csv","*.txt","*.log"]):
        print(dirpath)
        print(dirnames)
        print(filenames)
        for filename in filenames:

            files.append(os.path.relpath(os.path.join(dirpath, filename), project_root).replace("\\", "/"))

    assert "logs/error.log" in files, "Logs should not be ignored without a specific profile"
    assert "data/data1.csv" in files, "Data files should not be ignored without a specific profile"
