import configparser


class ConfigurationLoader:
    """
    Loads and merges configuration from files and command line arguments.
    """
    def __init__(self, file_paths):
        self.file_paths = file_paths if file_paths is not None else []
        self.file_configurations = self.load_file_configurations()

    def load_file_configurations(self):
        """
        Loads configurations from specified file paths.
        """
        configurations = {}
        for path in self.file_paths:
            configurations.update(self.parse_configuration_file(path))
        return configurations

    @staticmethod
    def parse_configuration_file(file_path):
        """
        Parses a key-value configuration file into a dictionary.
        """
        parser = configparser.ConfigParser()
        parser.read(file_path)
        # Assuming standard INI file format for simplicity
        return {section: dict(parser.items(section)) for section in parser.sections()}

    def merge_with_command_line(self, cmd_args):
        """
        Merges command line arguments with file-based configurations.
        """
        merged_config = self.file_configurations.copy()
        merged_config.update(cmd_args)  # Command-line arguments override file configurations
        return merged_config
