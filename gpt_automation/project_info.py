import os
import traceback

from gpt_automation.impl.app_context import AppContext
from gpt_automation.impl.directory_walker import DirectoryWalker

class ProjectInfo:
    def __init__(self, app_context: AppContext):
        self.app_context = app_context
        self.root_dir = app_context.get_root_dir().strip(os.sep)
        self.directory_walker = None
        self.profile_names = app_context.app.profile_names

    def are_profiles_initialized(self):
        return self.app_context.check_profile_created()

    def initialize(self):
        try:
            if not self.are_profiles_initialized():
                print("Please run init command.")
                return False
            self.directory_walker = DirectoryWalker(
                path=self.root_dir,
                plugin_manager=self.app_context.get_plugin_manager()
            )
            return True
        except Exception as e:
            print(f"Initialization failed with an error: {e}")
            traceback_str = traceback.format_exc()
            print(traceback_str)
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
