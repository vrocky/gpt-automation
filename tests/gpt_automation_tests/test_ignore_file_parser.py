import os
from gpt_automation.ignore_file_parser import parse_gptignore_file, collect_patterns_from_ignore_files

# Use a temporary directory for creating test files
import tempfile

def create_temp_gptignore_file(contents):
    """
    Helper function to create a temporary .gptignore file with specified contents.
    Returns the path to the created file.
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.gptignore')
    temp_file.write(contents)
    temp_file.close()
    return temp_file.name

def test_parse_gptignore_global_patterns():
    """
    Test that global patterns are correctly identified.
    """
    contents = """
    # Global patterns
    pattern1
    pattern2
    """
    temp_file_path = create_temp_gptignore_file(contents)
    global_patterns, profile_patterns = parse_gptignore_file(temp_file_path)
    os.unlink(temp_file_path)  # Clean up temporary file
    assert 'pattern1' in global_patterns
    assert 'pattern2' in global_patterns
    assert not profile_patterns  # No profile-specific patterns should be identified

def test_parse_gptignore_profile_specific_patterns():
    """
    Test that profile-specific patterns are correctly identified.
    """
    contents = """
    # Global patterns
    pattern1

    [Profile1]
    pattern2
    """
    temp_file_path = create_temp_gptignore_file(contents)
    global_patterns, profile_patterns = parse_gptignore_file(temp_file_path, profile_name="Profile1")
    os.unlink(temp_file_path)  # Clean up temporary file
    assert 'pattern1' in global_patterns
    assert 'pattern2' in profile_patterns

def test_collect_patterns_from_ignore_files():
    """
    Test collecting patterns from .gptignore files considering global and profile-specific patterns.
    """
    contents = """
    # Global patterns
    pattern1

    [Profile1]
    pattern2
    """
    temp_file_path = create_temp_gptignore_file(contents)
    directory_path = os.path.dirname(temp_file_path)
    pattern_pairs = collect_patterns_from_ignore_files(directory_path, [os.path.basename(temp_file_path)], profile_name="Profile1")
    os.unlink(temp_file_path)  # Clean up temporary file
    patterns = [pattern for _, pattern in pattern_pairs]
    assert 'pattern1' in patterns
    assert 'pattern2' in patterns

# Additional test cases can be added as needed to cover more scenarios
