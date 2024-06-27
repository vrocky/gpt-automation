import pytest
from gpt_automation.config.config import Config
from gpt_automation.plugin_impl.manager.plugin_class_registry import PluginClassRegistry, PluginInfo

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

# Configuration instance
config_instance = Config(data)


@pytest.fixture
def registry():
    # Setup the registry
    registry = PluginClassRegistry()
    # Access the plugins using the data dictionary from Config instance
    registry.load_plugin_info(
        config_instance.data['plugins'])  # Assume this correctly loads plugins from the Config instance
    registry.load_plugin_classes()  # This should load the actual plugin classes
    return registry


def test_registry_initialization():
    registry = PluginClassRegistry()
    assert isinstance(registry, PluginClassRegistry)
    assert registry.plugin_info_registry == {}
    assert registry.plugin_classes == {}


def test_load_plugin_info(registry):
    # Testing the loading of plugin information
    assert len(registry.plugin_info_registry) == len(data["plugins"])
    for plugin in data["plugins"]:
        plugin_key = f"{plugin['package_name']}.{plugin['plugin_name']}"
        assert plugin_key in registry.plugin_info_registry
        assert registry.plugin_info_registry[plugin_key].enable == plugin["enable"]


def test_load_plugin_classes(registry):
    # Testing the loading of plugin classes
    for plugin in data["plugins"]:
        plugin_key = f"{plugin['package_name']}.{plugin['plugin_name']}"
        assert plugin_key in registry.plugin_classes


def test_get_class(registry):
    # Testing retrieval of plugin classes
    for plugin in data["plugins"]:
        plugin_info = PluginInfo(
            package_name=plugin["package_name"],
            plugin_name=plugin["plugin_name"],
            enable=plugin["enable"],
            settings=plugin["settings"]
        )
        plugin_class = registry.get_class(plugin_info)
        assert plugin_class is not None
        assert isinstance(plugin_class, type)
