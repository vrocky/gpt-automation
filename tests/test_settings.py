"""
Test settings model and file loading.
"""

import json
import tempfile
from pathlib import Path

from gpt_automation.infrastructure.config.settings_model import ProjectSettings, BuiltinPlugin
from gpt_automation.infrastructure.config.settings_loader import SettingsReader, SettingsWriter


class TestProjectSettings:
    """Pure data model tests — no I/O."""

    def test_defaults_enable_all_plugins(self):
        s = ProjectSettings.defaults()
        assert s.is_plugin_active(BuiltinPlugin.IGNORE_PATTERNS)
        assert s.is_plugin_active(BuiltinPlugin.INCLUDE_PATTERNS)
        assert s.is_plugin_active(BuiltinPlugin.BLOCKLIST_ALLOWLIST)

    def test_active_plugins_excludes_disabled(self):
        s = ProjectSettings.defaults()
        s.plugins[0].enabled = False
        active = s.active_plugins()
        assert len(active) == 2

    def test_plugin_settings_returns_none_when_missing(self):
        s = ProjectSettings(plugins=[])
        assert s.plugin_settings(BuiltinPlugin.IGNORE_PATTERNS) is None

    def test_is_plugin_active_false_when_disabled(self):
        s = ProjectSettings.defaults()
        s.plugins[0].enabled = False
        assert not s.is_plugin_active(s.plugins[0].plugin)


class TestSettingsRoundtrip:
    """Write then read settings — values survive the round-trip."""

    def test_round_trip_defaults(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / 'settings.json'

            writer = SettingsWriter(f)
            writer.write(ProjectSettings.defaults())

            reader = SettingsReader(f)
            loaded = reader.read()

            assert loaded.is_plugin_active(BuiltinPlugin.IGNORE_PATTERNS)
            assert loaded.is_plugin_active(BuiltinPlugin.INCLUDE_PATTERNS)
            assert loaded.is_plugin_active(BuiltinPlugin.BLOCKLIST_ALLOWLIST)

    def test_reader_returns_defaults_when_file_missing(self):
        reader = SettingsReader(Path('/nonexistent/settings.json'))
        s = reader.read()
        assert isinstance(s, ProjectSettings)
        assert len(s.active_plugins()) == 3

    def test_reader_parses_existing_base_settings_json(self):
        """Verify the actual settings file in the repo loads correctly."""
        existing = Path(__file__).parent.parent / '.gpt' / 'settings' / 'base_settings.json'
        if not existing.exists():
            return  # Repo not initialised yet — skip

        reader = SettingsReader(existing)
        s = reader.read()
        assert isinstance(s, ProjectSettings)
