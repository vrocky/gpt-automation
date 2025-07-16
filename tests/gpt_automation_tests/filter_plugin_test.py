import os
import shutil
import unittest
from gpt_automation.plugins.filter_plugin.plugin import BlacklistWhitelistPlugin
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


class TestFilterPlugin(unittest.TestCase):
    def setUp(self):
        # Create test directory structure
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_filter_root')
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
        # Create base directory structure
        os.makedirs(self.test_dir)
        
        # Initialize path manager and get plugin settings path
        self.path_manager = PathManager(self.test_dir)
        self.plugin_settings_path = self.path_manager.get_plugin_settings_path(
            'gpt_automation', 
            'filter_plugin'
        )
        
        # Ensure plugin settings directory exists
        os.makedirs(self.plugin_settings_path, exist_ok=True)

        # Create test file structure
        self.create_test_files()
        
        # Initialize plugin
        self.plugin = BlacklistWhitelistPlugin()
        self.profiles = ['test_profile']
        
        # Setup plugin configuration files
        self.setup_plugin_config()

    def setup_plugin_config(self):
        """Setup plugin configuration files"""
        # Create sample config directory if it doesn't exist
        sample_config_dir = os.path.join(self.plugin_settings_path, "sample_config")
        os.makedirs(sample_config_dir, exist_ok=True)
        
        # Helper function to write list file
        def write_list_file(path, items):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write('\n'.join(items))

        # Create sample config files
        write_list_file(
            os.path.join(sample_config_dir, 'black_list.txt'),
            ['*.pyc', '__pycache__', '.git', 'node_modules']
        )
        write_list_file(
            os.path.join(sample_config_dir, 'white_list.txt'),
            ['*.py', '*.txt']
        )

        # Create default config files
        write_list_file(
            os.path.join(self.plugin_settings_path, 'black_list.txt'),
            ['*.pyc', '__pycache__', '.git', 'node_modules']
        )
        write_list_file(
            os.path.join(self.plugin_settings_path, 'white_list.txt'),
            ['*.py', '*.txt']
        )

        # Create profile config
        profile_dir = os.path.join(self.plugin_settings_path, 'test_profile')
        write_list_file(
            os.path.join(profile_dir, 'black_list.txt'),
            ['*.pyc', '__pycache__']
        )
        write_list_file(
            os.path.join(profile_dir, 'white_list.txt'),
            ['*.py']
        )

    def create_test_files(self):
        """Create a test directory structure with various file types"""
        test_files = {
            os.path.join('test.py'): 'print("Hello")',
            os.path.join('test.txt'): 'Text content',
            os.path.join('test.pyc'): 'Binary content',
            os.path.join('subdir1', 'test1.py'): 'def test1(): pass',
            os.path.join('subdir1', 'test1.txt'): 'More text',
            os.path.join('subdir2', 'test2.py'): 'def test2(): pass',
            os.path.join('subdir2', '__pycache__', 'cache.pyc'): 'cache content',
            os.path.join('.git', 'config'): 'git config',
            os.path.join('node_modules', 'package.json'): 'npm package'
        }

        for file_path, content in test_files.items():
            full_path = os.path.join(self.test_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)

    def tearDown(self):
        from gpt_automation.impl.logging_utils import close_logger_handlers
        close_logger_handlers('BlacklistWhitelistPlugin')
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_complete_plugin_workflow(self):
        """Test the complete plugin workflow - init, configure, and use"""
        try:
            # Initialize plugin with settings path
            self.plugin.init(self.plugin_settings_path, self.test_dir, self.profiles)
            self.assertTrue(os.path.exists(self.plugin_settings_path))
            
            # Get plugin visitors
            plugin_visitors = self.plugin.get_visitors(self.test_dir)
            self.assertTrue(len(plugin_visitors) > 0)
            
            # Create collector visitor with plugin visitor
            collector = TestFileVisitor(plugin_visitors[0])
            
            # Create directory walker
            walker = DirectoryWalker(self.test_dir, visitor=collector)
            
            # Walk and collect files
            list(walker.walk())
            
            # Verify results using normalized paths
            def normalize_path(path):
                return os.path.normpath(os.path.join(self.test_dir, path))
            
            self.assertIn(normalize_path('test.py'), collector.visited_files)
            self.assertNotIn(normalize_path('test.pyc'), collector.visited_files)
            self.assertIn(normalize_path(os.path.join('subdir1', 'test1.py')), collector.visited_files)
            self.assertNotIn(normalize_path(os.path.join('.git', 'config')), collector.visited_files)
            
        except Exception as e:
            self.fail(f"Test failed with error: {str(e)}")

    def test_profile_configuration(self):
        """Test plugin with profile-specific configuration"""
        # Initialize with profile
        self.plugin.init(self.plugin_settings_path, self.test_dir, self.profiles)
        self.assertTrue(self.plugin.is_plugin_configured())
        
        # Get profile-specific visitors
        plugin_visitors = self.plugin.get_visitors(self.test_dir)
        self.assertTrue(len(plugin_visitors) > 0)
        
        # Create collector with plugin visitor
        collector = TestFileVisitor(plugin_visitors[0])
        walker = DirectoryWalker(self.test_dir, visitor=collector)
        
        # Walk and collect files
        list(walker.walk())
        
        # Verify profile-specific filtering using normalized paths
        def normalize_path(path):
            return os.path.normpath(os.path.join(self.test_dir, path))

        self.assertIn(normalize_path('test.py'), collector.visited_files)
        self.assertNotIn(normalize_path('test.txt'), collector.visited_files)
        self.assertNotIn(normalize_path('test.pyc'), collector.visited_files)

if __name__ == '__main__':
    unittest.main()
