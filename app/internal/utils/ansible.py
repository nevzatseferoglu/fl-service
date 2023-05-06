import logging
import os

import yaml


def ansible_read_yaml(filepath: str) -> dict:
    """
    Read a yaml file and return a dictionary.
    """

    try:
        with open(filepath, "r") as yaml_file:
            return yaml.safe_load(yaml_file)
    except (yaml.YAMLError, OSError) as e:
        logging.error(f"Failed to read {filepath} as a yaml file, {e}")
        return {}


def ansible_export_to_yaml(
    dict: dict, filepath: str, is_playbook: bool = False
) -> bool:
    """
    Export a dictionary to a yaml file.
    """

    try:
        with open(filepath, "w") as yaml_file:
            if not is_playbook:
                yaml_file.write("# code: language=ansible" + 2 * os.linesep)
            else:
                yaml_file.write("---" + os.linesep)
            yaml.dump(dict, yaml_file, default_flow_style=False, sort_keys=False)
        logging.info(f"Successfully exported dictionary to {filepath}")
    except (IOError, OSError) as e:
        logging.error(f"Failed to export dictionary to {filepath} as a yaml file, {e}")
        return False
    else:
        return True
