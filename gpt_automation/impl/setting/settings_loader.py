import json
from gpt_automation.impl.setting.settingmerger import SettingMerger


def load_config_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return SettingMerger(data)
