# file_pattern_filter.py
from pathlib import Path


class FilePatternFilter:
    def __init__(self, patterns):
        self.patterns = patterns

    def filter_files(self, files):
        """Filter files based on the patterns specified in the plugin's manifest."""
        filtered_files = []
        for file in files:
            if any(Path(file).match(pattern) for pattern in self.patterns):
                filtered_files.append(file)
        return filtered_files
