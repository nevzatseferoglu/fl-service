import logging
from os import linesep
from pathlib import Path

import yaml
from fastapi import Depends
from pytest import Session

from ...internal.schema import FlowerType
from ...internal.sql.crud import get_remote_machine_by_ip_address
from ...internal.utils.validator import validate_ip_address
from ...routers.database import get_db

FLOWER_INVENTORY = {
    "all": {
        "children": {
            "flower_server": {"hosts": None},
            "flower_clients": {"hosts": None},
        },
        "vars": {
            "ansible_connection": "ssh",
        },
    }
}


def ansible_export_to_yaml(dictionary: dict, file_name: str):
    """Export a dictionary to a yaml file"""

    file_path = Path(file_name)

    # Create the directory if it does not exist
    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with file_path.open("w") as yaml_file:
            yaml_file.write("# code: language=ansible")
            yaml_file.write(2 * linesep)
            yaml.dump(dictionary, yaml_file, default_flow_style=False, sort_keys=False)
        logging.info(f"Successfully exported dictionary to {file_name}")
    except IOError as e:
        logging.error(f"Failed to export dictionary to {file_name} as a yaml file, {e}")


def add_new_host_to_flower_inventory(
    machine_identifier: str,
    ansible_host: str,
    ansible_user: str,
    flower_type: FlowerType,
    db: Session = Depends(get_db),
) -> None:
    """Add a new host to flower inventory file"""

    try:
        if validate_ip_address(ansible_host) == False:
            raise Exception(f"Invalid IP address! (ip_address: {ansible_host})")

        # check if the host is in the inventory
        host = get_remote_machine_by_ip_address(db, ansible_host)
        if host == None:
            raise Exception(
                f"Host {ansible_host} not found in the inventory, it must be added first"
            )

        identifier = f"machine{host.id}_{machine_identifier}"

        if flower_type == FlowerType.client:
            empty = (
                FLOWER_INVENTORY["all"]["children"]["flower_clients"]["hosts"] == None
            )

            if (
                not empty
                and identifier
                in FLOWER_INVENTORY["all"]["children"]["flower_clients"]["hosts"].keys()
            ):
                raise Exception(
                    f"Flower client host {ansible_host} already exists in the inventory"
                )

            if empty:
                FLOWER_INVENTORY["all"]["children"]["flower_clients"]["hosts"] = {}

            FLOWER_INVENTORY["all"]["children"]["flower_clients"]["hosts"][
                identifier
            ] = {
                "ansible_host": ansible_host,
                "ansible_user": ansible_user,
            }
        else:
            empty = (
                FLOWER_INVENTORY["all"]["children"]["flower_server"]["hosts"] == None
            )

            if (
                not empty
                and identifier
                in FLOWER_INVENTORY["all"]["children"]["flower_server"]["hosts"].keys()
            ):
                raise Exception(
                    f"Flower server host {ansible_host} already exists in the inventory"
                )

            if empty:
                FLOWER_INVENTORY["all"]["children"]["flower_server"]["hosts"] = {}

            FLOWER_INVENTORY["all"]["children"]["flower_server"]["hosts"][
                identifier
            ] = {"ansible_host": ansible_host, "ansible_user": ansible_user}

        ansible_export_to_yaml(FLOWER_INVENTORY, "flower_inventory.yaml")

    except Exception as e:
        logging.error("Exeption occured in add_new_host_to_flower_inventory")
        raise e
