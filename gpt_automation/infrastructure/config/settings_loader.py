"""
Load and save settings from/to JSON files.

All I/O for settings happens here.
"""

import json
from pathlib import Path
from typing import Dict, Any

from gpt_automation.infrastructure.config.settings_model import (
    Settings,
    PluginConfig,
    PluginType,
)


class SettingsLoader:
    """Load settings from JSON file."""

    def __init__(self, file_path: Path):
        self._file_path = Path(file_path)

    def load(self) -> Settings:
        """
        Load settings from file.

        Returns defaults if file doesn't exist.
        Raises SettingsLoadError if file is invalid.
        """
        if not self._file_path.exists():
            return Settings.defaults()

        try:
            return self._load_from_file()
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            raise SettingsLoadError(f"Invalid settings file {self._file_path}: {e}")

    def _load_from_file(self) -> Settings:
        """Load and parse JSON file."""
        content = self._file_path.read_text(encoding='utf-8')
        data = json.loads(content)

        # Parse plugins
        plugins = []
        for plugin_data in data.get('plugins', []):
            try:
                plugin_type = PluginType[plugin_data['type'].upper().replace('-', '_')]
                plugin = PluginConfig(
                    type=plugin_type,
                    enabled=plugin_data.get('enabled', True),
                    settings=plugin_data.get('settings', {}),
                )
                plugins.append(plugin)
            except KeyError as e:
                raise ValueError(f"Invalid plugin config: {e}")

        return Settings(
            extends=data.get('extends', 'none'),
            override=data.get('override', False),
            plugins=plugins,
        )


class SettingsSaver:
    """Save settings to JSON file."""

    def __init__(self, file_path: Path):
        self._file_path = Path(file_path)

    def save(self, settings: Settings) -> None:
        """Save settings to file."""
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'extends': settings.extends,
            'override': settings.override,
            'plugins': [
                {
                    'type': p.type.value,
                    'enabled': p.enabled,
                    'settings': p.settings,
                }
                for p in settings.plugins
            ],
        }

        self._file_path.write_text(json.dumps(data, indent=2), encoding='utf-8')


class SettingsLoadError(Exception):
    """Raised when settings cannot be loaded."""

    pass
