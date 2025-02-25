import logging
import os
from typing import List
import chardet

from gpt_automation.impl.base_plugin import BasePlugin
from gpt_automation.impl.directory_walker import DirectoryWalker, IDirectoryTraverser, ITraverseFilter


class PluginBasedTraverser(IDirectoryTraverser):
    def __init__(self, plugins: List[BasePlugin]):
        self.plugins = plugins

    def on_enter_directory(self, directory_path: str) -> None:
        for plugin in self.plugins:
            for visitor in plugin.get_visitors(""):
                visitor.enter_directory(directory_path)

    def on_leave_directory(self, directory_path: str) -> None:
        for plugin in self.plugins:
            for visitor in plugin.get_visitors(""):
                visitor.leave_directory(directory_path)

    def on_file_found(self, file_path: str) -> None:
        for plugin in self.plugins:
            for visitor in plugin.get_visitors(""):
                visitor.visit_file(file_path)


class PluginBasedFilter(ITraverseFilter):
    def __init__(self, plugins: List[BasePlugin]):
        self.plugins = plugins

    def should_visit_file(self, file_path: str) -> bool:
        return all(
            visitor.should_visit_file(file_path)
            for plugin in self.plugins
            for visitor in plugin.get_visitors("")
        )

    def should_visit_directory(self, directory_path: str) -> bool:
        return all(
            visitor.should_visit_subdirectory(directory_path)
            for plugin in self.plugins
            for visitor in plugin.get_visitors("")
        )


class PromptGenerator:
    def __init__(self, root_dir: str, plugins: List[BasePlugin], logger: logging.Logger = None):
        self.root_dir = root_dir.rstrip(os.sep)
        self.plugins = plugins
        self.logger = logger or logging.getLogger(__name__)
        self.skipped_files_count = 0

    def create_walker(self, prompt_dir: str) -> DirectoryWalker:
        return DirectoryWalker(
            prompt_dir,
            traverser=PluginBasedTraverser(self.plugins),
            traverse_filter=PluginBasedFilter(self.plugins)
        )

    def create_directory_structure_prompt(self, prompt_dir: str) -> str:
        walker = self.create_walker(prompt_dir)
        tree = {}
        
        for file_path in sorted(walker.walk()):
            if file_path.startswith(self.root_dir):
                relative_path = file_path[len(self.root_dir) + 1:]
                parts = relative_path.split(os.sep)
                current_level = tree
                for part in parts[:-1]:
                    current_level = current_level.setdefault(part, {})
                current_level[parts[-1]] = {}

        return "\n./\n" + self._format_tree_output(tree, 0)

    def create_file_contents_prompt(self, prompt_dir: str) -> str:
        walker = self.create_walker(prompt_dir)
        prompt = []

        for file_path in walker.walk():
            if os.path.isfile(file_path):
                content = self._read_file_content(file_path)
                if content is not None:
                    relative_path = os.path.relpath(file_path, self.root_dir)
                    prompt.append(f"=========={relative_path}:\n{content}\n")

        if self.skipped_files_count > 0:
            self.logger.warning(f"Skipped {self.skipped_files_count} files during content generation")

        return "\n".join(prompt)

    def _read_file_content(self, file_path: str) -> str | None:
        try:
            encoding = self._detect_file_encoding(file_path)
            if encoding is None:
                self.logger.warning(f"Could not detect encoding for {file_path}")
                self.skipped_files_count += 1
                return None

            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            self.skipped_files_count += 1
            return None

    def _detect_file_encoding(self, file_path: str) -> str | None:
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(1024)
                result = chardet.detect(raw_data)
                return result['encoding']
        except Exception as e:
            self.logger.error(f"Error detecting encoding for {file_path}: {e}")
            return None

    def _format_tree_output(self, node: dict, indent_level: int) -> str:
        lines = []
        for name, subdict in sorted(node.items()):
            indent = '    ' * indent_level
            if subdict:
                lines.append(f"{indent}{name}/")
                lines.append(self._format_tree_output(subdict, indent_level + 1))
            else:
                lines.append(f"{indent}{name}")
        return "\n".join(lines)
