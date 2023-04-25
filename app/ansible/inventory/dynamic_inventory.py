import logging

import yaml
from anyio import Path

from app.internal.utils.validator import validate_ip_address

from ...internal.sql.crud import get_remote_machine_by_ip_address

FLOWER_INVENTORY = {
    "all": {
        "children": {
            "flower_server": {
                "hosts": [],
            },
            "flower_clients": {
                "hosts": [],
            },
        },
        "vars": {
            "ansible_connection": "ssh",
        },
    }
}


def export_to_yaml(dictionary: dict, file_name: str):
    file_path = Path(file_name)

    # Create the directory if it does not exist
    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with file_path.open("w") as yaml_file:
            yaml.dump(dictionary, yaml_file, default_flow_style=False, sort_keys=False)
        logging.info(f"Successfully exported dictionary to {file_name}")
    except IOError as e:
        logging.error(f"occurred while trying to write to file {file_name}: {e}")


def add_new_host_to_flower_server_inventory(
    machine_identifier: str, ansible_host: str, ansible_user: str
) -> None:
    """Add a new host to the inventory file as a server"""

    try:
        if validate_ip_address(ansible_host) == False:
            raise Exception(f"Invalid IP address! (ip_address: {ansible_host})")

        # check if the host is in the inventory
        host = get_remote_machine_by_ip_address(ansible_host)
        if host == None:
            raise Exception(
                f"Host {ansible_host} not found in the inventory, it must be added first"
            )

        if machine_identifier == "":
            raise Exception(f"Hostname cannot be empty")

    except Exception as e:
        logging.error("occurred while trying to add a new host to the inventory")
        raise e

    new_host = {
        f"{machine_identifier}_{host.id}": {
            "ansible_user": ansible_user,
            "ansible_host": ansible_host,
        },
    }

    FLOWER_INVENTORY["all"]["children"]["flower_server"]["hosts"].append(new_host)


def add_new_vars(pairs: dict) -> None:
    """Add new vars to the inventory file"""

    FLOWER_INVENTORY["all"]["children"]["flower_server"]["vars"].update(pairs)


def delete_var(key: str) -> None:
    """Delete vars from the inventory file"""

    FLOWER_INVENTORY["all"]["children"]["flower_server"]["vars"].pop(key)
