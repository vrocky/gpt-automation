import pytest

from gpt_automation.plugin_impl.reader.plugin_loader import PluginLoader


def test_plugin_loader_success():
    """Test that PluginLoader correctly loads a plugin with valid parameters."""
    loader = PluginLoader("gpt_automation")
    plugin_class = loader.get_plugin_class("IgnorePlugin")
    assert plugin_class is not None, "Failed to load the plugin class."

def test_plugin_loader_failure():
    """Test that PluginLoader raises an error when the plugin does not exist."""
    loader = PluginLoader("gpt_automation")
    with pytest.raises(FileNotFoundError):
        loader.get_plugin_class("non_existent_plugin")

# Additional tests can be added for specific behaviors or edge cases.
