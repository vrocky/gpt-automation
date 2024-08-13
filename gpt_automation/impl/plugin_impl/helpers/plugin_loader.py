from gpt_automation.impl.plugin_impl.plugin_registry import PluginLoader


class PluginLoaderHelper:
    def __init__(self, path_manager):
        self.path_manager = path_manager

    def load_plugin_class(self, plugin_info):
        """ Load the plugin class from its information. """
        loader = PluginLoader(plugin_info.package_name)
        return loader.get_plugin_class(plugin_info.plugin_name)
