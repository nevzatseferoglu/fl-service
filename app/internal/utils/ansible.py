import logging
from os import linesep
from pathlib import Path

import yaml


def ansible_export_to_yaml(dict: dict, file_name: str, is_playbook: bool = False):
    """Export a dictionary to a yaml file"""

    file_path = Path(file_name)

    # Create the directory if it does not exist
    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with file_path.open("w") as yaml_file:
            if not is_playbook:
                yaml_file.write("# code: language=ansible" + 2 * linesep)
            else:
                yaml_file.write("---" + linesep)
            yaml.dump(dict, yaml_file, default_flow_style=False, sort_keys=False)
        logging.info(f"Successfully exported dictionary to {file_name}")
    except IOError as e:
        logging.error(f"Failed to export dictionary to {file_name} as a yaml file, {e}")
