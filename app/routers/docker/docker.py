import logging
import os
import shutil
from typing import Annotated, Any

import ansible_runner
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from ...definitions import ANSIBLE_INVENTORY_DIR, ANSIBLE_PLAYBOOK_DIR
from ...internal.schema import Status
from ...internal.sql import crud
from ...internal.utils.enum import InstallationStatus, StatusType
from ...internal.utils.validator import validate_ip_address
from ...routers.database import get_db

router = APIRouter(
    prefix="/docker",
    tags=["docker"],
)


def closure_docker_installation_event_handler(
    ip_address: str, db: Session = Depends(get_db)
):
    def docker_installation_event_handler(data: dict):
        if (
            "event_data" in data
            and "task" in data["event_data"]
            and data["event_data"]["task"] == "Gathering Facts"
        ):
            return

        match data["event"]:
            case "playbook_on_task_start":
                logging.info("playbook_on_task_start")
            case "runner_on_start":
                logging.info("runner_on_start")
            case "runner_on_ok":
                logging.info("runner_on_ok")
                info = f"Task {data['event_data']['task']} completed successfully..."
                logging.info(info)
                info = f"Updating database..."
                logging.info(info)

                crud.update_remote_host_docker_state_by_ip_address(
                    db=db,
                    ip_address=ip_address,
                    updated_docker_state={str(data["event_data"]["task"]): InstallationStatus.ok},
                )

                info = f"Database updated..."
                logging.info(info)

            case "runner_on_failed":
                logging.info("runner_on_failed")
                info = f"Task {data['event_data']['task']} is failed..."
                logging.info(info)

                info = f"Updating database..."
                logging.info(info)

                crud.update_remote_host_docker_state_by_ip_address(
                    db=db,
                    ip_address=ip_address,
                    updated_docker_state={
                        str(data["event_data"]["task"]): InstallationStatus.failed
                    },
                )

                info = f"Database updated..."
                logging.info(info)

            case "runner_on_unreachable":
                logging.info("runner_on_unreachable)")
                info = f"Task {data['event_data']['task']} is unreachable..."
                logging.info(info)

                info = f"Updating database..."
                logging.info(info)

                crud.update_remote_host_docker_state_by_ip_address(
                    db=db,
                    ip_address=ip_address,
                    updated_docker_state={
                        str(data["event_data"]["task"]): InstallationStatus.unreachable
                    },
                )

                info = f"Database updated..."
                logging.info(info)

            case "runner_on_skipped":
                logging.info("runner_on_skipped")
                info = f"Task {data['event_data']['task']} is skipped..."
                logging.info(info)

                info = f"Updating database..."
                logging.info(info)

                crud.update_remote_host_docker_state_by_ip_address(
                    db=db,
                    ip_address=ip_address,
                    updated_docker_state={
                        str(data["event_data"]["task"]): InstallationStatus.skipped
                    },
                )

                info = f"Database updated..."
                logging.info(info)
        return True

    
    return docker_installation_event_handler


@router.post("/install/{ip_address}")
def install_docker(
    ip_address: Annotated[str, Path()], db: Session = Depends(get_db)
) -> Any:
    """
    Install Docker on the remote host. The hostmachine is needed to be registered in the database first.
    """

    logging.info(f"Validating ip address {ip_address}...{os.linesep}")
    if not validate_ip_address(ip_address):
        err = f"IP address {ip_address} is not valid"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    logging.info(
        f"Checking if remote host with ip address {ip_address} exists in database..."
    )
    host = crud.get_remote_host_by_ip_address(db=db, ip_address=ip_address)
    if host == None:
        err = f"Remote host with ip address {ip_address} not found in database"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)

    logging.info(
        f"Checking if inventory directory for remote host with ip address {ip_address} exists..."
    )
    inventory_path = os.path.join(ANSIBLE_INVENTORY_DIR, str(host.fl_identifier))
    if not os.path.exists(inventory_path):
        err = f"Inventory directory for remote host with ip address {ip_address} not found"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)

    tmp_path = os.path.join(inventory_path, "tmp")
    if os.path.exists(tmp_path):
        shutil.rmtree(tmp_path)
    os.makedirs(os.path.join(inventory_path, "tmp"), exist_ok=True)

    handler = closure_docker_installation_event_handler(str(host.ip_address), db=db)
    runner_config = {
        "private_data_dir": os.path.join(inventory_path, "tmp"),
        "inventory": os.path.join(inventory_path, f"{host.fl_identifier}.yaml"),
        "playbook": os.path.join(ANSIBLE_PLAYBOOK_DIR, "docker.yaml"),
        "verbosity": 4,
        "limit": str(host.host_pattern),
        "passwords": {"become_pass": str(host.ssh_password)},
        "event_handler": handler,
    }

    runner = ansible_runner.run(**runner_config)
    if runner.status == "successful":
        return Status(
            status=StatusType.success, description="Ansible playbook run successfully"
        )
    else:
        return Status(
            status=StatusType.error,
            description="Ansible playbook run failed, check out the database to figure out which task(s) failed!",
        )
