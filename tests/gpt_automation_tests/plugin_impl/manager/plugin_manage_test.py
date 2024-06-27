import pytest

from gpt_automation.config.config import Config
from gpt_automation.plugin_impl.manager.plugin_runtime_manager import PluginRuntimeManager

# Define the configuration data
data = {
    "extends": "none",
    "override": False,
    "plugins": [
        {
            "plugin_name": "IgnorePlugin",
            "package_name": "gpt_automation",
            "enable": True,
            "settings": {"ignore_filenames": [".gitignore", ".gptignore"]}
        },
        {
            "plugin_name": "IncludeOnlyPlugin",
            "package_name": "gpt_automation",
            "enable": True,
            "settings": {"include_only_filenames": [".gptincludeonly"]}
        }
    ]
}

@pytest.fixture
def config_instance():
    return Config(data)

@pytest.fixture
def plugin_manager(config_instance):
    profile_names = ['default_profile']
    return PluginRuntimeManager(profile_names, None )


def test_load_plugin_classes(config_instance,plugin_manager):
    # Load plugin classes
    plugin_manager.load_plugin_classes_from_config(config_instance)
    # Check if the registry is populated
    assert len(plugin_manager.plugin_class_registry.plugin_classes) > 0


def test_create_plugin_instances(config_instance,plugin_manager):
    # Load plugin classes
    plugin_manager.load_plugin_classes_from_config(config_instance)
    # Create plugin instances
    plugin_manager.create_plugin_instances()
    # Check if instances are created
    assert len(plugin_manager.plugin_instances) == 2

