import os

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from ...internal.sql.crud import get_remote_host_by_ip_address
from ...internal.utils.ansible import ansible_export_to_yaml, ansible_read_yaml
from ...internal.utils.enum import FlowerType
from ...internal.utils.file import create_file
from ...routers.database import get_db

FLOWER_SERVER_GROUP = "flower_server"
FLOWER_CLIENTS_GROUP = "flower_clients"


FLOWER_INVENTORY_DICT = {
    "all": {
        "children": {
            FLOWER_SERVER_GROUP: {"hosts": {}},
            FLOWER_CLIENTS_GROUP: {"hosts": {}},
        },
        "vars": {
            "ansible_connection": "ssh",
        },
    }
}


def add_new_host_to_flower_inventory(
    inventory_dirname: str,
    ansible_host: str,
    ansible_user: str,
    flower_type: FlowerType,
    db: Session = Depends(get_db),
) -> None:
    """
    Add a new host to flower inventory file.

    This function doesn't validate the given remote host. The caller should validate the remote host (IPAddress, OS type) before calling this function.
    """

    # ensure that given host is already registered in the database
    host = get_remote_host_by_ip_address(db, ansible_host)
    if host == None:
        err = f"Host {ansible_host} not found in the database, it must be added first"
        raise HTTPException(status_code=404, detail=err)

    yaml_dir = f"{os.path.dirname(__file__)}/{inventory_dirname}"
    yaml_file = f"{yaml_dir}/{inventory_dirname}.yaml"

    if os.path.exists(yaml_file) == False:
        if create_file(yaml_file) == False:
            err = f"Failed to create inventory file {yaml_file}"
            raise HTTPException(status_code=500, detail=err)
        ansible_export_to_yaml(dict(FLOWER_INVENTORY_DICT), yaml_file)

    # read the content of the file as a dict then modify rewrite again.
    content = ansible_read_yaml(yaml_file)
    if content == {}:
        err = f"Failed to read inventory file {yaml_file}, check out the logs for more details"
        raise HTTPException(status_code=500, detail=err)

    # generate unique internal host indentifier (relies on the host id (primary key))
    identifier = f"host_{host.id}"

    if flower_type == FlowerType.client:
        if (
            identifier
            in content["all"]["children"][FLOWER_CLIENTS_GROUP]["hosts"].keys()
        ):
            err = f"Flower client host {ansible_host} already exists in the inventory {yaml_file}"
            raise HTTPException(status_code=409, detail=err)

        content["all"]["children"][FLOWER_CLIENTS_GROUP]["hosts"][identifier] = {
            "ansible_host": ansible_host,
            "ansible_user": ansible_user,
        }
    else:
        if (
            identifier
            in content["all"]["children"][FLOWER_SERVER_GROUP]["hosts"].keys()
        ):
            err = f"Flower server host {ansible_host} already exists in the inventory {yaml_file}"
            raise HTTPException(status_code=409, detail=err)

        content["all"]["children"][FLOWER_SERVER_GROUP]["hosts"][identifier] = {
            "ansible_host": ansible_host,
            "ansible_user": ansible_user,
        }

    if ansible_export_to_yaml(content, yaml_file) == False:
        err = f"Failed to write inventory file {yaml_file}, check out the logs for more details"
        raise HTTPException(status_code=500, detail=err)
