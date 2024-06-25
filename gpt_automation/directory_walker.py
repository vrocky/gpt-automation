import os


class DirectoryWalker:
    def __init__(self, path, visitor):
        self.path = path
        self.visitor = visitor  # This should be an instance of a class that implements BaseVisitor

    def walk(self):
        visited_dirs = set()
        yield from self._walk(self.path, visited_dirs)

    def _walk(self, directory_path, visited_dirs):
        if directory_path in visited_dirs:
            return
        visited_dirs.add(directory_path)

        self.visitor.before_traverse_directory(directory_path)  # Before traversal hook
        if self.visitor.should_visit_subdirectory(directory_path):  # Check if we should proceed
            self.visitor.enter_directory(directory_path)
            entries = list(os.scandir(directory_path))
            subdirectories, file_names = [], []
            for entry in entries:
                if entry.is_dir(follow_symlinks=False):
                    subdirectories.append(entry.path)
                elif entry.is_file():
                    file_names.append(entry.path)

            for filename in file_names:
                if self.visitor.should_visit_file(filename):
                    self.visitor.visit_file(filename)
                    yield filename

            for subdir in subdirectories:
                if self.visitor.should_visit_subdirectory(subdir):
                    yield from self._walk(subdir, visited_dirs)

            self.visitor.leave_directory(directory_path)
