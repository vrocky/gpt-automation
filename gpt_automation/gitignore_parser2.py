from gitignore_parser import _normalize_path, rule_from_pattern, handle_negation
from typing import List


def parse_patterns_with_base_dir(base_dir: str, patterns: List[str]):
    rules = []
    base_path = _normalize_path(base_dir)
    for counter, line in enumerate(patterns, start=1):
        line = line.rstrip('\n')
        rule = rule_from_pattern(line, base_path=base_path, source=("direct input", counter))
        if rule:
            rules.append(rule)
    if not any(r.negation for r in rules):
        return lambda file_path: any(r.match(file_path) for r in rules)
    else:
        return lambda file_path: handle_negation(file_path, rules)
