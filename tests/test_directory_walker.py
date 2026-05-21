"""
Test DirectoryWalker with a fake FilesystemQuery.

No real files — just pure logic. Runs instantly.
"""

from pathlib import Path
from unittest.mock import MagicMock

from gpt_automation.domain.traversal.directory_reader import DirectoryWalker, FilesystemQuery
from gpt_automation.domain.filters.file_filter import IncludeEverythingFilter, AllFilters, FileFilter


def _make_filesystem(tree: dict) -> FilesystemQuery:
    """
    Build a fake FilesystemQuery from a nested dict describing the tree.

    Example:
        {'src': {'main.py': None, 'utils.py': None}, 'README.md': None}
    """
    fs = MagicMock(spec=FilesystemQuery)

    def _is_file(p: Path) -> bool:
        node = _get_node(tree, p)
        return node is None  # leaf = file

    def _is_dir(p: Path) -> bool:
        node = _get_node(tree, p)
        return isinstance(node, dict)

    def _list(p: Path) -> list[Path]:
        node = _get_node(tree, p)
        if not isinstance(node, dict):
            return []
        return [p / name for name in node.keys()]

    def _get_node(t: dict, p: Path):
        # parts relative to ROOT (strip the ROOT prefix first)
        try:
            rel_parts = list(p.relative_to(ROOT).parts)
        except ValueError:
            return None
        node = t
        for part in rel_parts:
            if not isinstance(node, dict) or part not in node:
                return None
            node = node[part]
        return node

    fs.is_file.side_effect = _is_file
    fs.is_directory.side_effect = _is_dir
    fs.list_directory.side_effect = _list
    return fs


ROOT = Path('/project')

_TREE = {
    'src': {
        'main.py': None,
        'utils.py': None,
        'tests': {
            'test_main.py': None,
        },
    },
    'README.md': None,
    '.hidden': None,
}


class TestDirectoryWalker:

    def test_collect_all_files_with_pass_through_filter(self):
        fs = _make_filesystem(_TREE)
        walker = DirectoryWalker(fs)

        files = walker.collect_matching_files(ROOT, IncludeEverythingFilter())
        names = {p.name for p in files}

        assert names == {'main.py', 'utils.py', 'test_main.py', 'README.md', '.hidden'}

    def test_filter_excludes_files(self):
        """Filter that rejects .py files excludes them."""

        class NoPyFiles(FileFilter):
            def should_include_file(self, p: Path) -> bool:
                return p.suffix != '.py'

            def should_include_directory(self, d: Path) -> bool:
                return True

        fs = _make_filesystem(_TREE)
        walker = DirectoryWalker(fs)

        files = walker.collect_matching_files(ROOT, NoPyFiles())
        names = {p.name for p in files}

        assert names == {'README.md', '.hidden'}
        assert 'main.py' not in names

    def test_filter_can_prune_directories(self):
        """Filter that excludes a directory skips everything inside it."""

        class NoTests(FileFilter):
            def should_include_file(self, p: Path) -> bool:
                return True

            def should_include_directory(self, d: Path) -> bool:
                return d.name != 'tests'

        fs = _make_filesystem(_TREE)
        walker = DirectoryWalker(fs)

        files = walker.collect_matching_files(ROOT, NoTests())
        names = {p.name for p in files}

        assert 'test_main.py' not in names
        assert 'main.py' in names

    def test_empty_directory_returns_empty_list(self):
        fs = _make_filesystem({})
        walker = DirectoryWalker(fs)

        files = walker.collect_matching_files(ROOT, IncludeEverythingFilter())
        assert files == []
