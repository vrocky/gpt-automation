from gpt_automation.impl.plugin_impl.config import PluginInfo, PluginConfig
from gpt_automation.impl.plugin_impl.reader.plugin_loader import PluginLoader
from gpt_automation.impl.plugin_impl.manager.runtime.plugin_context import PluginContext, PluginContextBuilder


def start_plugin_instance(plugin_class, context: PluginContext, settings):
    context_dict = context.to_dict()
    plugin_instance = plugin_class(context_dict, settings)
    return plugin_instance


class PluginRuntimeManager:
    def __init__(self, profile_names, config_manager=None):
        self.profile_names = profile_names
        self.config_manager = config_manager
        self.plugin_config = PluginConfig(config_manager)
        self.plugin_info_registry = {}
        self.plugin_classes = {}
        self.plugin_instances = {}

    def load_plugin_classes(self):
        plugins_config = self.plugin_config.get_all_plugins(self.profile_names)
        for plugin_info in plugins_config:
            self.plugin_info_registry[plugin_info.key()] = plugin_info
            print(f"Saved info for plugin {plugin_info.plugin_name}.")

            loader = PluginLoader(plugin_info.package_name)
            plugin_class = loader.get_plugin_class(plugin_info.plugin_name)
            self.plugin_classes[plugin_info.key()] = plugin_class
            print(f"Loaded class for plugin {plugin_info.plugin_name}.")

    def create_plugin_instances(self):
        for plugin_name, plugin_class in self.plugin_classes.items():
            plugin_info: PluginInfo = self.plugin_info_registry[plugin_name]
            context = self._create_context(plugin_info)
            settings = plugin_info.settings
            plugin_instance = start_plugin_instance(plugin_class, context, settings=settings)
            print(f"Created instance for plugin {plugin_info.plugin_name}.")
            self.plugin_instances[plugin_info.key()] = plugin_instance

    def _create_context(self, plugin_info):
        path = self.plugin_config.get_plugin_settings_path(plugin_info.package_name, plugin_info.plugin_name)
        context = PluginContextBuilder() \
            .set_plugin_key(plugin_info.key()) \
            .set_package_name(plugin_info.package_name) \
            .set_plugin_name(plugin_info.plugin_name) \
            .set_profile_names(self.profile_names) \
            .set_plugin_settings_path(path) \
            .build()
        return context

    def initialize_plugins(self):
        for key, plugin_instance in self.plugin_instances.items():
            plugin_info = self.plugin_info_registry[key]
            context = self._create_context(plugin_info)
            if hasattr(plugin_instance, 'initialize'):
                plugin_instance.initialize(context.to_dict())
                print(f"Initialized plugin {plugin_info.plugin_name} with key {key}.")
            else:
                print(f"Plugin {plugin_info.plugin_name} does not have an 'initialize' method.")

    def get_all_visitors(self):
        visitors = []
        for plugin_instance in self.plugin_instances.values():
            if hasattr(plugin_instance, 'get_visitors'):
                visitors.extend(plugin_instance.get_visitors())
        return visitors
