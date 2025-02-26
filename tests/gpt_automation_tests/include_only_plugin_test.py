import os
import shutil
import unittest
from gpt_automation.plugins.include_only_plugin.plugin import IncludeOnlyPlugin
from gpt_automation.impl.directory_walker import DirectoryWalker
from gpt_automation.impl.setting.paths import PathManager
from gpt_automation.impl.visitor.basevisitor import BaseVisitor


class TestFileVisitor(BaseVisitor):
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


class TestIncludeOnlyPlugin(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_include_only_root')
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)

        self.path_manager = PathManager(self.test_dir)
        self.plugin_settings_path = self.path_manager.get_plugin_settings_path(
            'gpt_automation',
            'include_only_plugin'
        )
        os.makedirs(self.plugin_settings_path, exist_ok=True)

        # Create simple test structure
        self.create_test_files()
        
        self.plugin = IncludeOnlyPlugin()
        self.profiles = ['test_profile']

    def create_test_files(self):
        """Create minimal test file structure"""
        files = {
            '.gptincludeonly': '*.py',  # Simple pattern to include all Python files
            'test.py': 'print("test")',
            'test.txt': 'text content'
        }

        for file_path, content in files.items():
            full_path = os.path.join(self.test_dir, file_path)
            with open(full_path, 'w') as f:
                f.write(content)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_basic_include_only(self):
        """Test simplest include-only functionality"""
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
        
        # Only .py file should be included
        self.assertIn(normalize_path('test.py'), collector.visited_files)
        self.assertNotIn(normalize_path('test.txt'), collector.visited_files)

if __name__ == '__main__':
    unittest.main()
