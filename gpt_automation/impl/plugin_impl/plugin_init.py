from gpt_automation.impl.base_plugin import BasePlugin
from gpt_automation.impl.plugin_impl.plugin_arg_filter import PluginArgFilter
from gpt_automation.impl.plugin_impl.utils.file_pattern_filter import FilePatternFilter
from gpt_automation.impl.setting.paths import PathManager
from gpt_automation.impl.plugin_impl.plugin_settings import PluginSettings
from gpt_automation.impl.plugin_impl.plugin_registry import PluginLoader
from gpt_automation.impl.plugin_impl.plugin_context import PluginContext, PluginContextBuilder


class PluginInstanceManager:
    """Manages initialization and lifecycle of plugin instances."""

    def __init__(self):
        self.plugin_instances = {}

    def create_and_store_plugin_instance(self, plugin_class, context, config, file_args):
        """Create an instance of a plugin and store it in the dictionary."""
        context_dict = context.to_dict()
        plugin_instance = plugin_class(context_dict, config, file_args)
        self.plugin_instances[context.plugin_key] = plugin_instance
        return plugin_instance

    def get_all_plugin_visitors(self):
        """Return visitors from all plugins if they have a 'get_visitors' method."""
        visitors = []
        for plugin_instance in self.plugin_instances.values():
            if hasattr(plugin_instance, 'get_visitors'):
                visitors.extend(plugin_instance.get_visitors())
        return visitors

    def verify_all_plugins_are_configured(self):
        """Check if all plugins are configured properly, log if not."""
        for key, plugin_instance in self.plugin_instances.items():
            if hasattr(plugin_instance, 'is_plugin_configured') and not plugin_instance.is_plugin_configured():
                print(f"Plugin {key} is not properly configured.")
                return False
        return True


class PluginInitializationContext:
    """Handles initialization context for plugins, including directories."""

    def __init__(self, profile_names, root_dir):
        self.profile_names = profile_names
        self.root_dir = root_dir
        self.prompt_dir = root_dir  # Default to the root directory unless updated.

    def update_prompt_directory(self, new_prompt_dir):
        """Update the directory where prompts are stored."""
        self.prompt_dir = new_prompt_dir


class PluginArguments:
    """Handles merging of base and specific plugin arguments."""

    def __init__(self, base_args, plugin_specific_args):
        self.base_args = base_args
        self.plugin_specific_args = plugin_specific_args

    def merge_arguments(self):
        """Merge base and plugin-specific arguments to form a complete set."""
        return {**self.base_args, **self.plugin_specific_args}


class FileArguments:
    """Handles file argument filtering based on provided patterns."""

    def __init__(self, file_args):
        self.file_args = file_args

    def get_filtered_files(self, pattern):
        """Filter files based on the specified pattern."""
        return FilePatternFilter(pattern).filter_files(self.file_args)


class PluginConfigurationManager:
    """Manages the configuration and initialization of plugins based on settings."""

    def __init__(self, profile_names, root_dir, path_manager, settings):
        self.init_context = PluginInitializationContext(profile_names, root_dir)
        self.path_manager = path_manager
        self.plugin_settings = PluginSettings(settings, self.path_manager)
        self.plugin_instance_manager = PluginInstanceManager()

    def setup_and_configure_all_plugins(self, plugin_args, config_file_args):
        """Initialize and configure all plugins based on the provided arguments."""
        file_arguments = FileArguments(config_file_args)
        for plugin_info in self.plugin_settings.get_all_plugins():
            self.setup_individual_plugin(plugin_args, plugin_info, file_arguments)

    def setup_individual_plugin(self, args, plugin_info, file_arguments):
        """Setup and possibly initialize an individual plugin if it exists."""
        plugin_loader = PluginLoader(plugin_info.package_name)
        if plugin_loader.registry.plugin_exists(plugin_info.plugin_name):
            self.initialize_plugin_if_enabled(plugin_loader, plugin_info, args, file_arguments)

    def initialize_plugin_if_enabled(self, plugin_loader, plugin_info, args, file_arguments):
        """Initialize a plugin if it is enabled in the configuration."""
        filtered_args = PluginArgFilter.get_plugin_args(args, plugin_info.package_name, plugin_info.plugin_name)
        plugin_arguments = PluginArguments(plugin_info.settings_args, filtered_args).merge_arguments()
        if plugin_arguments.get('enable', False):
            context = self.create_context_for_plugin(plugin_info)
            matched_files = file_arguments.get_filtered_files(
                plugin_loader.get_manifest(plugin_info.plugin_name).get('configFilePatterns', []))
            plugin_instance = self.plugin_instance_manager.create_and_store_plugin_instance(
                plugin_loader.get_plugin_class(plugin_info.plugin_name), context, plugin_arguments, matched_files)
            self.finalize_plugin_initialization(plugin_instance, context)

    def finalize_plugin_initialization(self, plugin_instance, context):
        """Finalize the initialization of a plugin, setting up its configuration."""
        if hasattr(plugin_instance, 'configure'):
            plugin_instance.configure(context.to_dict())
            print(f"Initialized plugin {context.plugin_name} with key {context.plugin_key}.")
        else:
            print(f"Plugin {context.plugin_name} does not have a 'configure' method.")

    def create_context_for_plugin(self, plugin_info):
        """Create a context for plugin initialization based on plugin information."""
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

