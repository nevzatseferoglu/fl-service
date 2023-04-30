import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from app.internal.utils.ansible import ansible_export_to_yaml
from app.internal.utils.enum import FlowerType

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


def test_export_to_yaml():
    ansible_host = "dummy_host"
    ansible_user = "dummy_user"
    identifier = "dummy"
    flower_type = "client"

    if flower_type == FlowerType.client:
        empty = (
            FLOWER_INVENTORY["all"]["children"][FLOWER_CLIENTS_GROUP]["hosts"] == None
        )

        if (
            not empty
            and identifier
            in FLOWER_INVENTORY["all"]["children"][FLOWER_CLIENTS_GROUP]["hosts"].keys()
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
            FLOWER_INVENTORY["all"]["children"][FLOWER_SERVER_GROUP]["hosts"] == None
        )

        if (
            not empty
            and identifier
            in FLOWER_INVENTORY["all"]["children"][FLOWER_SERVER_GROUP]["hosts"].keys()
        ):
            raise Exception(
                f"Flower server host {ansible_host} already exists in the inventory"
            )

        if empty:
            FLOWER_INVENTORY["all"]["children"][FLOWER_SERVER_GROUP]["hosts"] = {}

        FLOWER_INVENTORY["all"]["children"][FLOWER_SERVER_GROUP]["hosts"][
            identifier
        ] = {"ansible_host": ansible_host, "ansible_user": ansible_user}

    try:
        ansible_export_to_yaml(
            dict=FLOWER_INVENTORY, file_name="dummy.yaml", is_playbook=True
        )
    except Exception as e:
        raise e
    else:
        print("Test passed")


if __name__ == "__main__":
    test_export_to_yaml()
