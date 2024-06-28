import json
from copy import deepcopy


class Config:
    def __init__(self, data):
        self.data = deepcopy(data)

    def merge(self, other):
        merged_data = self._merge_dicts(self.data, other.data)
        return Config(merged_data)

    def _merge_dicts(self, base, other):
        result = deepcopy(base)
        for key, value in other.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dicts(result[key], value)
            elif key in result and isinstance(result[key], list) and isinstance(value, list):
                result[key].extend(value)
            else:
                result[key] = deepcopy(value)
        return result

    def __str__(self):
        return json.dumps(self.data, indent=4)
