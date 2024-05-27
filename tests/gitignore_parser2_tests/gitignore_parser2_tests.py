import unittest
from gitignore_parser2.parser import parse_patterns_with_base_dir

class TestParsePatternsWithBaseDir(unittest.TestCase):

    def test_basic_matching(self):
        base_dir = "C:/projects"
        patterns = ["*.py", "test/"]
        matcher = parse_patterns_with_base_dir(base_dir, patterns)
        self.assertTrue(matcher("C:/projects/example.py"))
        self.assertTrue(matcher("C:/projects/test/example.txt"))
        self.assertFalse(matcher("C:/projects/example.txt"))

    def test_no_matching(self):
        base_dir = "C:/projects"
        patterns = ["*.js", "node_modules/"]
        matcher = parse_patterns_with_base_dir(base_dir, patterns)
        self.assertFalse(matcher("C:/projects/example.py"))
        self.assertFalse(matcher("C:/projects/src/example.py"))

    def test_negation_rules(self):
        base_dir = "C:/projects"
        patterns = ["*", "!README.md"]
        matcher = parse_patterns_with_base_dir(base_dir, patterns)
        self.assertTrue(matcher("C:/projects/example.py"))
        self.assertFalse(matcher("C:/projects/README.md"))

    def test_path_normalization(self):
        base_dir = "C:/projects//"
        patterns = ["src/*.py"]
        matcher = parse_patterns_with_base_dir(base_dir, patterns)
        self.assertTrue(matcher("C:/projects/src/example.py"))
        self.assertFalse(matcher("C:/projects/docs/example.py"))

    def test_empty_patterns(self):
        base_dir = "C:/projects"
        patterns = []
        matcher = parse_patterns_with_base_dir(base_dir, patterns)
        self.assertFalse(matcher("C:/projects/example.py"))

if __name__ == '__main__':
    unittest.main()
