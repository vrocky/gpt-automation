import os
import sys
import logging
import chardet
from typing import Optional

from gpt_automation.impl.directory_walker import DirectoryWalker
from gpt_automation.impl.visitor.basevisitor import BaseVisitor
from gpt_automation.impl.plugin_impl.plugin_init import PluginManager
from gpt_automation.impl.setting.paths import PathManager
from gpt_automation.impl.setting.settings_resolver import SettingsResolver

def setup_logging(log_file):
    logger = logging.getLogger('PromptCommand')
    logger.setLevel(logging.ERROR)
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    
    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    file_handler = logging.FileHandler(log_file)  # Remove delay=True
    file_handler.setLevel(logging.WARNING)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    return logger, file_handler

class PluginBasedVisitor(BaseVisitor):
    def __init__(self, plugin_visitors):
        self.plugin_visitors = plugin_visitors

    def before_traverse_directory(self, directory_path):
        for visitor in self.plugin_visitors:
            visitor.before_traverse_directory(directory_path)

    def enter_directory(self, directory_path):
        for visitor in self.plugin_visitors:
            visitor.enter_directory(directory_path)

    def leave_directory(self, directory_path):
        for visitor in self.plugin_visitors:
            visitor.leave_directory(directory_path)

    def visit_file(self, file_path):
        for visitor in self.plugin_visitors:
            visitor.visit_file(file_path)

    def should_visit_file(self, file_path):
        return all(visitor.should_visit_file(file_path) for visitor in self.plugin_visitors)

    def should_visit_subdirectory(self, directory_path):
        return all(visitor.should_visit_subdirectory(directory_path) for visitor in self.plugin_visitors)

class RootLookup:
    def __init__(self, initial_dir, provided_root_dir=None):
        self.initial_dir = initial_dir
        self.provided_root_dir = provided_root_dir

    def find_root_directory(self):
        """
        Recursively checks parent directories from the initial_dir to find the '.gpt' directory.
        Returns the directory containing the '.gpt' directory as the root, if found.
        """
        current_dir = self.initial_dir
        try:
            while current_dir != os.path.dirname(current_dir):  # Stop when reaching the filesystem root
                if os.path.exists(current_dir) and '.gpt' in os.listdir(current_dir):
                    return current_dir
                current_dir = os.path.dirname(current_dir)
        except (FileNotFoundError, OSError):
            pass
        return None

    def determine_directories(self, prompt_dir=None):
        """
        Determines the root and prompt directories based on provided arguments and environment.
        Raises ValueError if validation fails.
        """
        root_dir = self.provided_root_dir or self.find_root_directory()
        if not root_dir or not os.path.exists(root_dir):
            raise ValueError(f"Could not find valid root directory. Provided or discovered path: {root_dir}")

        final_prompt_dir = prompt_dir or self.initial_dir
        if not os.path.exists(final_prompt_dir):
            raise ValueError(f"Prompt directory does not exist: {final_prompt_dir}")

        # Validate prompt directory is within root
        try:
            relative_path = os.path.relpath(final_prompt_dir, root_dir)
            if relative_path.startswith('..'):
                raise ValueError(f"Prompt directory must be within root directory: {final_prompt_dir}")
        except ValueError as e:
            raise ValueError(f"Invalid prompt directory: {str(e)}")

        return root_dir, final_prompt_dir

