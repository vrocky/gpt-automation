"""
Factory for creating FileFilter instances from plugin configurations.

Responsibility: Takes settings and creates concrete filter objects.
Keeps FilterBuilder focused on orchestration.
"""

from pathlib import Path

from gpt_automation.infrastructure.config.settings_model import ProjectSettings, BuiltinPlugin


class FilterFactory:
    """
    Create FileFilter instances for each active plugin.

    Separates filter creation logic from filter orchestration.
    FilterBuilder handles policy (which filters, how to combine them).
    FilterFactory handles creation (how to instantiate each filter).
    """

    def __init__(self, settings: ProjectSettings, plugin_dir: Path):
        """
        settings   – loaded project settings (which plugins are active)
        plugin_dir – .gpt/config/ directory where plugin data files live
        """
        self._settings = settings
        self._plugin_dir = plugin_dir

    def create_ignore_filter(
        self,
        root_dir: Path,
        work_dir: Path,
        profiles: list[str],
    ):
        """Create a filter for .gitignore-style ignore patterns."""
        from gpt_automation.infrastructure.plugins.visitor_adapter import IgnoreVisitorFilter

        cfg = self._settings.plugin_settings(BuiltinPlugin.IGNORE_PATTERNS)
        filenames = cfg.option('ignore_filenames') or ['.gitignore', '.gptignore']

        return IgnoreVisitorFilter(
            root_dir=root_dir,
            work_dir=work_dir,
            ignore_filenames=filenames,
            profiles=profiles,
        )

    def create_include_only_filter(
        self,
        root_dir: Path,
        work_dir: Path,
        profiles: list[str],
    ):
        """Create a filter for .gptincludeonly whitelist patterns."""
        from gpt_automation.infrastructure.plugins.visitor_adapter import IncludeOnlyVisitorFilter

        cfg = self._settings.plugin_settings(BuiltinPlugin.INCLUDE_PATTERNS)
        filenames = cfg.option('include_only_filenames') or ['.gptincludeonly']

        return IncludeOnlyVisitorFilter(
            root_dir=root_dir,
            work_dir=work_dir,
            include_filenames=filenames,
            profiles=profiles,
        )

    def create_blocklist_allowlist_filter(
        self,
        root_dir: Path,
        profiles: list[str],
    ):
        """Create a filter for blacklist/allowlist patterns."""
        from gpt_automation.infrastructure.plugins.visitor_adapter import BlocklistAllowlistFilter

        plugin_data_dir = self._plugin_dir / 'gpt_automation' / 'bw_filter'

        return BlocklistAllowlistFilter(
            root_dir=root_dir,
            plugin_dir=plugin_data_dir,
            profiles=profiles,
        )

    def setup_blocklist_allowlist_files(
        self,
        root_dir: Path,
        profiles: list[str],
    ) -> None:
        """Initialize blocklist/allowlist files for first run."""
        from gpt_automation.plugins.filter_plugin.plugin import BlacklistWhitelistPlugin

        plugin = BlacklistWhitelistPlugin()
        plugin_data_dir = str(self._plugin_dir / 'gpt_automation' / 'bw_filter')
        plugin.init(plugin_data_dir, str(root_dir), profiles)
