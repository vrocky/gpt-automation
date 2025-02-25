import logging
import os
import traceback

from gpt_automation.impl.directory_walker import DirectoryWalker
from gpt_automation.impl.plugin_impl.plugin_init import PluginManager
from gpt_automation.impl.setting.paths import PathManager
from gpt_automation.impl.setting.settings_resolver import SettingsManager
from gpt_automation.setup_settings import SettingContext, PluginArguments
import chardet


def setup_logging(log_file):
    # Create a logger
    logger = logging.getLogger('PromptGenerator')
    logger.setLevel(logging.ERROR)

    # Create file handler for warnings and errors
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.WARNING)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Add the handler to the logger
    logger.addHandler(file_handler)

    return logger


def detect_file_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read(1024)  # Read the first 1024 bytes to detect encoding
        result = chardet.detect(raw_data)
        return result['encoding']


class PluginBasedTraverser(IDirectoryTraverser):
    def __init__(self, plugin_visitors):
        self.plugin_visitors = plugin_visitors

    def on_enter_directory(self, directory_path: str) -> None:
        for visitor in self.plugin_visitors:
            visitor.enter_directory(directory_path)

    def on_leave_directory(self, directory_path: str) -> None:
        for visitor in self.plugin_visitors:
            visitor.leave_directory(directory_path)

    def on_file_found(self, file_path: str) -> None:
        for visitor in self.plugin_visitors:
            visitor.visit_file(file_path)


class PluginBasedFilter(ITraverseFilter):
    def __init__(self, plugin_visitors):
        self.plugin_visitors = plugin_visitors

    def should_visit_file(self, file_path: str) -> bool:
        return all(visitor.should_visit_file(file_path) for visitor in self.plugin_visitors)

    def should_visit_directory(self, directory_path: str) -> bool:
        return all(visitor.should_visit_subdirectory(directory_path) for visitor in self.plugin_visitors)


class PromptGenerator:
    def __init__(self, prompt_dir, context: SettingContext, plugin_args: PluginArguments):
        self.root_dir = context.root_dir.rstrip(os.sep)
        self.profile_names = context.profile_names
        path_manager = PathManager(self.root_dir)
        self.settings_manager = SettingsManager(path_manager)
        self.plugin_manager = PluginManager(context.profile_names, context.root_dir,
                                            settings=self.settings_manager.get_settings(context.profile_names))
        self.plugin_manager.setup_and_activate_plugins(plugin_args.args, plugin_args.config_file_args)
        plugin_visitors = self.plugin_manager.get_all_plugin_visitors(prompt_dir)
        
        self.directory_walker = DirectoryWalker(
            prompt_dir,
            traverser=PluginBasedTraverser(plugin_visitors),
            traverse_filter=PluginBasedFilter(plugin_visitors)
        )

        log_file = os.path.join(path_manager.get_logs_dir(), 'prompt_generator.log')
        self.logger = setup_logging(log_file)
        self.skipped_files_count = 0
        self.log_file_path = log_file

    def initialize(self):
        try:
            # Check if base and profile configurations are initialized
            if not self.settings_manager.is_base_config_initialized() or not self.settings_manager.check_profiles_created(
                    self.profile_names):
                self.logger.warning("Base or profile configurations are not initialized. Please run init command.")
                return False

            # Ensure all plugins are properly configured
            if not self.plugin_manager.is_all_plugin_configured():
                self.logger.warning("Some plugins are not properly configured.")
                return False

            self.logger.info("Initialization successful.")
            return True
        except Exception as e:
            self.logger.error(f"Initialization failed with an error: {e}")
            traceback_str = traceback.format_exc()
            self.logger.debug(traceback_str)
            return False

    def create_directory_structure_prompt(self):
        if not self.plugin_manager.is_all_plugin_configured():
            self.logger.warning("Not all plugins are properly configured. Unable to create directory structure prompt.")
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
        self.logger.info("Directory structure prompt created.")
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
        try:
            prompt = ""
            for file_path in self.directory_walker.walk():
                if os.path.isfile(file_path):
                    relative_path = os.path.relpath(file_path, self.root_dir)
                    encoding = detect_file_encoding(file_path)

                    # If encoding detection fails, skip the file
                    if encoding is None:
                        self.logger.warning(f"Could not detect encoding for {file_path}. Skipping file.")
                        self.skipped_files_count += 1
                        continue

                    try:
                        # First attempt: use detected encoding
                        with open(file_path, 'r', encoding=encoding) as f:
                            file_content = f.read()
                            prompt += f"=========={relative_path}:\n{file_content}\n\n"
                    except (UnicodeDecodeError, IOError) as e:
                        self.logger.warning(f"Error reading {file_path} with encoding {encoding}. Retrying with UTF-8.")

                        # Second attempt: retry with UTF-8
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                file_content = f.read()
                                prompt += f"=========={relative_path}:\n{file_content}\n\n"
                        except (UnicodeDecodeError, IOError) as e:
                            self.logger.error(f"Failed to read file {file_path} with UTF-8 encoding: {e}")
                            self.skipped_files_count += 1
                            continue

            if self.skipped_files_count > 0:
                print(f"{self.skipped_files_count} file(s) have been skipped. Check the logs at: {self.log_file_path}")

            return prompt
        except Exception as e:
            self.logger.error(f"An error occurred while creating file contents prompt: {e}")
            return ""
