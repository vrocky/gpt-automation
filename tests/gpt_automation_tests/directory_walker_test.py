import os
import shutil
import unittest
from unittest.mock import MagicMock

from gpt_automation.impl.directory_walker import DirectoryWalker, DefaultVisitor
from gpt_automation.impl.visitor.basevisitor import BaseVisitor


class TestDirectoryWalker(unittest.TestCase):
    def setUp(self):
        # Create test directory structure
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_walker')
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        # Create test file structure
        self.test_files = {
            f'file1.txt': 'content1',
            f'file2.py': 'content2',
            f'subdir1{os.path.sep}file3.md': 'content3',
            f'subdir1{os.path.sep}subdir2{os.path.sep}file4.json': 'content4',
            f'subdir1{os.path.sep}file5.yml': 'content5',
            f'.hidden{os.path.sep}hidden.txt': 'hidden'
        }
        
        for file_path, content in self.test_files.items():
            full_path = os.path.join(self.test_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)

    def tearDown(self):
        from gpt_automation.impl.logging_utils import close_logger_handlers
        close_logger_handlers('DirectoryWalker')
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_default_visitor_walk(self):
        """Test walking with default visitor that accepts everything"""
        walker = DirectoryWalker(self.test_dir)
        visited_files = list(walker.walk())
        
        # Normalize paths for comparison
        visited_files = {os.path.normpath(f) for f in visited_files}
        expected_files = {os.path.normpath(os.path.join(self.test_dir, f)) for f in self.test_files.keys()}
        self.assertEqual(visited_files, expected_files)

    def test_filtered_visitor(self):
        """Test walking with a visitor that filters certain files/directories"""
        class FilterVisitor(DefaultVisitor):
            def should_visit_file(self, file_path):
                return not file_path.endswith('.py')
                
            def should_visit_subdirectory(self, directory_path):
                return not os.path.basename(directory_path).startswith('.')

        walker = DirectoryWalker(self.test_dir, FilterVisitor())
        visited_files = list(walker.walk())
        
        # Verify .py files and .hidden directory are excluded
        for file_path in visited_files:
            self.assertFalse(file_path.endswith('.py'))
            self.assertFalse(os.path.sep + '.hidden' + os.path.sep in file_path)

    def test_visitor_callbacks(self):
        """Test that visitor callbacks are called in correct order"""
        visitor = MagicMock(spec=DefaultVisitor)
        visitor.should_visit_file.return_value = True
        visitor.should_visit_subdirectory.return_value = True
        
        walker = DirectoryWalker(self.test_dir, visitor)
        list(walker.walk())  # Consume generator
        
        # Verify visitor methods were called
        visitor.before_traverse_directory.assert_called_once_with(self.test_dir)
        visitor.enter_directory.assert_called()
        visitor.leave_directory.assert_called()
        visitor.visit_file.assert_called()
        
        # Get all method calls excluding boolean checks
        call_order = [name for name, args, _ in visitor.mock_calls 
                     if name not in ('should_visit_file', 'should_visit_subdirectory')]
        
        # First call should be before_traverse
        self.assertEqual(call_order[0], 'before_traverse_directory')
        # Enter should come before visit_file for same directory
        enter_idx = call_order.index('enter_directory')
        visit_idx = call_order.index('visit_file')
        self.assertLess(enter_idx, visit_idx)
        # Leave should come after visit_file
        leave_idx = len(call_order) - call_order[::-1].index('leave_directory') - 1
        self.assertGreater(leave_idx, visit_idx)

    def test_cyclic_directory_handling(self):
        """Test handling of cyclic directory structures"""
        # Create a directory cycle using symlinks
        cycle_dir = os.path.join(self.test_dir, 'cycle')
        os.makedirs(cycle_dir)
        os.symlink(cycle_dir, os.path.join(cycle_dir, 'loop'))
        
        walker = DirectoryWalker(self.test_dir)
        visited_files = list(walker.walk())
        
        # Verify no infinite loop occurred
        self.assertTrue(len(visited_files) < 100)  # Reasonable upper bound

    def test_empty_directory(self):
        """Test walking an empty directory"""
        empty_dir = os.path.join(self.test_dir, 'empty')
        os.makedirs(empty_dir)
        
        walker = DirectoryWalker(empty_dir)
        visited_files = list(walker.walk())
        
        self.assertEqual(len(visited_files), 0)

    def test_error_handling(self):
        """Test handling of permission errors and missing files"""
        errors = []
        
        class ErrorVisitor(DefaultVisitor):
            def visit_file(self, file_path):
                errors.append(file_path)
                raise Exception("Test error")
        
        walker = DirectoryWalker(self.test_dir, ErrorVisitor())
        
        # Should complete walk despite errors
        visited_files = list(walker.walk())
        self.assertTrue(len(visited_files) > 0)
        self.assertTrue(len(errors) > 0)  # Verify errors were caught

    def test_nested_directory_order(self):
        """Test that nested directories are processed in the correct order"""
        visited_paths = []
        test_dir = self.test_dir  # Capture test_dir in closure
        
        class OrderVisitor(DefaultVisitor):
            def visit_file(self, file_path):
                visited_paths.append(os.path.relpath(file_path, test_dir))
                
        walker = DirectoryWalker(self.test_dir, OrderVisitor())
        list(walker.walk())  # Execute the walk
        
        # Group files by directory
        files_by_dir = {}
        for path in visited_paths:
            dir_name = os.path.dirname(path) or '.'
            files_by_dir.setdefault(dir_name, []).append(path)
        
        # Verify each directory's files are processed together
        current_files = None
        for path in visited_paths:
            dir_name = os.path.dirname(path) or '.'
            if dir_name not in files_by_dir:
                continue
                
            # When we hit a new directory
            if current_files is None or dir_name != os.path.dirname(current_files[0]):
                # Verify previous directory was fully processed
                if current_files:
                    remaining = set(current_files) - set(visited_paths[:visited_paths.index(path)])
                    self.assertEqual(len(remaining), 0, 
                        f"Files in directory {os.path.dirname(current_files[0])} were not fully processed before moving to {dir_name}")
                current_files = files_by_dir.pop(dir_name)

        # Verify last directory was fully processed
        if current_files:
            remaining = set(current_files) - set(visited_paths)
            self.assertEqual(len(remaining), 0, 
                "Last directory was not fully processed")

    def test_early_directory_exclusion(self):
        """Test that ignored directories are not scanned at all"""
        # Create a directory structure where some directories should be ignored
        ignore_dir = os.path.join(self.test_dir, 'node_modules')
        os.makedirs(ignore_dir)
        
        # Create some files in the ignored directory
        for i in range(10):
            with open(os.path.join(ignore_dir, f'file{i}.txt'), 'w') as f:
                f.write('content')

        visited_paths = set()
        scanned_dirs = set()
        
        class ScanTrackingVisitor(DefaultVisitor):
            def should_visit_subdirectory(self, directory_path):
                return 'node_modules' not in directory_path
                
            def enter_directory(self, directory_path):
                scanned_dirs.add(directory_path)
                
            def visit_file(self, file_path):
                visited_paths.add(file_path)

        walker = DirectoryWalker(self.test_dir, ScanTrackingVisitor())
        list(walker.walk())  # Execute the walk

        # Verify that ignored directory was not scanned
        self.assertNotIn(ignore_dir, scanned_dirs, 
            "Walker should not scan ignored directory")
        
        # Verify no files from ignored directory were visited
        ignored_files = [f for f in visited_paths if 'node_modules' in f]
        self.assertEqual(len(ignored_files), 0,
            "No files from ignored directory should be visited")

if __name__ == '__main__':
    unittest.main()
