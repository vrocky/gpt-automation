import unittest
from pathlib import Path

from gpt_automation.third_party import GitIgnoreParser


class TestGitIgnoreParser(unittest.TestCase):
    def setUp(self):
        self.base_dir = str(Path("").resolve())  # Setting up the base directory
        self.patterns = ['tests/*']
        self.parser = GitIgnoreParser(self.base_dir, self.patterns)



    def test_no_match_for_utils_test_py(self):
        # Specific test case from your request
        file_path = './tests/utils_test.py'
        self.assertTrue(self.parser.match(file_path))

if __name__ == '__main__':
    unittest.main()
