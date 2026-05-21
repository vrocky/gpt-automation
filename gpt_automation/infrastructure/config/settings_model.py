"""
Settings data structures — immutable configuration objects.

Pure data, no I/O, no business logic. These are loaded once and
passed around. Treat them as read-only after creation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any


class BuiltinPlugin(Enum):
    """
    The three built-in file filtering plugins.

    Each controls a different aspect of which files get included.
    """

    IGNORE_PATTERNS = 'ignore'           # Reads .gitignore / .gptignore files
    INCLUDE_PATTERNS = 'include'         # Reads .gptincludeonly files
    BLOCKLIST_ALLOWLIST = 'bw_filter'    # Reads black_list.txt / white_list.txt


@dataclass
class PluginSettings:
    """
    Settings for one plugin: is it on, and what options does it have?
    """

    plugin: BuiltinPlugin
    enabled: bool = True
    options: dict[str, Any] = field(default_factory=dict)

    def option(self, key: str, default: Any = None) -> Any:
        """Read one option value, with a fallback default."""
        return self.options.get(key, default)


@dataclass
class ProjectSettings:
    """
    Full project settings.

    Holds the configuration for all plugins.
    Loaded from base_settings.json; use ProjectSettings.defaults() for a
    fresh project that hasn't been configured yet.
    """

    plugins: list[PluginSettings] = field(default_factory=list)

    @classmethod
    def defaults(cls) -> 'ProjectSettings':
        """All plugins enabled with sensible defaults."""
        return cls(
            plugins=[
                PluginSettings(BuiltinPlugin.IGNORE_PATTERNS, enabled=True),
                PluginSettings(BuiltinPlugin.INCLUDE_PATTERNS, enabled=True),
                PluginSettings(BuiltinPlugin.BLOCKLIST_ALLOWLIST, enabled=True),
            ]
        )

    def plugin_settings(self, plugin: BuiltinPlugin) -> Optional[PluginSettings]:
        """Find configuration for a specific plugin. Returns None if not configured."""
        return next((p for p in self.plugins if p.plugin == plugin), None)

    def active_plugins(self) -> list[PluginSettings]:
        """Return only the plugins that are enabled."""
        return [p for p in self.plugins if p.enabled]

    def is_plugin_active(self, plugin: BuiltinPlugin) -> bool:
        """True if the given plugin is configured and enabled."""
        cfg = self.plugin_settings(plugin)
        return cfg is not None and cfg.enabled
