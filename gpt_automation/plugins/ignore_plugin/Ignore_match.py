import logging
import os

from gpt_automation.impl.third_party.gitignore_parser2.parser2 import GitIgnoreParser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
class IgnoreMatch:
    def __init__(self, base_pattern_pairs):
        # Now expects an array of (base_path, pattern) tuples
        self.base_pattern_pairs = base_pattern_pairs
        self.matches = [
            GitIgnoreParser(base_path, [pattern]) for base_path, pattern in base_pattern_pairs
        ]

    def match2(self, file_path):
        return any(match(file_path) for match in self.matches)

    def match(self, file_path):
        results = []

        for match in self.matches:
            log_dict = {"input": file_path,
                        "match": match.__str__()}
            logging.debug(f"matching: {log_dict}")
            result = match.match(file_path)
            results.append({
                "input": file_path,
                "match": match.__str__(),
                "result": result,
            })

        # Optionally, you could print or log the results array to inspect it
        #print(results)
        logging.debug(f"results:{ results}")
        final_result = any(result['result'] for result in results)
        return final_result

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

    def __str__(self):
        # Provides a string representation that lists all base_path and pattern pairs
        return f"IgnoreMatch(base_pattern_pairs={self.base_pattern_pairs})"
