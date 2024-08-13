from gpt_automation.impl.base_plugin import BasePlugin
from gpt_automation.impl.plugin_impl.plugin_arg_filter import PluginArgFilter
from gpt_automation.impl.plugin_impl.utils.file_pattern_filter import FilePatternFilter
from gpt_automation.impl.setting.paths import PathManager
from gpt_automation.impl.plugin_impl.plugin_settings import PluginSettings
from gpt_automation.impl.plugin_impl.plugin_registry import PluginLoader
from gpt_automation.impl.plugin_impl.plugin_context import PluginContext, PluginContextBuilder


def start_plugin_instance(plugin_class: BasePlugin.__class__, context: PluginContext, config, file_args):
    context_dict = context.to_dict()
    plugin_instance = plugin_class(context_dict, config, file_args)
    return plugin_instance


class PluginInitializationContext:
    def __init__(self, profile_names, root_dir):
        self.profile_names = profile_names
        self.root_dir = root_dir
        self.prompt_dir = root_dir  # assuming prompt_dir follows the same path as root_dir

    def update_prompt_dir(self, new_prompt_dir):
        self.prompt_dir = new_prompt_dir


class PluginArguments:
    def __init__(self, base_args, plugin_specific_args):
        self.base_args = base_args
        self.plugin_specific_args = plugin_specific_args

    def merge(self):
        """Merge base and plugin-specific arguments."""
        return {**self.base_args, **self.plugin_specific_args}


class FileArguments:
    def __init__(self, file_args):
        self.file_args = file_args

    def filter_files(self, pattern):
        file_pattern_filter = FilePatternFilter(pattern)
        return file_pattern_filter.filter_files(self.file_args)


class PluginSettingsInitializer:
    def __init__(self, profile_names, root_dir, path_manager, settings):

        self.init_context = PluginInitializationContext(profile_names, root_dir)
        self.path_manager = path_manager
        self.plugin_settings = PluginSettings(settings, self.path_manager)
        self.plugin_instances = {}
        self.plugin_info_registry = {}

    def initialize_and_configure_plugins(self, args, file_args):
        plugins_settings = self.plugin_settings.get_all_plugins()
        file_arguments = FileArguments(file_args)

        for plugin_info in plugins_settings:
            plugin_loader = PluginLoader(plugin_info.package_name)
            if plugin_loader.registry.plugin_exists(plugin_info.plugin_name):
                filtered_args = PluginArgFilter.get_plugin_args(args, plugin_info.package_name, plugin_info.plugin_name)
                plugin_arguments = PluginArguments(plugin_info.settings_args, filtered_args)
                self.configure_single_plugin(plugin_info, plugin_loader, plugin_arguments, file_arguments)

    def configure_single_plugin(self, plugin_info, plugin_loader, plugin_arguments, file_arguments):
        if plugin_arguments.merge().get('enable', False):
            self.initialize_plugin(plugin_info, plugin_loader, plugin_arguments, file_arguments)

    def initialize_plugin(self, plugin_info, plugin_loader, plugin_arguments, file_arguments):
        context = self.create_plugin_context(plugin_info)
        matched_files = file_arguments.filter_files(
            plugin_loader.get_manifest(plugin_info.plugin_name).get('configFilePatterns', []))

        plugin_class = plugin_loader.get_plugin_class(plugin_info.plugin_name)
        plugin_instance = start_plugin_instance(plugin_class, context, plugin_arguments.merge(), matched_files)
        self.plugin_instances[plugin_info.key()] = plugin_instance

        if hasattr(plugin_instance, 'configure'):
            plugin_instance.configure(context.to_dict())
            print(f"Initialized plugin {plugin_info.plugin_name} with key {plugin_info.key()}.")
        else:
            print(f"Plugin {plugin_info.plugin_name} does not have a 'configure' method.")

    def create_plugin_context(self, plugin_info):
        """Create a context for plugin initialization."""
        path = self.plugin_settings.get_plugin_settings_path(plugin_info.package_name, plugin_info.plugin_name)
        return PluginContextBuilder() \
            .set_plugin_key(plugin_info.key()) \
            .set_package_name(plugin_info.package_name) \
            .set_plugin_name(plugin_info.plugin_name) \
            .set_profile_names(self.init_context.profile_names) \
            .set_root_dir(self.init_context.root_dir) \
            .set_prompt_dir(self.init_context.prompt_dir) \
            .set_plugin_settings_path(path) \
            .build()

    def is_all_plugin_configured(self):
        """Check all plugins are properly configured."""
        for key, plugin_instance in self.plugin_instances.items():
            if hasattr(plugin_instance, 'is_plugin_configured') and not plugin_instance.is_plugin_configured():
                print(f"Plugin {key} is not properly configured.")
                return False
        return True

    def get_all_visitors(self):
        """Retrieve all visitors from configured plugins."""
        if self.is_all_plugin_configured():
            visitors = []
            for plugin_instance in self.plugin_instances.values():
                if hasattr(plugin_instance, 'get_visitors'):
                    visitors.extend(plugin_instance.get_visitors())
            return visitors
        else:
            print("Not all plugins are configured correctly. Unable to retrieve visitors.")
            return []
