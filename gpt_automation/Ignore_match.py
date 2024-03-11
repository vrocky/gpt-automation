import os

from gpt_automation.utils.gitignore_parser2 import parse_patterns_with_base_dir


class IgnoreMatch:
    def __init__(self, base_pattern_pairs):
        # Now expects an array of (base_path, pattern) tuples
        self.matches = [
            parse_patterns_with_base_dir(base_path, [pattern]) for base_path, pattern in base_pattern_pairs
        ]

    def match(self, file_path):
        return any(match(file_path) for match in self.matches)

    def has_matches(self):
        # Since each match function represents a single pattern from a specific base,
        # we can assume there's at least one non-empty pattern if self.matches is not empty.
        return bool(self.matches)

    @staticmethod
    def _is_file_effectively_empty(file_path):
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'r') as file:
                content = file.read().strip()
                return len(content) == 0
        return True


    @staticmethod
    def _is_file_effectively_empty(file_path):
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'r') as file:
                content = file.read().strip()
                return len(content) == 0
        return True
