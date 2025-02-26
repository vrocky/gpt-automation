import os
import shutil
import unittest
from gpt_automation.plugins.ignore_plugin.plugin import IgnorePlugin
from gpt_automation.impl.directory_walker import DirectoryWalker
from gpt_automation.impl.setting.paths import PathManager
from gpt_automation.impl.visitor.basevisitor import BaseVisitor


class TestFileVisitor(BaseVisitor):
    """Helper class to collect files during traversal"""
    def __init__(self, plugin_visitor=None):
        self.plugin_visitor = plugin_visitor
        self.visited_files = []
        self.visited_dirs = []

    def before_traverse_directory(self, directory_path):
        if self.plugin_visitor:
            self.plugin_visitor.before_traverse_directory(directory_path)

    def enter_directory(self, directory_path):
        if self.plugin_visitor and self.plugin_visitor.should_visit_subdirectory(directory_path):
            self.visited_dirs.append(directory_path)
            self.plugin_visitor.enter_directory(directory_path)

    def visit_file(self, file_path):
        if self.plugin_visitor and self.plugin_visitor.should_visit_file(file_path):
            self.visited_files.append(file_path)
            self.plugin_visitor.visit_file(file_path)

    def leave_directory(self, directory_path):
        if self.plugin_visitor:
            self.plugin_visitor.leave_directory(directory_path)

    def should_visit_file(self, file_path):
        if self.plugin_visitor:
            return self.plugin_visitor.should_visit_file(file_path)
        return True

    def should_visit_subdirectory(self, directory_path):
        if self.plugin_visitor:
            return self.plugin_visitor.should_visit_subdirectory(directory_path)
        return True


class TestIgnorePlugin(unittest.TestCase):
    def setUp(self):
        # Create test directory structure
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_ignore_root')
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)

        # Initialize path manager
        self.path_manager = PathManager(self.test_dir)
        self.plugin_settings_path = self.path_manager.get_plugin_settings_path(
            'gpt_automation',
            'ignore_plugin'
        )
        os.makedirs(self.plugin_settings_path, exist_ok=True)

        # Create test file structure
        self.create_test_files()

        # Initialize plugin
        self.plugin = IgnorePlugin()
        self.profiles = ['test_profile']

    def create_test_files(self):
        """Create a test directory structure with various files and .gptignore"""
        # Create some test files and directories
        files = {
            'main.py': 'print("Hello")',
            'test.txt': 'text content',
            '.gptignore': '*.txt\nignored_dir/\n',
            'src/module.py': 'def test(): pass',
            'src/.gptignore': '*.pyc\n',
            'ignored_dir/secret.txt': 'secret',
            'ignored_dir/important.py': 'data'
        }

        for file_path, content in files.items():
            full_path = os.path.join(self.test_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_basic_ignore_functionality(self):
        """Test the basic ignore functionality with .gptignore files"""
        # Initialize plugin
        self.plugin.init(self.plugin_settings_path, self.test_dir, self.profiles)
        
        # Get plugin visitors
        plugin_visitors = self.plugin.get_visitors(self.test_dir)
        self.assertTrue(len(plugin_visitors) > 0)
        
        # Create collector with plugin visitor
        collector = TestFileVisitor(plugin_visitors[0])
        walker = DirectoryWalker(self.test_dir, visitor=collector)
        
        # Walk and collect files
        list(walker.walk())
        
        # Verify results using normalized paths
        def normalize_path(path):
            return os.path.normpath(os.path.join(self.test_dir, path))
        
        # Files that should be visited
        self.assertIn(normalize_path('main.py'), collector.visited_files)
        self.assertIn(normalize_path('src/module.py'), collector.visited_files)
        
        # Files that should be ignored
        self.assertNotIn(normalize_path('test.txt'), collector.visited_files)
        self.assertNotIn(normalize_path('ignored_dir/secret.txt'), collector.visited_files)
        self.assertNotIn(normalize_path('ignored_dir/important.py'), collector.visited_files)

    def test_early_directory_exclusion(self):
        """Test that ignored directories are not scanned at all"""
        # Create a large directory structure that should be ignored
        node_modules = os.path.join(self.test_dir, 'node_modules')
        os.makedirs(node_modules)
        
        # Create many files in node_modules to verify it's not scanned
        for i in range(100):
            subdir = os.path.join(node_modules, f'package_{i}')
            os.makedirs(subdir)
            with open(os.path.join(subdir, 'package.json'), 'w') as f:
                f.write('{"name": "test"}')

        # Create .gptignore with node_modules exclusion
        with open(os.path.join(self.test_dir, '.gptignore'), 'w') as f:
            f.write('node_modules/\n')

        # Initialize plugin
        self.plugin.init(self.plugin_settings_path, self.test_dir, self.profiles)
        plugin_visitors = self.plugin.get_visitors(self.test_dir)
        
        # Track which directories are actually scanned
        scanned_dirs = set()
        visited_files = set()
        
        class TrackingVisitor(TestFileVisitor):
            def enter_directory(self, directory_path):
                scanned_dirs.add(directory_path)
                super().enter_directory(directory_path)
                
            def visit_file(self, file_path):
                visited_files.add(file_path)
                super().visit_file(file_path)

        # Walk the directory
        collector = TrackingVisitor(plugin_visitors[0])
        walker = DirectoryWalker(self.test_dir, visitor=collector)
        list(walker.walk())

        # Verify node_modules was not scanned
        self.assertNotIn(node_modules, scanned_dirs,
            "node_modules directory should not be scanned")
        
        # Verify no files from node_modules were visited
        node_modules_files = [f for f in visited_files if 'node_modules' in f]
        self.assertEqual(len(node_modules_files), 0,
            "No files from node_modules should be visited")

if __name__ == '__main__':
    unittest.main()
