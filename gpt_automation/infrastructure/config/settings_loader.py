"""
Load and save project settings from/to JSON.

All I/O for settings lives here. Domain only ever sees ProjectSettings objects.
"""

import json
from pathlib import Path

from gpt_automation.infrastructure.config.settings_model import (
    ProjectSettings,
    PluginSettings,
    BuiltinPlugin,
)

# Maps the JSON "plugin_name" field to our BuiltinPlugin enum.
# Supports both old-style names (from existing base_settings.json) and new enum values.
_JSON_NAME_TO_PLUGIN: dict[str, BuiltinPlugin] = {
    'gpt_ignore':      BuiltinPlugin.IGNORE_PATTERNS,
    'gpt_include_only': BuiltinPlugin.INCLUDE_PATTERNS,
    'bw_filter':       BuiltinPlugin.BLOCKLIST_ALLOWLIST,
    'ignore':          BuiltinPlugin.IGNORE_PATTERNS,
    'include':         BuiltinPlugin.INCLUDE_PATTERNS,
}

_PLUGIN_TO_JSON_NAME: dict[BuiltinPlugin, str] = {
    BuiltinPlugin.IGNORE_PATTERNS:    'gpt_ignore',
    BuiltinPlugin.INCLUDE_PATTERNS:   'gpt_include_only',
    BuiltinPlugin.BLOCKLIST_ALLOWLIST: 'bw_filter',
}


class SettingsReader:
    """Read ProjectSettings from a JSON file."""

    def __init__(self, settings_file: Path):
        self._file = Path(settings_file)

    def read(self) -> ProjectSettings:
        """
        Load settings from file.

        Returns defaults when file doesn't exist (e.g. before first `init`).
        Raises SettingsParseError for malformed files.
        """
        if not self._file.exists():
            return ProjectSettings.defaults()

        try:
            return self._parse(self._file.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, ValueError) as e:
            raise SettingsParseError(f"Cannot read settings from {self._file}: {e}")

    def _parse(self, json_text: str) -> ProjectSettings:
        """Parse JSON text into ProjectSettings."""
        data = json.loads(json_text)

        plugins = []
        for raw in data.get('plugins', []):
            plugin_name = raw.get('plugin_name') or raw.get('type', '')
            plugin = _JSON_NAME_TO_PLUGIN.get(plugin_name)

            if plugin is None:
                continue  # Unknown plugin — skip rather than fail

            # Args live under either "args" or "settings" key for backward compat
            args = raw.get('args', raw.get('settings', {}))
            enabled = args.get('enable', raw.get('enabled', True))

            plugins.append(PluginSettings(
                plugin=plugin,
                enabled=bool(enabled),
                options=args,
            ))

        return ProjectSettings(plugins=plugins)


class SettingsWriter:
    """Write ProjectSettings to a JSON file."""

    def __init__(self, settings_file: Path):
        self._file = Path(settings_file)

    def write(self, settings: ProjectSettings) -> None:
        """Save settings, creating parent directories as needed."""
        self._file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'plugins': [
                {
                    'plugin_name': _PLUGIN_TO_JSON_NAME[p.plugin],
                    'package_name': 'gpt_automation',
                    'args': {'enable': p.enabled, **p.options},
                }
                for p in settings.plugins
            ]
        }

        self._file.write_text(json.dumps(data, indent=2), encoding='utf-8')


class SettingsParseError(Exception):
    """Raised when a settings file cannot be parsed."""
    pass
