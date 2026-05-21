"""
Adapter layer: wraps legacy visitor objects in the new FileFilter interface.

The original visitor objects (IgnoreVisitor, IncludeOnlyVisitor) were written
before the clean architecture. These adapters let them work as FileFilter
objects without modifying the originals.
"""

from pathlib import Path

from gpt_automation.domain.filters.file_filter import FileFilter


class IgnoreVisitorFilter(FileFilter):
    """
    Wraps IgnoreVisitor as a FileFilter.

    Delegates all filtering decisions to the visitor.
    """

    def __init__(
        self,
        root_dir: Path,
        work_dir: Path,
        ignore_filenames: list[str],
        profiles: list[str],
    ):
        from gpt_automation.plugins.ignore_plugin.ignore_visitor import IgnoreVisitor

        self._visitor = IgnoreVisitor(
            root_dir=str(root_dir),
            prompt_dir=str(work_dir),
            ignore_filenames=ignore_filenames,
            profile_names=profiles or None,
        )

    def should_include_file(self, file_path: Path) -> bool:
        return self._visitor.should_visit_file(str(file_path))

    def should_include_directory(self, dir_path: Path) -> bool:
        return self._visitor.should_visit_subdirectory(str(dir_path))


class IncludeOnlyVisitorFilter(FileFilter):
    """
    Wraps IncludeOnlyVisitor as a FileFilter.
    """

    def __init__(
        self,
        root_dir: Path,
        work_dir: Path,
        include_filenames: list[str],
        profiles: list[str],
    ):
        from gpt_automation.plugins.include_only_plugin.includeonly_visitor import IncludeOnlyVisitor

        self._visitor = IncludeOnlyVisitor(
            root_dir=str(root_dir),
            prompt_dir=str(work_dir),
            include_only_filenames=include_filenames,
            profile_names=profiles or None,
        )

    def should_include_file(self, file_path: Path) -> bool:
        return self._visitor.should_visit_file(str(file_path))

    def should_include_directory(self, dir_path: Path) -> bool:
        return self._visitor.should_visit_subdirectory(str(dir_path))


class BlocklistAllowlistFilter(FileFilter):
    """
    Wraps BlacklistWhitelistPlugin's visitors as a single FileFilter.

    The plugin may return multiple visitors (one per profile); this adapter
    combines them all with AND logic.
    """

    def __init__(
        self,
        root_dir: Path,
        plugin_dir: Path,
        profiles: list[str],
    ):
        from gpt_automation.plugins.filter_plugin.plugin import BlacklistWhitelistPlugin

        plugin = BlacklistWhitelistPlugin()
        plugin.init(str(plugin_dir), str(root_dir), profiles)
        self._visitors = plugin.get_visitors(str(root_dir))

    def should_include_file(self, file_path: Path) -> bool:
        return all(v.should_visit_file(str(file_path)) for v in self._visitors)

    def should_include_directory(self, dir_path: Path) -> bool:
        return all(v.should_visit_subdirectory(str(dir_path)) for v in self._visitors)
