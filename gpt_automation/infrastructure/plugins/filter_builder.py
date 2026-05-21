"""
Build file filters from project settings.

Bridges settings (what the user configured) with concrete visitor objects
(the actual filtering logic). Each enabled plugin becomes a FileFilter.
"""

from pathlib import Path

from gpt_automation.domain.filters.file_filter import FileFilter, AllFilters, IncludeEverythingFilter
from gpt_automation.infrastructure.config.settings_model import ProjectSettings, BuiltinPlugin


class FilterBuilder:
    """
    Construct a FileFilter from ProjectSettings.

    Usage:
        builder = FilterBuilder(settings, project_paths)
        filter_ = builder.build_for_traversal(root_dir, work_dir, profiles)
        files = walker.collect_matching_files(work_dir, filter_)
    """

    def __init__(self, settings: ProjectSettings, plugin_dir: Path):
        """
        settings   – loaded project settings (controls which plugins run)
        plugin_dir – .gpt/config/ directory where plugin data files live
        """
        self._settings = settings
        self._plugin_dir = plugin_dir

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
            self._setup_blocklist_allowlist(root_dir, profiles)

    # ──────────────────────────── private helpers ────────────────────────────

    def _create_filters(
        self,
        root_dir: Path,
        work_dir: Path,
        profiles: list[str],
    ) -> list[FileFilter]:
        """Create one FileFilter per active plugin, in order."""
        filters: list[FileFilter] = []

        if self._settings.is_plugin_active(BuiltinPlugin.IGNORE_PATTERNS):
            f = self._create_ignore_filter(root_dir, work_dir, profiles)
            if f:
                filters.append(f)

        if self._settings.is_plugin_active(BuiltinPlugin.INCLUDE_PATTERNS):
            f = self._create_include_filter(root_dir, work_dir, profiles)
            if f:
                filters.append(f)

        if self._settings.is_plugin_active(BuiltinPlugin.BLOCKLIST_ALLOWLIST):
            f = self._create_blocklist_allowlist_filter(root_dir, profiles)
            if f:
                filters.append(f)

        return filters

    def _create_ignore_filter(
        self,
        root_dir: Path,
        work_dir: Path,
        profiles: list[str],
    ) -> FileFilter:
        """Build IgnoreVisitor-backed filter."""
        from gpt_automation.infrastructure.plugins.visitor_adapter import IgnoreVisitorFilter

        cfg = self._settings.plugin_settings(BuiltinPlugin.IGNORE_PATTERNS)
        filenames = cfg.option('ignore_filenames') or ['.gitignore', '.gptignore']

        return IgnoreVisitorFilter(
            root_dir=root_dir,
            work_dir=work_dir,
            ignore_filenames=filenames,
            profiles=profiles,
        )

    def _create_include_filter(
        self,
        root_dir: Path,
        work_dir: Path,
        profiles: list[str],
    ) -> FileFilter:
        """Build IncludeOnlyVisitor-backed filter."""
        from gpt_automation.infrastructure.plugins.visitor_adapter import IncludeOnlyVisitorFilter

        cfg = self._settings.plugin_settings(BuiltinPlugin.INCLUDE_PATTERNS)
        filenames = cfg.option('include_only_filenames') or ['.gptincludeonly']

        return IncludeOnlyVisitorFilter(
            root_dir=root_dir,
            work_dir=work_dir,
            include_filenames=filenames,
            profiles=profiles,
        )

    def _create_blocklist_allowlist_filter(
        self,
        root_dir: Path,
        profiles: list[str],
    ) -> FileFilter:
        """Build BlocklistAllowlist-backed filter."""
        from gpt_automation.infrastructure.plugins.visitor_adapter import BlocklistAllowlistFilter

        plugin_data_dir = self._plugin_dir / 'gpt_automation' / 'bw_filter'

        return BlocklistAllowlistFilter(
            root_dir=root_dir,
            plugin_dir=plugin_data_dir,
            profiles=profiles,
        )

    def _setup_blocklist_allowlist(self, root_dir: Path, profiles: list[str]) -> None:
        """Initialize blocklist/allowlist files for first run."""
        from gpt_automation.plugins.filter_plugin.plugin import BlacklistWhitelistPlugin

        plugin = BlacklistWhitelistPlugin()
        plugin_data_dir = str(self._plugin_dir / 'gpt_automation' / 'bw_filter')
        plugin.init(plugin_data_dir, str(root_dir), profiles)
