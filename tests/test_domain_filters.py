"""
Test domain layer filter logic.

Pure business logic tests — no I/O, no external dependencies.
All tests run in milliseconds with zero mock setup.
"""

import pytest
from pathlib import Path
from gpt_automation.domain.filters.file_filter import (
    FileFilter,
    AllFilters,
    IncludeEverythingFilter,
)


# ── helpers ──────────────────────────────────────────────────────────────────

class AcceptAll(FileFilter):
    def should_include_file(self, f: Path) -> bool:
        return True

    def should_include_directory(self, d: Path) -> bool:
        return True


class RejectAll(FileFilter):
    def should_include_file(self, f: Path) -> bool:
        return False

    def should_include_directory(self, d: Path) -> bool:
        return False


# ── IncludeEverythingFilter ───────────────────────────────────────────────────

class TestIncludeEverythingFilter:
    """Pass-through filter accepts all files and directories."""

    def test_accepts_all_files(self):
        f = IncludeEverythingFilter()
        assert f.should_include_file(Path('file.txt'))
        assert f.should_include_file(Path('deep/nested/path.py'))
        assert f.should_include_file(Path('.hidden'))

    def test_traverses_all_directories(self):
        f = IncludeEverythingFilter()
        assert f.should_include_directory(Path('any/dir'))
        assert f.should_include_directory(Path('.git'))
        assert f.should_include_directory(Path('.'))


# ── AllFilters ────────────────────────────────────────────────────────────────

class TestAllFilters:
    """AND logic — every filter must agree."""

    def test_all_accept_means_include(self):
        assert AllFilters([AcceptAll(), AcceptAll()]).should_include_file(Path('f'))

    def test_one_reject_means_exclude(self):
        assert not AllFilters([AcceptAll(), RejectAll()]).should_include_file(Path('f'))

    def test_all_reject_means_exclude(self):
        assert not AllFilters([RejectAll(), RejectAll()]).should_include_file(Path('f'))

    def test_directory_all_must_agree(self):
        assert AllFilters([AcceptAll(), AcceptAll()]).should_include_directory(Path('d'))
        assert not AllFilters([AcceptAll(), RejectAll()]).should_include_directory(Path('d'))

    def test_requires_at_least_one_filter(self):
        with pytest.raises(ValueError, match="at least one"):
            AllFilters([])

    def test_single_filter_works(self):
        assert AllFilters([AcceptAll()]).should_include_file(Path('f'))
        assert not AllFilters([RejectAll()]).should_include_file(Path('f'))
