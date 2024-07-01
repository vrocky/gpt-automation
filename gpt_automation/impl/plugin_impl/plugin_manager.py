from gpt_automation.impl.config.paths import PathManager
from gpt_automation.impl.plugin_impl.plugin_config import PluginInfo, PluginConfig
from gpt_automation.impl.plugin_impl.plugin_loader import PluginLoader
from gpt_automation.impl.plugin_impl.plugin_context import PluginContext, PluginContextBuilder


def start_plugin_instance(plugin_class, context: PluginContext, settings):
    context_dict = context.to_dict()
    plugin_instance = plugin_class(context_dict, settings)
    return plugin_instance


class PluginManager:
    def __init__(self, profile_names, config=None, path_manager:PathManager=None):
        if not config:
            raise ValueError("Config is required to initialize PluginRuntimeManager.")
        self.profile_names = profile_names
        self.config = config
        self.plugin_config = PluginConfig(config,path_manager)
        self.plugin_info_registry = {}
        self.plugin_classes = {}
        self.plugin_instances = {}
        self.path_manager = path_manager

    def load_plugin_classes(self):
        plugins_config = self.plugin_config.get_all_plugins()
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

    def configure_all_plugins(self):
        for key, plugin_instance in self.plugin_instances.items():
            plugin_info = self.plugin_info_registry[key]
            context = self._create_context(plugin_info)
            if hasattr(plugin_instance, 'configure'):
                plugin_instance.configure(context.to_dict())
                print(f"Initialized plugin {plugin_info.plugin_name} with key {key}.")
            else:
                print(f"Plugin {plugin_info.plugin_name} does not have an 'configure' method.")

    def is_all_plugin_configured(self):
        # Check if all plugin instances are correctly configured.
        for key, plugin_instance in self.plugin_instances.items():
            if hasattr(plugin_instance, 'is_plugin_configured'):
                if not plugin_instance.is_plugin_configured():
                    print(f"Plugin {self.plugin_info_registry[key].plugin_name} is not properly configured.")
                    return False
            else:
                print(f"No configuration check method for plugin {self.plugin_info_registry[key].plugin_name}.")
                return False

        # If all plugin instances have been correctly configured.
        return True

    def get_all_visitors(self):
        # First, check if all plugins are correctly configured
        if self.is_all_plugin_configured():
            visitors = []
            for plugin_instance in self.plugin_instances.values():
                if hasattr(plugin_instance, 'get_visitors'):
                    visitors.extend(plugin_instance.get_visitors())
            return visitors
        else:
            print("Not all plugins are configured correctly. Unable to retrieve visitors.")
            return []
