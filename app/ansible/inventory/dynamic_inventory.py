import logging

from fastapi import Depends
from sqlalchemy.orm import Session

from ...internal.sql.crud import get_remote_host_by_ip_address
from ...internal.utils.ansible import ansible_export_to_yaml
from ...internal.utils.enum import FlowerType
from ...internal.utils.validator import validate_ip_address
from ...routers.database import get_db

FLOWER_SERVER_GROUP = "flower_server"
FLOWER_CLIENTS_GROUP = "flower_clients"

FLOWER_INVENTORY = {
    "all": {
        "children": {
            FLOWER_SERVER_GROUP: {"hosts": None},
            FLOWER_CLIENTS_GROUP: {"hosts": None},
        },
        "vars": {
            "ansible_connection": "ssh",
        },
    }
}


def add_new_host_to_flower_inventory(
    host_identifier: str,
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
        host = get_remote_host_by_ip_address(db, ansible_host)
        if host == None:
            raise Exception(
                f"Host {ansible_host} not found in the inventory, it must be added first"
            )

        identifier = f"host{host.id}_{host_identifier}"

        if flower_type == FlowerType.client:
            empty = (
                FLOWER_INVENTORY["all"]["children"][FLOWER_CLIENTS_GROUP]["hosts"]
                == None
            )

            if (
                not empty
                and identifier
                in FLOWER_INVENTORY["all"]["children"][FLOWER_CLIENTS_GROUP][
                    "hosts"
                ].keys()
            ):
                raise Exception(
                    f"Flower client host {ansible_host} already exists in the inventory"
                )

            if empty:
                FLOWER_INVENTORY["all"]["children"][FLOWER_CLIENTS_GROUP]["hosts"] = {}

            FLOWER_INVENTORY["all"]["children"][FLOWER_CLIENTS_GROUP]["hosts"][
                identifier
            ] = {
                "ansible_host": ansible_host,
                "ansible_user": ansible_user,
            }
        else:
            empty = (
                FLOWER_INVENTORY["all"]["children"][FLOWER_SERVER_GROUP]["hosts"]
                == None
            )

            if (
                not empty
                and identifier
                in FLOWER_INVENTORY["all"]["children"][FLOWER_SERVER_GROUP][
                    "hosts"
                ].keys()
            ):
                raise Exception(
                    f"Flower server host {ansible_host} already exists in the inventory"
                )

            if empty:
                FLOWER_INVENTORY["all"]["children"][FLOWER_SERVER_GROUP]["hosts"] = {}

            FLOWER_INVENTORY["all"]["children"][FLOWER_SERVER_GROUP]["hosts"][
                identifier
            ] = {"ansible_host": ansible_host, "ansible_user": ansible_user}

        ansible_export_to_yaml(
            FLOWER_INVENTORY, "./app/ansible/inventory/flower_inventory.yaml"
        )

    except Exception as e:
        logging.error("Exeption occured in add_new_host_to_flower_inventory")
        raise e
