"""
Build file filters from project settings.

Orchestrates filter creation: decides which filters to create and how to combine them.
Delegates actual creation to FilterFactory.
"""

from pathlib import Path

from gpt_automation.domain.filters.file_filter import FileFilter, AllFilters, IncludeEverythingFilter
from gpt_automation.infrastructure.config.settings_model import ProjectSettings, BuiltinPlugin
from gpt_automation.infrastructure.plugins.filter_factory import FilterFactory


class FilterBuilder:
    """
    Orchestrate filter creation and combination.

    Decides which filters to create, in what order, and how to combine them.
    Delegates actual creation to FilterFactory.

    Usage:
        builder = FilterBuilder(settings, plugin_dir)
        filter_ = builder.build_for_traversal(root_dir, work_dir, profiles)
    """

    def __init__(self, settings: ProjectSettings, plugin_dir: Path):
        """
        settings   – loaded project settings (controls which plugins run)
        plugin_dir – .gpt/config/ directory where plugin data files live
        """
        self._settings = settings
        self._factory = FilterFactory(settings, plugin_dir)

    def build_for_traversal(
        self,
        root_dir: Path,
        work_dir: Path,
        profiles: list[str],
    ) -> FileFilter:
        """
        Return a filter ready for directory traversal.

        Combines all active plugin filters with AND logic:
        a file must pass every enabled filter to be included.
        """
        active_filters = self._create_filters(root_dir, work_dir, profiles)

        if not active_filters:
            return IncludeEverythingFilter()

        if len(active_filters) == 1:
            return active_filters[0]

        return AllFilters(active_filters)

    def setup_plugin_files(self, root_dir: Path, profiles: list[str]) -> None:
        """
        Create any files that plugins need on disk (e.g. blocklist/allowlist).

        Called during `init` so that users can edit the files after setup.
        """
        if self._settings.is_plugin_active(BuiltinPlugin.BLOCKLIST_ALLOWLIST):
            self._factory.setup_blocklist_allowlist_files(root_dir, profiles)

    # ──────────────────────────── private helpers ────────────────────────────

    def _create_filters(
        self,
        root_dir: Path,
        work_dir: Path,
        profiles: list[str],
    ) -> list[FileFilter]:
        """Create one FileFilter per active plugin, in order (via factory)."""
        filters: list[FileFilter] = []

        if self._settings.is_plugin_active(BuiltinPlugin.IGNORE_PATTERNS):
            f = self._factory.create_ignore_filter(root_dir, work_dir, profiles)
            if f:
                filters.append(f)

        if self._settings.is_plugin_active(BuiltinPlugin.INCLUDE_PATTERNS):
            f = self._factory.create_include_only_filter(root_dir, work_dir, profiles)
            if f:
                filters.append(f)

        if self._settings.is_plugin_active(BuiltinPlugin.BLOCKLIST_ALLOWLIST):
            f = self._factory.create_blocklist_allowlist_filter(root_dir, profiles)
            if f:
                filters.append(f)

        return filters
