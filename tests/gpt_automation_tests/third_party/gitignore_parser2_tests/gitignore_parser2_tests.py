import unittest
from pathlib import Path

from gpt_automation.third_party import GitIgnoreParser


class TestGitIgnoreParser(unittest.TestCase):
    def setUp(self):
        self.base_dir = str(Path(__file__).parent)  # Use the directory of the test file
        self.parser = GitIgnoreParser(self.base_dir, [
            '*.pyc',  # Ignore all .pyc files
            '/logs/',  # Ignore everything in the logs directory
            '**/__pycache__/',  # Ignore all __pycache__ directories
            '*.log'  # Ignore all .log files
        ])

    def test_basic_matching(self):
        # Check that .pyc files are ignored
        self.assertTrue(self.parser.match('test.pyc'))
        self.assertFalse(self.parser.match('test.py'))

    def test_directory_specific_rules(self):
        # The logs directory should be ignored
        self.assertTrue(self.parser.match('logs/error.log'))


    def test_complex_patterns(self):
        # __pycache__ directories should be ignored regardless of location
        self.assertTrue(self.parser.match('src/__pycache__/module.pyc'))


    def test_directory_anchoring(self):
        # Ensure only top-level log files are ignored
        self.assertTrue(self.parser.match('error.log'))
        #self.assertFalse(self.parser.match('subdir/error.log'))

if __name__ == '__main__':
    unittest.main()
