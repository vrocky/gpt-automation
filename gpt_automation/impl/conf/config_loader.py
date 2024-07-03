import os

from gpt_automation.impl.conf.conf_reader import parse_key_value_file


class ConfigLoader:
    """Loads all .conf files in a given directory into a single configuration dictionary."""

    def __init__(self, directory):
        self.directory = directory
        self.config = {}

    def load_configs(self):
        """Loads all .conf files in the specified directory if the directory exists."""
        if not os.path.exists(self.directory):
            print(f"Warning: Config directory does not exist at {self.directory}")
            return

        for filename in os.listdir(self.directory):
            if filename.endswith('.conf'):
                file_path = os.path.join(self.directory, filename)
                try:
                    file_config = parse_key_value_file(file_path)
                    self.merge_configs(file_config)
                except Exception as e:
                    print(f"Error reading {filename}: {str(e)}")

    def merge_configs(self, new_config):
        """Merges new configuration dictionary into the existing configuration dictionary."""
        self.config.update(new_config)

    def get_config(self):
        """Returns the complete configuration dictionary."""
        return self.config


# Usage example
if __name__ == "__main__":
    loader = ConfigLoader('/path/to/config/directory')
    loader.load_configs()
    config = loader.get_config()
    if config:  # Only print if there's something to print
        print(config)
    else:
        print("No configuration loaded.")
