import os
import shutil
import unittest
from unittest.mock import patch

from gpt_automation.main import main
from gpt_automation.impl.setting.paths import PathManager

class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        # Setup test directories
        self.test_root = os.path.join(os.path.dirname(__file__), 'test_e2e_root')
        self.test_prompt_dir = os.path.join(self.test_root, 'sample_project')
        
        # Clean and create test directories
        for dir_path in [self.test_root, self.test_prompt_dir]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
            os.makedirs(dir_path)
        
        # Create sample project structure
        self._create_sample_project()

    def _create_sample_project(self):
        """Create a sample project structure for testing"""
        sample_files = {
            'src/main.py': 'def main():\n    print("Hello World")\n\nif __name__ == "__main__":\n    main()',
            'src/utils.py': 'def helper():\n    return "helper function"',
            'tests/test_main.py': 'def test_main():\n    assert True',
            'README.md': '# Sample Project\nThis is a test project.',
            'requirements.txt': 'pytest>=7.0.0\npytest-cov>=4.0.0'
        }
        
        for file_path, content in sample_files.items():
            full_path = os.path.join(self.test_prompt_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)

    def tearDown(self):
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)

    @patch('pyperclip.copy')
    def test_full_workflow(self, mock_copy):
        """Test the complete workflow: init followed by prompt command"""
        # Step 1: Initialize the project
        with patch('sys.argv', ['gpt-automation', 'init', '--root_dir', self.test_root]):
            main()
        
        # Verify initialization
        path_manager = PathManager(self.test_root)
        self.assertTrue(os.path.exists(os.path.join(self.test_root, '.gpt')))
        self.assertTrue(os.path.exists(path_manager.settings_base_dir))
        
        # Step 2: Generate prompts for the project
        with patch('sys.argv', [
            'gpt-automation', 
            'prompt', 
            '--root_dir', self.test_root,
            '--prompt_dir', self.test_prompt_dir
        ]):
            main()
        
        # Verify prompt generation
        mock_copy.assert_called_once()
        copied_content = mock_copy.call_args[0][0]
        
        # Check if directory structure is included
        self.assertIn('Directory Structure:', copied_content)
        self.assertIn('src/', copied_content)
        self.assertIn('tests/', copied_content)
        self.assertIn('README.md', copied_content)
        
        # Check if file contents are included
        self.assertIn('File Contents:', copied_content)
        self.assertIn('def main():', copied_content)
        self.assertIn('# Sample Project', copied_content)

    @patch('pyperclip.copy')
    def test_selective_prompt_generation(self, mock_copy):
        """Test generating only directory structure or only content"""
        # Initialize first
        with patch('sys.argv', ['gpt-automation', 'init', '--root_dir', self.test_root]):
            main()

        # Test directory structure only
        with patch('sys.argv', [
            'gpt-automation', 
            'prompt', 
            '--root_dir', self.test_root,
            '--prompt_dir', self.test_prompt_dir,
            '--dir'
        ]):
            main()
        
        dir_content = mock_copy.call_args[0][0]
        self.assertIn('Directory Structure:', dir_content)
        self.assertNotIn('File Contents:', dir_content)

        # Test file content only
        mock_copy.reset_mock()
        with patch('sys.argv', [
            'gpt-automation', 
            'prompt', 
            '--root_dir', self.test_root,
            '--prompt_dir', self.test_prompt_dir,
            '--content'
        ]):
            main()
        
        file_content = mock_copy.call_args[0][0]
        self.assertNotIn('Directory Structure:', file_content)
        self.assertIn('File Contents:', file_content)

    def test_error_handling(self):
        """Test error handling for incorrect usage"""
        # Test prompting before initialization
        with patch('sys.argv', [
            'gpt-automation', 
            'prompt', 
            '--root_dir', self.test_root,
            '--prompt_dir', self.test_prompt_dir
        ]):
            main()
            # Verify no .gpt directory exists
            self.assertFalse(os.path.exists(os.path.join(self.test_root, '.gpt')))

        # Test with invalid prompt directory
        with patch('sys.argv', [
            'gpt-automation', 
            'prompt', 
            '--root_dir', self.test_root,
            '--prompt_dir', '/invalid/path'
        ]):
            main()

if __name__ == '__main__':
    unittest.main()
