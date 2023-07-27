import sys
import os
import configparser
from gpt_automation.main import main


def read_config():
    config = configparser.ConfigParser()
    config.read("tests/config.ini")
    return config["main"]


def run_main_with_args(args):
    sys.argv = args
    main()


if __name__ == "__main__":
    config = read_config()

    # Get the absolute path of main.py
    main_path = os.path.abspath("gpt_automation/main.py")

    # Construct the arguments list using the values from the config file
    args = [main_path, "prompt-all", "--black-list-file", config["black_list_file"],
            "--white-list-file", config["white_list_file"], "--project-path", config["project_path"]]

    run_main_with_args(args)