class PromptCommand:
    def __init__(self, root_dir: str, prompt_dir: str, profiles: list[str], 
                 dir_profiles: list[str], content_profiles: list[str],
                 generate_dir: bool = True, generate_content: bool = True):
        # Initialize using RootLookup
        root_lookup = RootLookup(root_dir or os.getcwd(), root_dir)
        # This will now raise ValueError for invalid directories
        self.root_dir, self.prompt_dir = root_lookup.determine_directories(prompt_dir)
        
        self.profiles = profiles
        self.dir_profiles = dir_profiles
        self.content_profiles = content_profiles
        self.generate_dir = generate_dir
        self.generate_content = generate_content

        # Initialize components with resolved root_dir
        self.path_manager = PathManager(self.root_dir)
        self.setting_resolver = SettingsResolver(self.path_manager.get_base_settings_path())
        self.settings = self.setting_resolver.resolve_settings()
        self.plugin_manager = PluginManager(path_manager=self.path_manager, settings=self.settings)
        self.plugin_manager.setup_and_activate_plugins()
        
        log_file = os.path.join(self.path_manager.logs_dir, 'prompt_command.log')
        self.logger, self.file_handler = setup_logging(log_file)
        self.skipped_files_count = 0
        self.log_file_path = log_file

    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'file_handler') and self.file_handler:
            self.file_handler.close()
            if self.logger:
                self.logger.removeHandler(self.file_handler)

    def _check_settings_initialized(self) -> bool:
        """Check if settings are properly initialized."""
        base_settings_path = self.path_manager.get_base_settings_path()
        if not os.path.exists(base_settings_path):
            print("Error: Settings not initialized. Please run 'autogpt init' command first.")
            return False
        return True

    def execute(self):
        # Add check for valid initialization
        if not hasattr(self, 'path_manager'):
            return False

        if not self._check_settings_initialized():
            return False

        if self.generate_dir:
            dir_prompt = self._generate_directory_prompt()
        else:
            dir_prompt = ""

        if self.generate_content:
            content_prompt = self._generate_content_prompt()
        else:
            content_prompt = ""

        if dir_prompt or content_prompt:
            self._display_prompts(dir_prompt, content_prompt)

        return True

    def _get_initialized_visitors(self) -> list:
        """Get visitors from properly initialized plugins"""
        all_visitors = []
        plugin_infos = self.plugin_manager.get_all_plugins()
        
        self.logger.info(f"Initializing {len(plugin_infos)} plugins for visitor collection")
        
        for plugin_id, plugin_info in plugin_infos.items():
            try:
                # Get plugin settings path and initialize plugin
                plugin_settings_path = self.path_manager.get_plugin_settings_path(
                    plugin_info.context.package_name,
                    plugin_info.context.plugin_name
                )
                
                self.logger.info(f"Initializing plugin: {plugin_id}")
                plugin_info.instance.init(plugin_settings_path, self.root_dir, self.profiles)
                
                # Get visitors after initialization
                visitors = plugin_info.instance.get_visitors(self.prompt_dir)
                if visitors:
                    all_visitors.extend(visitors)
                    self.logger.info(f"Added {len(visitors)} visitors from plugin {plugin_id}")
                else:
                    self.logger.debug(f"No visitors returned from plugin {plugin_id}")
                    
            except Exception as e:
                self.logger.error(f"Error initializing plugin {plugin_id}: {str(e)}", exc_info=True)
                
        return all_visitors

    def _generate_directory_prompt(self) -> str:
        try:
            all_visitors = self._get_initialized_visitors()
            
            if not all_visitors:
                self.logger.warning("No plugin visitors available")
                return ""

            directory_walker = DirectoryWalker(
                self.prompt_dir,
                visitor=PluginBasedVisitor(all_visitors)
            )

            tree = {}
            for file_path in sorted(directory_walker.walk()):
                if file_path.startswith(self.root_dir):
                    relative_path = file_path[len(self.root_dir) + 1:]
                    parts = relative_path.split(os.sep)
                    current_level = tree
                    for part in parts[:-1]:
                        current_level = current_level.setdefault(part, {})
                    current_level[parts[-1]] = {}

            prompt = "\n./\n" + self._format_tree_output(tree, 0)
            print("\nDirectory Structure Preview:")
            print(prompt)
            return prompt
        except Exception as e:
            self.logger.error(f"Error generating directory prompt: {str(e)}")
            return ""

    def _generate_content_prompt(self) -> str:
        try:
            all_visitors = self._get_initialized_visitors()
            
            if not all_visitors:
                self.logger.warning("No plugin visitors available")
                return ""

            directory_walker = DirectoryWalker(
                self.prompt_dir,
                visitor=PluginBasedVisitor(all_visitors)
            )

            prompt = ""
            for file_path in directory_walker.walk():
                if os.path.isfile(file_path):
                    relative_path = os.path.relpath(file_path, self.root_dir)
                    content = self._read_file_content(file_path)
                    if content is not None:
                        prompt += f"=========={relative_path}:\n{content}\n\n"

            if self.skipped_files_count > 0:
                print(f"{self.skipped_files_count} file(s) have been skipped. Check the logs at: {self.log_file_path}")
            return prompt
        except Exception as e:
            self.logger.error(f"Error generating content prompt: {str(e)}")
            return ""

    def _read_file_content(self, file_path: str) -> Optional[str]:
        try:
            encoding = chardet.detect(open(file_path, 'rb').read(1024))['encoding']
            if encoding is None:
                self.logger.warning(f"Could not detect encoding for {file_path}. Skipping file.")
                self.skipped_files_count += 1
                return None

            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                self.logger.error(f"Failed to read file {file_path}: {str(e)}")
                self.skipped_files_count += 1
                return None

    def _format_tree_output(self, node, indent_level: int) -> str:
        lines = []
        for name, subdict in sorted(node.items()):
            indent = '    ' * indent_level
            if subdict:
                lines.append(f"{indent}{name}/")
                lines.append(self._format_tree_output(subdict, indent_level + 1))
            else:
                lines.append(f"{indent}{name}")
        return "\n".join(lines)

    def _display_prompts(self, dir_prompt: str, content_prompt: str) -> None:
        combined_prompt = self._combine_prompts(dir_prompt, content_prompt)
        if combined_prompt:
            self._copy_to_clipboard(combined_prompt)

    def _combine_prompts(self, dir_prompt: str, content_prompt: str) -> str:
        combined_prompt = ""
        if dir_prompt:
            combined_prompt += "Directory Structure:\n" + dir_prompt + "\n"
        if content_prompt:
            combined_prompt += "File Contents:\n" + content_prompt.strip()
        return combined_prompt

    def _copy_to_clipboard(self, prompt: str) -> None:
        try:
            import pyperclip
            pyperclip.copy(prompt)
            print("\nPrompt has been copied to the clipboard.")
        except ImportError:
            print("\nFailed to copy prompt to clipboard. Pyperclip module not installed.")
