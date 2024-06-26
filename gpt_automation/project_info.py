import os
from gpt_automation.directory_walker import DirectoryWalker
from gpt_automation.plugin_manager import PluginManager
from gpt_automation.plugins.Ignore_plugin import IgnorePlugin
from gpt_automation.plugins.include_only_plugin import IncludeOnlyPlugin
from gpt_automation.visitor.ignore_visitor import IgnoreVisitor
from gpt_automation.visitor.includeonly_visitor import IncludeOnlyVisitor


class ProjectInfo:
    def __init__(self, root_dir, black_list=None, white_list=None, profile_names=None):


        self.root_dir = root_dir.strip(os.sep)
        self.plugin_manager = PluginManager()

        # Setup plugins with settings
        self.plugin_manager.register_plugin(IgnorePlugin({

            "ignore_filenames": ['.gitignore', '.gptignore'],
            "profile_names": profile_names

        }))
        self.plugin_manager.register_plugin(IncludeOnlyPlugin({
            'include_only_filenames': ['.gptincludeonly'],
            'profile_names': profile_names
        }))
        self.directory_walker = DirectoryWalker(path=root_dir, plugin_manager=self.plugin_manager)

    def create_directory_structure_prompt(self):
        """
        Create a structured directory prompt displaying all directories and files in a hierarchical format.
        """
        tree = {}
        for file_path in sorted(self.directory_walker.walk()):
            if file_path.startswith(self.root_dir):
                relative_path = file_path[len(self.root_dir) + 1:]
                parts = relative_path.split(os.sep)
                current_level = tree
                for part in parts[:-1]:  # Navigate/create to the correct location in the dictionary
                    current_level = current_level.setdefault(part, {})
                current_level[parts[-1]] = {}  # Set the last part as a key in the dict

        return "\n./\n" + self.format_output(tree, 0)

    def format_output(self, node, indent_level):
        """
        Recursively generate the string representation of the directory structure.
        """
        lines = []
        for name, subdict in sorted(node.items()):
            indent = '    ' * indent_level
            if subdict:  # This is a directory
                lines.append(f"{indent}{name}/")
                lines.append(self.format_output(subdict, indent_level + 1))
            else:  # This is a file
                lines.append(f"{indent}{name}")
        return "\n".join(lines)

    def create_file_contents_prompt(self):
        """
        Create a prompt showing the contents of each file.
        """
        prompt = ""
        for file_path in self.directory_walker.walk():
            if os.path.isfile(file_path):
                relative_path = os.path.relpath(file_path, self.root_dir)
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    prompt += f"=========={relative_path}:\n{file_content}\n\n"
        return prompt
