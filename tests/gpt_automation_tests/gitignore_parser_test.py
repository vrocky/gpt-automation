import re

import pytest
from gitignore_parser import rule_from_pattern, _normalize_path, IgnoreRule  # Make sure to adjust the import based on your actual module structure

# Test cases for rule_from_pattern
@pytest.mark.parametrize("pattern, base_path, expected_negation, expected_regex, expected_directory_only", [
    ("*.py", None, False, '.*\\.py$', False),
    ("!*.py", None, True, '.*\\.py$', False),
    ("/src/*.py", "/myproject", False, '^src\\/.*\\.py$', False),
    ("src/", "/myproject", False, '^src\\/$', True),
    ("**/*.bak", "/myproject", False, '(^|\\/).*\\.bak$', False),
    ("/*.c", "/myproject", False, '^\\.c$', False),
    ("*.py[cod]", "/myproject", False, '.*\\.py[cod]$', False),
    ("debug/", "/myproject", False, '^debug\\/$', True)
])

def test_rule_from_pattern(pattern, base_path, expected_negation, expected_regex, expected_directory_only):
    base_path = _normalize_path(base_path) if base_path else None
    rule = rule_from_pattern(pattern, base_path=str(base_path) if base_path else None)

    assert rule is not None, "Rule should not be None"
    assert rule.negation == expected_negation, f"Negation should be {expected_negation}"
    assert rule.regex is not None, "Regex should not be None"
    assert isinstance(rule.regex, re.Pattern), "Regex should be a compiled regex object"
    assert rule.regex.pattern == expected_regex, f"Expected regex pattern '{expected_regex}', got '{rule.regex.pattern}'"

def test_comments_and_blank_lines():
    # Comments and blank lines should not create any rules
    assert rule_from_pattern("# This is a comment", None) is None, "Comments should not create a rule"
    assert rule_from_pattern("", None) is None, "Blank lines should not create a rule"

def test_rule_matching():
    # Test the matching functionality of a sample rule
    base_path = "/myproject"
    rule = rule_from_pattern("*.py", base_path)
    assert rule.match(_normalize_path(f"{base_path}/test.py")), "Should match the '*.py' pattern"
    assert not rule.match(_normalize_path(f"{base_path}/test.pyx")), "Should not match the '*.py' pattern"
# You might need to extend tests to cover more edge cases or configurations.
