from gitignore_parser import _normalize_path, rule_from_pattern, handle_negation
from typing import List


class GitIgnoreParser:
    def __init__(self, base_dir: str, patterns: List[str]):
        self.base_dir = _normalize_path(base_dir)
        self.patterns = patterns  # Save patterns as an attribute
        self.rules = self.parse_patterns(patterns)

    def parse_patterns(self, patterns: List[str]) -> List:
        rules = []
        for counter, line in enumerate(patterns, start=1):
            line = line.rstrip('\n')
            rule = rule_from_pattern(line, base_path=self.base_dir, source=("direct input", counter))
            if rule:
                rules.append(rule)
        return rules

    def match(self, file_path: str) -> bool:
        """Determine if the file path matches any of the ignore rules."""
        if not any(r.negation for r in self.rules):
            return any(r.match(file_path) for r in self.rules)
        else:
            return handle_negation(file_path, self.rules)

    def __str__(self):
        return f"Base Directory: {self.base_dir}\nPatterns: {self.patterns}"
