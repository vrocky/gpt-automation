# gpt_automation/directory_walker.py
import os


class DirectoryWalker:
    def __init__(self, path, plugin_manager):
        self.path = path
        visitors = plugin_manager.get_all_visitors()
        self.visitors = visitors if isinstance(visitors, list) else [visitors]

    def walk(self):
        visited_dirs = set()
        yield from self._walk(self.path, visited_dirs)

    def _walk(self, directory_path, visited_dirs):
        if directory_path in visited_dirs:
            return
        visited_dirs.add(directory_path)

        # Notify all visitors before traversal
        for visitor in self.visitors:
            visitor.enter_directory(directory_path)

        entries = list(os.scandir(directory_path))
        subdirectories, file_names = [], []
        for entry in entries:
            if entry.is_dir(follow_symlinks=False):
                subdirectories.append(entry.path)
            elif entry.is_file():
                file_names.append(entry.path)

        for filename in file_names:
            if all(visitor.should_visit_file(filename) for visitor in self.visitors):
                for visitor in self.visitors:
                    visitor.visit_file(filename)
                yield filename

        for subdir in subdirectories:
            if all(visitor.should_visit_subdirectory(subdir) for visitor in self.visitors):
                yield from self._walk(subdir, visited_dirs)

        # Notify all visitors after traversal
        for visitor in self.visitors:
            visitor.leave_directory(directory_path)
