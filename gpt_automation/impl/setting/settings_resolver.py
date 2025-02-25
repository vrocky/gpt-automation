import os
import json
from typing import Dict, Any
from .setting_models import Settings

class SettingsResolver:
    def __init__(self, base_settings_path: str):
        self.base_settings_path = base_settings_path

    def _load_json_file(self, file_path: str) -> Dict[str, Any]:
        """Load and parse a JSON file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Settings file not found: {file_path}")
        
        with open(file_path, 'r') as f:
            return json.load(f)

    def resolve_settings(self) -> Settings:
        """Resolve base settings and return a Settings object."""
        json_data = self._load_json_file(self.base_settings_path)
        return Settings.from_dict(json_data)