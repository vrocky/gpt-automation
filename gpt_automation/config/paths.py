import os


class PathManager:
    def __init__(self, generate_dir='.'):
        self.generate_dir = generate_dir
        self.base_dir = os.path.join(self.generate_dir, '.gpt', 'config')
        self.profile_dir = os.path.join(self.generate_dir, '.gpt', 'profiles')
        self.resources_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')

    def get_base_config_path(self):
        return os.path.join(self.base_dir, 'base_config.json')

    def get_global_config_path(self):
        return os.path.join(self.base_dir, 'global_config.json')

    def get_profile_config_path(self, profile_name):
        return os.path.join(self.profile_dir, profile_name, 'config.json')
