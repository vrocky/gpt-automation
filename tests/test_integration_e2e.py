"""
End-to-end integration tests using AppContainer.

These tests verify real workflows: init → configure → generate prompts
with actual filesystem operations (using temp directories).
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from gpt_automation.container import AppContainer


class TestInitializeProjectEndToEnd(unittest.TestCase):
    """Test project initialization workflow."""

    def setUp(self):
        """Create a temporary project directory for testing."""
        self.temp_dir = tempfile.mkdtemp(prefix='gpt_test_')
        self.project_root = Path(self.temp_dir).resolve()  # Normalize path

    def tearDown(self):
        """Clean up temporary directory."""
        if self.project_root.exists():
            # Close any open file handles before removing
            import gc
            gc.collect()
            # Use ignore_errors to handle Windows file locking issues
            shutil.rmtree(self.project_root, ignore_errors=True)

    def test_init_creates_gpt_directory_structure(self):
        """Verify init command creates all necessary directories."""
        container = AppContainer(self.project_root)
        success = container.initialize_project.run([])

        self.assertTrue(success)
        self.assertTrue((self.project_root / '.gpt').exists())
        self.assertTrue((self.project_root / '.gpt' / 'settings').exists())
        self.assertTrue((self.project_root / '.gpt' / 'logs').exists())
        self.assertTrue((self.project_root / '.gpt' / 'config').exists())

    def test_init_creates_settings_file(self):
        """Verify init creates base_settings.json with defaults."""
        container = AppContainer(self.project_root)
        success = container.initialize_project.run([])

        self.assertTrue(success)
        settings_file = self.project_root / '.gpt' / 'settings' / 'base_settings.json'
        self.assertTrue(settings_file.exists())

        # Verify file is readable and contains expected structure
        import json
        with open(settings_file) as f:
            settings = json.load(f)
        self.assertIn('plugins', settings)
        self.assertTrue(len(settings['plugins']) > 0)

    def test_init_with_profiles_creates_profile_dirs(self):
        """Verify profiles create profile-specific config directories."""
        container = AppContainer(self.project_root)
        success = container.initialize_project.run(['backend', 'frontend'])

        self.assertTrue(success)
        self.assertTrue((self.project_root / '.gpt' / 'config' / 'backend').exists())
        self.assertTrue((self.project_root / '.gpt' / 'config' / 'frontend').exists())

    def test_init_creates_gitignore_template(self):
        """Verify init creates .gitignore template for filtering."""
        container = AppContainer(self.project_root)
        success = container.initialize_project.run([])

        self.assertTrue(success)
        gitignore = self.project_root / '.gpt' / '.gitignore'
        self.assertTrue(gitignore.exists())


class TestGeneratePromptsEndToEnd(unittest.TestCase):
    """Test prompt generation workflow."""

    def setUp(self):
        """Create a temporary project with test files."""
        self.temp_dir = tempfile.mkdtemp(prefix='gpt_test_')
        self.project_root = Path(self.temp_dir)

        # Initialize the project first
        container = AppContainer(self.project_root)
        container.initialize_project.run([])

        # Create test file structure
        (self.project_root / 'src').mkdir()
        (self.project_root / 'tests').mkdir()
        (self.project_root / 'docs').mkdir()

        (self.project_root / 'src' / 'main.py').write_text('def main():\n    pass\n')
        (self.project_root / 'src' / 'utils.py').write_text('def helper():\n    pass\n')
        (self.project_root / 'tests' / 'test_main.py').write_text('def test_main():\n    pass\n')
        (self.project_root / 'README.md').write_text('# Test Project\n')
        (self.project_root / 'docs' / 'guide.md').write_text('# User Guide\n')

    def tearDown(self):
        """Clean up temporary directory."""
        if self.project_root.exists():
            # Close any open file handles before removing
            import gc
            gc.collect()
            # Use ignore_errors to handle Windows file locking issues
            shutil.rmtree(self.project_root, ignore_errors=True)

    def test_generate_prompts_returns_directory_tree(self):
        """Verify generate_prompts returns directory tree."""
        container = AppContainer(self.project_root)
        result = container.generate_prompts.run(
            work_dir=self.project_root,
            profiles=[],
            include_tree=True,
            include_contents=False,
        )

        self.assertIsNotNone(result.directory_tree)
        self.assertTrue(len(result.directory_tree) > 0)
        # Directory tree should contain structure
        self.assertIn('src', result.directory_tree)
        self.assertIn('tests', result.directory_tree)

    def test_generate_prompts_returns_file_contents(self):
        """Verify generate_prompts returns file contents."""
        container = AppContainer(self.project_root)
        result = container.generate_prompts.run(
            work_dir=self.project_root,
            profiles=[],
            include_tree=False,
            include_contents=True,
        )

        self.assertIsNotNone(result.file_contents)
        self.assertTrue(len(result.file_contents) > 0)
        # File contents should include our test code
        self.assertIn('main.py', result.file_contents)
        self.assertIn('def main():', result.file_contents)

    def test_generate_prompts_returns_both(self):
        """Verify generate_prompts can return both tree and contents."""
        container = AppContainer(self.project_root)
        result = container.generate_prompts.run(
            work_dir=self.project_root,
            profiles=[],
            include_tree=True,
            include_contents=True,
        )

        self.assertIsNotNone(result.directory_tree)
        self.assertIsNotNone(result.file_contents)
        self.assertTrue(len(result.directory_tree) > 0)
        self.assertTrue(len(result.file_contents) > 0)

    def test_filtering_excludes_ignored_files(self):
        """Verify filtering works: create .gptignore and verify exclusion."""
        # Create .gptignore to exclude tests/
        gpt_ignore = self.project_root / '.gpt' / '.gptignore'
        gpt_ignore.write_text('tests/\n')

        container = AppContainer(self.project_root)
        result = container.generate_prompts.run(
            work_dir=self.project_root,
            profiles=[],
            include_tree=True,
            include_contents=True,
        )

        # Directory tree should NOT include tests/
        self.assertNotIn('tests', result.directory_tree)
        # File contents should NOT include test_main.py
        self.assertNotIn('test_main.py', result.file_contents)
        # But should include src/
        self.assertIn('src', result.directory_tree)
        self.assertIn('main.py', result.file_contents)

    def test_filtering_with_include_only(self):
        """Verify include-only filter: only include specified files."""
        # Create .gptincludeonly to only include src/
        include_only = self.project_root / '.gpt' / '.gptincludeonly'
        include_only.write_text('src/\n')

        container = AppContainer(self.project_root)
        result = container.generate_prompts.run(
            work_dir=self.project_root,
            profiles=[],
            include_tree=True,
            include_contents=True,
        )

        # Should only include src/ directory
        self.assertIn('src', result.directory_tree)
        self.assertNotIn('tests', result.directory_tree)
        self.assertNotIn('docs', result.directory_tree)
        self.assertNotIn('README', result.directory_tree)
        # File contents should only have src files
        self.assertIn('main.py', result.file_contents)
        self.assertNotIn('test_main.py', result.file_contents)

    def test_generate_prompts_with_subdirectory(self):
        """Verify generate_prompts can work on a subdirectory."""
        container = AppContainer(self.project_root)
        result = container.generate_prompts.run(
            work_dir=self.project_root / 'src',
            profiles=[],
            include_tree=True,
            include_contents=True,
        )

        # Should contain src files
        self.assertIn('main.py', result.directory_tree)
        self.assertIn('utils.py', result.directory_tree)
        # Should NOT contain test or doc files
        self.assertNotIn('test_main.py', result.directory_tree)
        self.assertNotIn('guide.md', result.directory_tree)

    def test_empty_directory_returns_empty_result(self):
        """Verify handling of empty directories."""
        empty_dir = self.project_root / 'empty'
        empty_dir.mkdir()

        container = AppContainer(self.project_root)
        result = container.generate_prompts.run(
            work_dir=empty_dir,
            profiles=[],
            include_tree=True,
            include_contents=True,
        )

        # Empty directory should have minimal tree
        self.assertIsNotNone(result.directory_tree)
        # File contents should be empty
        self.assertEqual(len(result.file_contents.strip()), 0)


class TestCompleteWorkflowEndToEnd(unittest.TestCase):
    """Test the complete workflow: init → generate prompts."""

    def setUp(self):
        """Create a temporary project directory."""
        self.temp_dir = tempfile.mkdtemp(prefix='gpt_test_')
        self.project_root = Path(self.temp_dir)

        # Create project structure
        (self.project_root / 'app').mkdir()
        (self.project_root / 'app' / 'main.py').write_text('print("hello")\n')
        (self.project_root / '.gitignore').write_text('__pycache__/\n*.pyc\n')

    def tearDown(self):
        """Clean up temporary directory."""
        if self.project_root.exists():
            # Close any open file handles before removing
            import gc
            gc.collect()
            # Use ignore_errors to handle Windows file locking issues
            shutil.rmtree(self.project_root, ignore_errors=True)

    def test_complete_workflow(self):
        """Test: init project → generate prompts → verify output."""
        container = AppContainer(self.project_root)

        # Step 1: Initialize
        init_success = container.initialize_project.run([])
        self.assertTrue(init_success)
        self.assertTrue((self.project_root / '.gpt').exists())

        # Step 2: Generate prompts (should work now)
        result = container.generate_prompts.run(
            work_dir=self.project_root,
            profiles=[],
            include_tree=True,
            include_contents=True,
        )

        # Step 3: Verify results
        self.assertIsNotNone(result.directory_tree)
        self.assertIsNotNone(result.file_contents)
        self.assertTrue(len(result.directory_tree) > 0)
        self.assertTrue(len(result.file_contents) > 0)
        self.assertIn('app', result.directory_tree)
        self.assertIn('main.py', result.file_contents)
        self.assertIn('print("hello")', result.file_contents)

    def test_workflow_is_idempotent(self):
        """Test: running init twice doesn't break anything."""
        container1 = AppContainer(self.project_root)
        success1 = container1.initialize_project.run([])
        self.assertTrue(success1)

        # Run init again (should be safe)
        container2 = AppContainer(self.project_root)
        success2 = container2.initialize_project.run([])
        self.assertTrue(success2)

        # Generate prompts should still work
        result = container2.generate_prompts.run(
            work_dir=self.project_root,
            profiles=[],
            include_tree=True,
            include_contents=True,
        )
        self.assertIsNotNone(result.directory_tree)


if __name__ == '__main__':
    unittest.main()
