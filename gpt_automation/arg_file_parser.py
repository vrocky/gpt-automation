import configparser

from gpt_automation.impl.conf.conf_reader import parse_key_value_file


class ArgFileParser:
    """
    Parses configuration files and merges them with command line arguments.
    """

    def __init__(self, arg_files):
        self.arg_files = arg_files
        self.file_args = self.load_conf_files()

    def load_conf_files(self):
        """
        Load and parse .conf files to extract arguments.
        """
        config = {}
        for filename in self.arg_files:
            config.update(parse_key_value_file(filename))
        return config

    def merge_args(self, cmdline_args):
        """
        Merge command line arguments with file arguments.
        """
        merged_args = self.file_args.copy()  # Start with file-based arguments
        # Command-line args overwrite file-based args if they exist
        merged_args.update(cmdline_args)
        return merged_args
