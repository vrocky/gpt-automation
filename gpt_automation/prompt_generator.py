import os
import traceback

from gpt_automation.impl.directory_walker import DirectoryWalker
from gpt_automation.impl.plugin_impl.plugin_init import PluginManager
from gpt_automation.impl.setting.paths import PathManager
from gpt_automation.impl.setting.settings_manager import SettingsManager
from gpt_automation.setup_settings import SettingContext, PluginArguments


class PromptGenerator:
    def __init__(self, prompt_dir ,context: SettingContext, plugin_args: PluginArguments):
        self.root_dir = context.root_dir.strip(os.sep)
        self.profile_names = context.profile_names
        path_manager = PathManager(self.root_dir)
        self.settings_manager = SettingsManager(path_manager)
        self.plugin_manager = PluginManager(context.profile_names, context.root_dir,
                                            settings=self.settings_manager.get_settings(context.profile_names))
        self.plugin_manager.setup_and_activate_plugins(plugin_args.args, plugin_args.config_file_args)
        self.directory_walker = DirectoryWalker(prompt_dir, self.plugin_manager.get_all_plugin_visitors(prompt_dir))

    def initialize(self):
        try:
            # Check if base and profile configurations are initialized
            if not self.settings_manager.is_base_config_initialized() or not self.settings_manager.check_profiles_created(self.profile_names):
                print("Please run init command.")
                return False

            # Ensure all plugins are properly configured
            if not self.plugin_manager.is_all_plugin_configured():
                print("Some plugins are not properly configured.")
                return False

            return True
        except Exception as e:
            print(f"Initialization failed with an error: {e}")
            traceback_str = traceback.format_exc()
            print(traceback_str)
            return False

    def create_directory_structure_prompt(self):
        if not self.plugin_manager.is_all_plugin_configured():
            print("Not all plugins are properly configured. Unable to create directory structure prompt.")
            return ""

        tree = {}
        for file_path in sorted(self.directory_walker.walk()):
            if file_path.startswith(self.root_dir):
                relative_path = file_path[len(self.root_dir) + 1:]
                parts = relative_path.split(os.sep)
                current_level = tree
                for part in parts[:-1]:
                    current_level = current_level.setdefault(part, {})
                current_level[parts[-1]] = {}
        return "\n./\n" + self.format_output(tree, 0)

    def format_output(self, node, indent_level):
        lines = []
        for name, subdict in sorted(node.items()):
            indent = '    ' * indent_level
            if subdict:
                lines.append(f"{indent}{name}/")
                lines.append(self.format_output(subdict, indent_level + 1))
            else:
                lines.append(f"{indent}{name}")
        return "\n".join(lines)

    def create_file_contents_prompt(self):
        if not self.plugin_manager.is_all_plugin_configured():
            print("Not all plugins are properly configured. Unable to create file contents prompt.")
            return ""

        prompt = ""
        for file_path in self.directory_walker.walk():
            if os.path.isfile(file_path):
                relative_path = os.path.relpath(file_path, self.root_dir)
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    prompt += f"=========={relative_path}:\n{file_content}\n\n"
        return prompt
