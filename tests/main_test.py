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
    main_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gpt_automation/main.py"))

    # Construct the arguments list using the values from the config file
    args = sys.argv
    args[0] = main_path

    run_main_with_args(args)
