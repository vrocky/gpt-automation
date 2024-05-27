import unittest
from pathlib import Path

from gitignore_parser2.parser2 import GitIgnoreParser


class TestGitIgnoreParser(unittest.TestCase):
    def setUp(self):
        self.base_dir = str(Path(__file__).parent)  # Use the directory of the test file
        self.parser = GitIgnoreParser(self.base_dir, [
            '*.pyc',
            '!main.py',
            '/logs/',
            '**/__pycache__/',
            '*.log',
            '!important.log',
            '/project/deep/'
        ])

    def test_basic_matching(self):
        self.assertTrue(self.parser.match('test.pyc'))
        self.assertFalse(self.parser.match('test.py'))
        self.assertFalse(self.parser.match('main.py'))

    def test_negation_rules(self):
        self.assertTrue(self.parser.match('important.log'))
        self.assertFalse(self.parser.match('output.log'))

    def test_directory_specific_rules(self):
        self.assertTrue(self.parser.match('logs/error.log'))
        self.assertFalse(self.parser.match('error.log'))

    def test_complex_patterns(self):
        self.assertTrue(self.parser.match('src/__pycache__/module.pyc'))
        self.assertFalse(self.parser.match('__pycache__/module.pyc'))

    def test_directory_anchoring(self):
        self.assertTrue(self.parser.match('project/deep/file.txt'))
        self.assertFalse(self.parser.match('extra/project/deep/file.txt'))

if __name__ == '__main__':
    unittest.main()
