import os

from gpt_automation.utils.gitignore_parser2 import parse_patterns_with_base_dir


class IgnoreMatch:
    def __init__(self, base_pattern_pairs):
        # Expects an array of (base_path, pattern) tuples
        self.base_pattern_pairs = base_pattern_pairs
        # Creates a list of GitIgnoreRules objects for each (base_path, pattern) pair
        self.matches = [
            parse_patterns_with_base_dir(base_path, [pattern]) for base_path, pattern in base_pattern_pairs
        ]

    def match(self, file_path):
        # Enhanced debugging: prints the result of each pattern match attempt
        print(f"Attempting to match file: {file_path}")
        for i, matcher in enumerate(self.matches):
            if matcher.matches(file_path):
                print(f"File {file_path} matches with pattern from {self.base_pattern_pairs[i]}")
                return True
            else:
                print(f"No match for file {file_path} with pattern from {self.base_pattern_pairs[i]}")
        return False
    def has_matches(self):
        # Checks if there are any active rules (non-empty pattern lists)
        return any(match.rules for match in self.matches)

    @staticmethod
    def _is_file_effectively_empty(file_path):
        # Checks if a file exists and is not effectively empty (ignores whitespace)
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'r') as file:
                content = file.read().strip()
                return len(content) == 0
        return True

    def __str__(self):
        # Provides a string representation that lists all base_path and pattern pairs
        return f"IgnoreMatch(base_pattern_pairs={self.base_pattern_pairs})"
