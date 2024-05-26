from gitignore_parser import _normalize_path, rule_from_pattern, handle_negation
from typing import List


class GitIgnoreRule:
    def __init__(self, pattern, base_path, source, negation=False):
        self.rule = rule_from_pattern(pattern, base_path, source)
        self.pattern = pattern
        self.base_path = base_path
        self.source = source
        self.negation = negation

    def match(self, file_path):
        if self.rule:
            match = self.rule.match(file_path)
            print(f"Matching {file_path} against pattern '{self.pattern}' with negation={self.negation}: {match}")
            return match
        print(f"No valid rule available to match {file_path} against pattern '{self.pattern}'")
        return False

    def __str__(self):
        return f"GitIgnoreRule(pattern='{self.pattern}', base_path='{self.base_path}', source={self.source}, negation={self.negation})"

class GitIgnoreRules:
    def __init__(self, base_dir: str, patterns: List[str]):
        self.base_dir = _normalize_path(base_dir)
        self.rules = self._parse_patterns(patterns)

    def _parse_patterns(self, patterns):
        rules = []
        for counter, line in enumerate(patterns, start=1):
            line = line.rstrip('\n')
            rule = GitIgnoreRule(line, self.base_dir, ("direct input", counter))
            rules.append(rule)
        return rules

    def matches(self, file_path):
        normalized_path = _normalize_path(file_path)
        print(f"Processing file path '{file_path}' with normalized path '{normalized_path}'")

        has_negation = any(r.negation for r in self.rules)
        print(f"Negation present in rules: {has_negation}")

        if not has_negation:
            for rule in self.rules:
                if rule.match(normalized_path):
                    print(f"File '{normalized_path}' matched by rule: {rule}")
                    return True
                else:
                    print(f"File '{normalized_path}' did not match rule: {rule}")
            print("No matches found for file without negation rules.")
            return False
        else:
            # Handle negation logic, you might need to add debug outputs in your handle_negation function as well
            result = handle_negation(normalized_path, [r.rule for r in self.rules])
            print(f"Negation rules applied. Final match result for '{normalized_path}': {result}")
            return result
    def __str__(self):
        return f"GitIgnoreRules(base_dir='{self.base_dir}', rules={[str(r) for r in self.rules]})"


# Usage in your code
def parse_patterns_with_base_dir(base_dir: str, patterns: List[str]):
    return GitIgnoreRules(base_dir, patterns)
