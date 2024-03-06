import sys
import os
import configparser

from gpt_automation.main import main

def read_config(section, key):
    config = configparser.ConfigParser()
    config.read("config.ini")  # Adjust path as necessary
    if config.has_section(section) and config.has_option(section, key):
        return config.get(section, key)
    else:
        raise ValueError(f"Missing section/key: {section}/{key}")

def run_main_with_args(args):
    original_argv = sys.argv.copy()  # Save the original sys.argv
    sys.argv = args  # Override sys.argv
    try:
        main()
    finally:
        sys.argv = original_argv  # Restore the original sys.argv

if __name__ == "__main__":
    project_path = read_config("main", "project_path")
    main_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gpt_automation/main.py"))

    # Change the current working directory
    os.chdir(project_path)

    args = [main_path]  # Construct args
    print("args:")
    print(args)
    args.append("prompt-dir")
    run_main_with_args(args)
