import pytest
from gpt_automation.utils.gitignore_parser2 import parse_patterns_with_base_dir
import os


# Helper function to walk through files in test_data, check against patterns, and collect results
def check_patterns_and_collect_results(base_dir, matcher):
    results = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            file_path = os.path.relpath(os.path.join(root, file), start=base_dir)
            match_result = matcher(file_path)
            if match_result:
                print(f"Pattern matches: {file_path}")
            else:
                print(f"Pattern does not match: {file_path}")
            results.append((file_path, match_result))
    return results


# Fixture to setup base directory path
@pytest.fixture
def base_dir_path():
    return "./test_data"


# Test to dry run parse_patterns_with_base_dir with specific patterns
def test_parse_patterns_with_specific_patterns(base_dir_path):
    patterns = ['*.txt', '!dir_1/']
    matcher = parse_patterns_with_base_dir(base_dir_path, patterns)
    results = check_patterns_and_collect_results(base_dir_path, matcher)
    # Add assertion to validate expected results
    for file_path, matched in results:
        if 'dir_1' not in file_path and file_path.endswith('.txt'):
            assert matched, f"Expected {file_path} to match patterns"
        else:
            assert not matched, f"Expected {file_path} not to match patterns"


# Test to dry run parse_patterns_with_base_dir with empty patterns
def test_parse_patterns_with_empty_patterns(base_dir_path):
    patterns = []
    matcher = parse_patterns_with_base_dir(base_dir_path, patterns)
    results = check_patterns_and_collect_results(base_dir_path, matcher)
    # Since no patterns are provided, nothing should match
    for file_path, matched in results:
        assert not matched, f"Expected {file_path} not to match any patterns"


# Test to dry run parse_patterns_with_base_dir for negation pattern
def test_parse_patterns_with_negation_pattern(base_dir_path):
    patterns = ['!file10.txt']
    matcher = parse_patterns_with_base_dir(base_dir_path, patterns)
    results = check_patterns_and_collect_results(base_dir_path, matcher)
    # Assert based on the negation pattern
    for file_path, matched in results:
        expected_match = 'file10.txt' not in file_path
        assert matched == expected_match, f"Expected {file_path} match result to be {expected_match}"


# Test to dry run parse_patterns_with_base_dir with non-existent files
def test_parse_patterns_with_non_existent_files(base_dir_path):
    patterns = ['non_existent_file.*']
    matcher = parse_patterns_with_base_dir(base_dir_path, patterns)
    results = check_patterns_and_collect_results(base_dir_path, matcher)
    # Since the pattern specifies non-existent files, nothing should match
    for file_path, matched in results:
        assert not matched, f"Expected {file_path} not to match pattern for non-existent files"
