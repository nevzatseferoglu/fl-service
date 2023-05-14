import logging
import os
import shutil
from typing import Annotated

import ansible_runner
from fastapi import Depends, FastAPI, HTTPException, Path, status

from .definitions import ANSIBLE_INVENTORY_DIR, ANSIBLE_PLAYBOOK_DIR
from .internal.schema import Status
from .internal.sql import crud
from .internal.utils.enum import StatusType
from .routers import database, ssh
from .routers.docker import docker

logging.basicConfig(
    filename="uvicorn.log",
    filemode="a",
    format="%(asctime)s:%(levelname)s:%(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG,
)

logging.info("Starting a fresh uvicorn!")


app = FastAPI(debug=True)

app.include_router(ssh.router)
app.include_router(database.router)
app.include_router(docker.router)


@app.get("/ping/{ip_address}")
def ping(ip_address: Annotated[str, Path()], db=Depends(database.get_db)):
    host = crud.get_remote_host_by_ip_address(db=db, ip_address=ip_address)
    if host == None:
        err = f"Remote host with ip address {ip_address} not found in database"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)

    inventory_path = os.path.join(
        ANSIBLE_INVENTORY_DIR, str(host.fl_identifier), f"{host.fl_identifier}.yaml"
    )
    if not os.path.exists(inventory_path):
        err = f"Inventory directory for remote host with ip address {ip_address} not found"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)

    tmp_path = os.path.join(ANSIBLE_INVENTORY_DIR, "ping-tmp")
    if os.path.exists(tmp_path):
        shutil.rmtree(tmp_path)
    os.makedirs(os.path.join(ANSIBLE_INVENTORY_DIR, "ping-tmp"), exist_ok=True)

    runner_config = {
        "private_data_dir": tmp_path,
        "inventory": inventory_path,
        "playbook": os.path.join(ANSIBLE_PLAYBOOK_DIR, "ping.yaml"),
        "verbosity": 2,
        "limit": str(host.host_pattern),
    }
    runner = ansible_runner.run(**runner_config)
    logging.info(runner.status)
    if runner.status == "failed":
        err = f"Ansible runner failed with status {runner.status}"
        logging.error(err)
        if os.path.exists(tmp_path):
            shutil.rmtree(tmp_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )
    else:
        if os.path.exists(tmp_path):
            shutil.rmtree(tmp_path)
        return Status(status=StatusType.success, description="Ping successful!")
