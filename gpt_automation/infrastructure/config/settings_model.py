"""
Settings data structures (immutable configuration objects).

These are pure data—no I/O, no logic, just structure.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any


class PluginType(Enum):
    """Available plugin types in the system."""

    IGNORE = 'ignore'
    INCLUDE = 'include'
    BLACKLIST_WHITELIST = 'bw_filter'


@dataclass
class PluginConfig:
    """Configuration for a single plugin."""

    type: PluginType
    enabled: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)

    def is_enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self.enabled

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a plugin setting with optional default."""
        return self.settings.get(key, default)


@dataclass
class Settings:
    """
    Application settings (immutable).

    Contains plugin configurations and extension settings.
    """

    extends: str = 'none'
    override: bool = False
    plugins: list[PluginConfig] = field(default_factory=list)

    @classmethod
    def defaults(cls) -> 'Settings':
        """Return default settings with all plugins enabled."""
        return cls(
            extends='none',
            override=False,
            plugins=[
                PluginConfig(PluginType.IGNORE, enabled=True),
                PluginConfig(PluginType.INCLUDE, enabled=True),
                PluginConfig(PluginType.BLACKLIST_WHITELIST, enabled=True),
            ],
        )

    def find_plugin_by_type(self, plugin_type: PluginType) -> Optional[PluginConfig]:
        """Find plugin config by type."""
        return next(
            (p for p in self.plugins if p.type == plugin_type),
            None,
        )

    def enabled_plugins(self) -> list[PluginConfig]:
        """Return only enabled plugins."""
        return [p for p in self.plugins if p.is_enabled()]
