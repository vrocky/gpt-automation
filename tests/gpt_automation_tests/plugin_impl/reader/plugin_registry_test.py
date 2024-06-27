import pytest
import json
from pathlib import Path

from gpt_automation.plugin_impl.reader.plugin_loader import PluginRegistry


# Fixture to create an instance of PluginRegistry
@pytest.fixture
def plugin_registry_instance():
    package_name = 'gpt_automation'
    return PluginRegistry(package_name)


# Test case to verify the initialization of PluginRegistry
def test_plugin_registry_initialization(plugin_registry_instance):
    assert plugin_registry_instance.package_name == 'gpt_automation'

    # Assuming 'plugin_registry.json' exists and contains valid JSON data for testing
    registry_path = plugin_registry_instance.find_registry_path()
    #assert registry_path == Path('gpt_automation/plugin_registry.json')

    # Assuming 'plugin_registry.json' is properly loaded and parsed
    assert isinstance(plugin_registry_instance.registry_data, dict)
    assert isinstance(plugin_registry_instance.plugin_map, dict)




