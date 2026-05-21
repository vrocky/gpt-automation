"""
Test domain layer filter logic.

Pure business logic tests — no I/O, no external dependencies.
"""

import pytest
from pathlib import Path
from gpt_automation.domain.filters.file_filter import FileFilter, NullFilter, ChainedFilter


class AlwaysAcceptFilter(FileFilter):
    """Test filter that always accepts."""

    def accepts(self, file_path: Path) -> bool:
        return True

    def should_traverse_directory(self, dir_path: Path) -> bool:
        return True


class NeverAcceptFilter(FileFilter):
    """Test filter that never accepts."""

    def accepts(self, file_path: Path) -> bool:
        return False

    def should_traverse_directory(self, dir_path: Path) -> bool:
        return True


class TestNullFilter:
    """Test NullFilter (accept everything)."""

    def test_accepts_all_files(self):
        f = NullFilter()
        assert f.accepts(Path('file.txt'))
        assert f.accepts(Path('dir/file.py'))
        assert f.accepts(Path('.hidden'))

    def test_traverses_all_directories(self):
        f = NullFilter()
        assert f.should_traverse_directory(Path('any/dir'))
        assert f.should_traverse_directory(Path('.git'))


class TestChainedFilter:
    """Test ChainedFilter (AND logic)."""

    def test_all_accept_returns_true(self):
        """All filters accept → file accepted."""
        f1 = AlwaysAcceptFilter()
        f2 = AlwaysAcceptFilter()
        chained = ChainedFilter([f1, f2])

        assert chained.accepts(Path('file.txt'))

    def test_one_rejects_returns_false(self):
        """One filter rejects → file rejected."""
        f1 = AlwaysAcceptFilter()
        f2 = NeverAcceptFilter()
        chained = ChainedFilter([f1, f2])

        assert not chained.accepts(Path('file.txt'))

    def test_requires_at_least_one_filter(self):
        """ChainedFilter requires at least one filter."""
        with pytest.raises(ValueError):
            ChainedFilter([])

    def test_directory_traversal_requires_all(self):
        """All filters must allow directory traversal."""
        f1 = AlwaysAcceptFilter()
        f2 = AlwaysAcceptFilter()
        chained = ChainedFilter([f1, f2])

        assert chained.should_traverse_directory(Path('dir'))
