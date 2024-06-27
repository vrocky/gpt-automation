import os

from gpt_automation.config.config_manager import ConfigManager
from gpt_automation.directory_walker import DirectoryWalker
from gpt_automation.plugin_impl.plugin_manager import PluginManager


class ProjectInfo:
    def __init__(self, root_dir, config_manager: ConfigManager, profile_names=None):
        self.root_dir = root_dir.strip(os.sep)
        self.config_manager = config_manager
        self.plugin_manager = None
        self.directory_walker = None
        self.profile_names = profile_names

    def initialize(self):
        """
        Initialize the ProjectInfo with the necessary configurations and plugins.
        Returns True if initialization is successful, False otherwise.
        """
        try:
            # config = self.config_manager.resolve_configs(self.profile_names)
            # if config is None:
            #     print("Configuration resolution failed; necessary profiles might be missing.")
            #     return False

            # self.plugin_impl = PluginManager({"profile_names": self.profile_names}, config)
            self.plugin_manager = PluginManager(self.config_manager)
            if not self.plugin_manager.load_plugins(self.profile_names):
                print("Failed to load plugins")

            self.directory_walker = DirectoryWalker(path=self.root_dir, plugin_manager=self.plugin_manager)
            return True
        except Exception as e:
            print(f"Initialization failed with an error: {e}")
            return False

    def create_directory_structure_prompt(self):
        if not self.directory_walker:
            print("ProjectInfo is not initialized.")
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
        if not self.directory_walker:
            print("ProjectInfo is not initialized.")
            return ""
        prompt = ""
        for file_path in self.directory_walker.walk():
            if os.path.isfile(file_path):
                relative_path = os.path.relpath(file_path, self.root_dir)
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    prompt += f"=========={relative_path}:\n{file_content}\n\n"
        return prompt
