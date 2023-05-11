import os

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from ...internal.sql import crud
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
    host_pattern: str | None,
    ansible_host: str,
    ansible_user: str,
    flower_type: FlowerType,
    db: Session = Depends(get_db),
) -> None:
    """
    Add a new host to flower inventory file.

    This function doesn't validate the given remote host. The caller should validate the remote host (IPAddress, OS type) before calling this function.
    :param inventory_dirname: the name of the inventory directory
    :param host_pattern: the host pattern in the inventory file
    :param ansible_host: the IP address of the remote host
    :param ansible_user: the username of the remote host
    :param flower_type: the type of the remote host (server or client)
    :param db: the database session
    """

    # ensure that given host is already registered in the database
    host = get_remote_host_by_ip_address(db, ansible_host)
    if host == None:
        err = f"Host {ansible_host} not found in the database, it must be added first"
        raise HTTPException(status_code=404, detail=err)

    # federated learning distinct directory
    yaml_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), inventory_dirname
    )

    # federated learning inventory file
    yaml_file = os.path.join(yaml_dir, f"{inventory_dirname}.yaml")

    if os.path.exists(yaml_file) == False:
        if create_file(yaml_file) == False:
            err = f"Failed to create inventory file {yaml_file}"
            raise HTTPException(status_code=500, detail=err)
        if not ansible_export_to_yaml(dict(FLOWER_INVENTORY_DICT), yaml_file):
            err = f"Failed to write inventory file {yaml_file}, check out the logs for more details"
            raise HTTPException(status_code=500, detail=err)

    tmp_dir = os.path.join(yaml_dir, "tmp")
    if os.path.isdir(tmp_dir) == False:
        os.makedirs(name=tmp_dir, exist_ok=True)

    # read the content of the file as a dict then modify rewrite again.
    content = ansible_read_yaml(yaml_file)
    if content == {}:
        err = f"Failed to read inventory file {yaml_file}, check out the logs for more details"
        raise HTTPException(status_code=500, detail=err)

    if host_pattern == None:
        host_pattern = f"host_{host.id}"

    # update the host pattern in the database
    crud.update_remote_host_host_pattern_by_ip_address(
        db=db, ip_address=ansible_host, host_pattern=host_pattern
    )

    if flower_type == FlowerType.client:
        if (
            host_pattern
            in content["all"]["children"][FLOWER_CLIENTS_GROUP]["hosts"].keys()
        ):
            err = f"Flower client host {ansible_host} already exists in the inventory {yaml_file}"
            raise HTTPException(status_code=409, detail=err)

        content["all"]["children"][FLOWER_CLIENTS_GROUP]["hosts"][host_pattern] = {
            "ansible_host": ansible_host,
            "ansible_user": ansible_user,
        }
    else:
        if (
            host_pattern
            in content["all"]["children"][FLOWER_SERVER_GROUP]["hosts"].keys()
        ):
            err = f"Flower server host {ansible_host} already exists in the inventory {yaml_file}"
            raise HTTPException(status_code=409, detail=err)

        content["all"]["children"][FLOWER_SERVER_GROUP]["hosts"][host_pattern] = {
            "ansible_host": ansible_host,
            "ansible_user": ansible_user,
        }

    if not ansible_export_to_yaml(content, yaml_file):
        err = f"Failed to write inventory file {yaml_file}, check out the logs for more details"
        raise HTTPException(status_code=500, detail=err)
