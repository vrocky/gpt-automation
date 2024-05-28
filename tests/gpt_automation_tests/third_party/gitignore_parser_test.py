import unittest

from gpt_automation.third_party.gitignore_parser2.parser2 import GitIgnoreParser


class TestGitIgnoreParser(unittest.TestCase):
    def test_match_no_ignore(self):
        # Test when there are no ignore rules
        parser = GitIgnoreParser(base_dir='C:/path/to/base/dir', patterns=[])
        self.assertFalse(parser.match('C:/path/to/file.txt'))

    def test_match_simple_ignore(self):
        # Test when there is a simple ignore rule
        parser = GitIgnoreParser(base_dir='C:/path/to/', patterns=['*.txt'])
        self.assertTrue(parser.match('C:/path/to/file.txt'))
        self.assertFalse(parser.match('C:/path/to/file.py'))

    def test_match_directory_ignore(self):
        # Test when ignoring a directory
        parser = GitIgnoreParser(base_dir='C:/path/to/base/dir', patterns=['dir_to_ignore/*'])
        self.assertTrue(parser.match('C:/path/to/base/dir/dir_to_ignore/file.txt'))
        self.assertFalse(parser.match('C:/path/to/base/dir/not_ignored_dir/file.txt'))



    def test_additional_case(self):
        # Test additional case you requested
        base_path = '.'
        pattern = 'tests/*'
        parser = GitIgnoreParser(base_dir=base_path, patterns=[pattern])
        self.assertTrue(parser.match('./tests/utils_test.py'))

if __name__ == '__main__':
    unittest.main()
