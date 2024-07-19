# main.py
from typing import Dict
import argparse
import yaml


def read_cli_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "--app-env",
        required=True,
        action="store",
        choices=("prod", "dev", "test"),
        help="Application environment to run in"
    )
    return arg_parser.parse_args()


def read_settings(app_env: str) -> Dict:
    try:
        with open("settings.yml", mode="r", encoding="utf-8") as config:
            configs: Dict = yaml.safe_load(config)
    except yaml.YAMLError as yaml_err:
        print(f"Error occurred while reading the file. Error: {yaml_err}")
        raise
    return configs[app_env]


# Program Execution Starts Here
if __name__ == "__main__":
    # Read CLI arguments
    args = read_cli_arguments()

    # Retrieve specific configurations
    settings: Dict = read_settings(app_env=args.app_env)

    print(f"Configs: {settings}")
