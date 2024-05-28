import pytest
from gpt_automation.Ignore_match import IgnoreMatch

# Sample test class for IgnoreMatch
class TestIgnoreMatch:
    @pytest.fixture
    def base_pattern_pairs(self):
        return [
          # ('.', 'captcha_decoder*'),  # Ignore paths including 'captcha_decoder'
            ('.', 'tests/*'),  # Ignore paths including 'tests'
           # ('utils', '*.log')  # Ignore log files inside utils directory
        ]

    @pytest.fixture
    def ignore_match(self, base_pattern_pairs):
        return IgnoreMatch(base_pattern_pairs)

    def test_match_ignore(self, ignore_match):
        # Assuming IgnoreMatch.match method checks for matches within the current directory and subdirectories
       # assert ignore_match.match("./captcha_decoder.py")  # Should ignore
       # assert ignore_match.match("utils/error.log")  # Should ignore based on directory-specific pattern
        assert ignore_match.match("./tests/utils_test.py")  # Should ignore

    def test_no_match(self, ignore_match):
        # Paths that do not match any ignore pattern
        assert not ignore_match.match("main.py")  # Should not ignore
        assert not ignore_match.match("utils/debug.py")  # Should not ignore, different file type

    def test_has_matches(self, ignore_match):
        # Check if the IgnoreMatch instance correctly identifies that it has active patterns
        assert ignore_match.has_matches()

    def test_empty_patterns(self):
        # Testing with no patterns
        empty_ignore = IgnoreMatch([])
        assert not empty_ignore.has_matches()  # No patterns, should return False

# Optionally, add more tests for edge cases, complex patterns, or handling of relative vs absolute paths
