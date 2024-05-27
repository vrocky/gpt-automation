import pytest
from gpt_automation.utils.gitignore_parser2 import GitIgnoreRule, _normalize_path  # Make sure to adjust the import based on your actual module structure
import pytest

# Test class for GitIgnoreRule
class TestGitIgnoreRule:
    @pytest.fixture
    def base_path(self):
        return 'C:/Projects/MyProject'

    @pytest.mark.parametrize("pattern, file_path, expected", [
        # Simple wildcard tests
        ("*.py", 'C:/Projects/MyProject/src/main.py', True),
        ("*.py", 'C:/Projects/MyProject/src/main.java', False),
        # Directory specific wildcard
        ("/src/*.py", 'C:/Projects/MyProject/src/main.py', True),
        ("/src/*.py", 'C:/Projects/MyProject/tests/main.py', False),

        # Subdirectory patterns
        ("src", 'C:/Projects/MyProject/src/main.py', True),
        ("src/", 'C:/Projects/MyProject/src/utils/helper.py', True),
        ("src/", 'C:/Projects/MyProject/tests/main.py', False),

        # Deep nested patterns
        ("docs/**/*.pdf", 'C:/Projects/MyProject/docs/build/output.pdf', True),
        ("docs/**/*.pdf", 'C:/Projects/MyProject/docs/source/intro.pdf', True),
        ("docs/**/*.pdf", 'C:/Projects/MyProject/docs/readme.md', False),
        # Root directory pattern
        ("/README.md", 'C:/Projects/MyProject/README.md', True),
        ("/README.md", 'C:/Projects/MyProject/subdir/README.md', False),
    ])
    def test_gitignore_rule(self, base_path, pattern, file_path, expected):
        source = ('direct input', 1)
        gitignore_rule = GitIgnoreRule(pattern, base_path, source, negation=False)
        normalized_path = _normalize_path(file_path)
        assert gitignore_rule.match(normalized_path) == expected, f"Pattern '{pattern}' failed for path '{file_path}'"

# Execute these tests with pytest to verify the GitIgnoreRule behavior.



class TestGitIgnoreRuleEdgeCases:
    @pytest.fixture
    def base_path(self):
        return 'C:/Users/vinit/OneDrive/Desktop/gpt-automation/tests'

    def test_failing_case(self, base_path):
        # This is the pattern and file path that led to unexpected results.
        pattern = '*tests*'
        file_path = 'C:/Users/vinit/OneDrive/Desktop/gpt-automation/tests/tests/utils_test.py'
        source = ('direct input', 1)

        # Creating a GitIgnoreRule instance with the specified pattern
        gitignore_rule = GitIgnoreRule(pattern, base_path, source, negation=False)
        normalized_path = _normalize_path(file_path)

        # Expected to match but initially did not. Let's verify and analyze.
        expected = True
        match_result = gitignore_rule.match(normalized_path)
        assert match_result == expected, f"Expected '{normalized_path}' to match pattern '{pattern}' but it did not. Match result was {match_result}"

# Execute this test with pytest to specifically check for the reported issue.
