from gpt_automation.impl.plugin_impl.manager.plugin_class_registry import PluginInfo, PluginClassRegistry
from gpt_automation.impl.plugin_impl.manager.runtime.plugin_context import PluginContext, PluginContextBuilder


def start_plugin_instance(plugin_class, context: PluginContext, settings):
    context_dict = context.to_dict()
    plugin_instance = plugin_class(context_dict, settings)
    return plugin_instance


class PluginRuntimeManager:
    def __init__(self, profile_names, config_manager=None):
        self.profile_names = profile_names
        self.config_manager = config_manager
        self.plugin_class_registry = PluginClassRegistry()
        self.plugin_instances = {}

    def load_plugin_classes(self):
        if not self.config_manager:
            raise ValueError("Config manager is required to load plugin classes.")
        config = self.config_manager.resolve_configs(self.profile_names)
        self._load_plugin_classes_from_config(config)

    def load_plugin_classes_from_config(self, config):
        self._load_plugin_classes_from_config(config)

    def _load_plugin_classes_from_config(self, config):

        if config:
            plugins_config = config.data['plugins']
            self.plugin_class_registry.load_plugin_info(plugins_config)
            self.plugin_class_registry.load_plugin_classes()
            print("All plugin classes loaded successfully.")

    def create_plugin_instances(self):
        # Iterate over plugin classes using PluginInfo objects stored in the registry
        for plugin_name, plugin_class in self.plugin_class_registry.plugin_classes.items():
            plugin_info: PluginInfo = self.plugin_class_registry.plugin_info_registry[plugin_name]
            context = self._create_context(plugin_info)
            settings = plugin_info.settings
            plugin_instance = start_plugin_instance(plugin_class, context, settings=settings)
            print(f"Created instance for plugin {plugin_info.plugin_name}.")
            self.plugin_instances[plugin_info.key()] = plugin_instance

    def _create_context(self, plugin_info):
        path = ""
        if self.config_manager:
            path = self.config_manager.path_manager.get_plugin_settings_path(plugin_info.package_name,
                                                                             plugin_info.plugin_name)
        context = PluginContextBuilder() \
            .set_plugin_key(plugin_info.key()) \
            .set_package_name(plugin_info.package_name) \
            .set_plugin_name(plugin_info.plugin_name) \
            .set_profile_names(self.profile_names) \
            .set_plugin_settings_path(path) \
            .build()
        return context

    def initialize_plugins(self):
        """
        Initialize each plugin instance using its corresponding context.
        This assumes that plugin instances have been created and are stored in self.plugin_instances.
        """
        for key, plugin_instance in self.plugin_instances.items():
            plugin_info = self.plugin_class_registry.plugin_info_registry[key]
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
