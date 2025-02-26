import os
import shutil
import unittest
from gpt_automation.plugins.ignore_plugin.plugin import IgnorePlugin
from gpt_automation.impl.directory_walker import DirectoryWalker
from gpt_automation.impl.setting.paths import PathManager
from gpt_automation.impl.visitor.basevisitor import BaseVisitor


class TestFileVisitor(BaseVisitor):
    def __init__(self, plugin_visitor=None):
        self.plugin_visitor = plugin_visitor
        self.visited_files = []

    def visit_file(self, file_path):
        if self.plugin_visitor and self.plugin_visitor.should_visit_file(file_path):
            self.visited_files.append(file_path)


class TestIgnorePluginConfiguration(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_ignore_root')
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        self.path_manager = PathManager(self.test_dir)
        self.plugin_settings_path = self.path_manager.get_plugin_settings_path(
            'gpt_automation', 
            'ignore_plugin'
        )
        os.makedirs(self.plugin_settings_path, exist_ok=True)
        
        self.plugin = IgnorePlugin()
        self.profiles = ['test_profile']

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_plugin_initialization(self):
        """Test if plugin initializes correctly"""
        self.plugin.init(self.plugin_settings_path, self.test_dir, self.profiles)
        self.assertTrue(self.plugin.is_plugin_configured())
        self.assertEqual(self.plugin.root_dir, self.test_dir)
        self.assertEqual(self.plugin.profile_names, self.profiles)

    def test_plugin_visitor_creation(self):
        """Test if plugin creates visitors correctly"""
        self.plugin.init(self.plugin_settings_path, self.test_dir, self.profiles)
        visitors = self.plugin.get_visitors(self.test_dir)
        self.assertIsNotNone(visitors)
        self.assertEqual(len(visitors), 1)


class TestIgnorePluginFunctionality(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_ignore_root')
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        # Create simple test files
        self.create_test_files()
        
        self.plugin = IgnorePlugin()
        self.plugin.init(self.test_dir, self.test_dir, ['test_profile'])
        self.plugin.settings_args = {
            'ignore_filenames': ['ignore.txt']
        }

    def create_test_files(self):
        """Create basic test files"""
        files = {
            'test.txt': 'test content',
            'ignore.txt': 'should be ignored',
            'keep.txt': 'should be kept'
        }
        
        for name, content in files.items():
            with open(os.path.join(self.test_dir, name), 'w') as f:
                f.write(content)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_basic_ignore_functionality(self):
        """Test if files are correctly ignored"""
        visitors = self.plugin.get_visitors(self.test_dir)
        collector = TestFileVisitor(visitors[0])
        walker = DirectoryWalker(self.test_dir, visitor=collector)
        
        list(walker.walk())
        
        visited_filenames = [os.path.basename(f) for f in collector.visited_files]
        self.assertIn('test.txt', visited_filenames)
        self.assertIn('keep.txt', visited_filenames)
        self.assertNotIn('ignore.txt', visited_filenames)


if __name__ == '__main__':
    unittest.main()
