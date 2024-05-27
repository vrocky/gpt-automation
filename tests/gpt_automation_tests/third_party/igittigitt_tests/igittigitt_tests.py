import pathlib
from igittigitt import IgnoreParser
import pytest


@pytest.fixture
def setup_ignore_parser():
    # Create a parser instance
    parser = IgnoreParser()
    # Path to a sample .gitignore file (you need to create this in your test directory)
    gitignore_path = pathlib.Path('sample.gitignore')
    # Write sample rules to the .gitignore file
    with gitignore_path.open('w') as file:
        file.write('*.pyc\n')
        file.write('__pycache__/\n')

    # Parse the .gitignore rules
    parser.parse_rule_file(gitignore_path)
    return parser


# Define tests using the setup
def test_file_ignored(setup_ignore_parser):
    # Example file paths
    pyc_file = pathlib.Path('/home/project/main.pyc')
    py_file = pathlib.Path('/home/project/main.py')

    # Test cases
    assert setup_ignore_parser.match(py_file) == False, "Should not ignore .py files"
    assert setup_ignore_parser.match(pyc_file) == True, "Should ignore .pyc files"



def test_directory_ignored(setup_ignore_parser):
    # Example directory path
    pycache_dir = pathlib.Path('/home/project/__pycache__')

    # Test case
    assert setup_ignore_parser.match(pycache_dir) == True, "Should ignore __pycache__ directory"


# Run the tests
if __name__ == '__main__':
    pytest.main()
