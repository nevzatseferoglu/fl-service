import logging
import os
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ...definitions import ANSIBLE_INVENTORY_DIR
from ...internal.schema import RemoteHostDockerState
from ...internal.sql import crud
from ...internal.utils.enum import InstallationStatus
from ...internal.utils.validator import validate_ip_address
from ...routers.database import get_db

router = APIRouter(
    prefix="/docker",
    tags=["docker"],
)


async def closure_docker_installation_event_handler(
    ip_address: str, db: Session = Depends(get_db)
):
    async def docker_installation_event_handler(data: dict):
        match data["event"]:
            case "runner_on_start":
                yield f"Starting task {data['task']}...{os.linesep}"
            case "runner_on_ok":
                yield f"Task {data['task']} completed successfully...{os.linesep}"
                yield f"Updating database...{os.linesep}"
                task_state_update = RemoteHostDockerState(
                    **{data["task"]: InstallationStatus.ok}
                )
                crud.update_remote_host_docker_state_by_ip_address(
                    db=db, ip_address=ip_address, updated_docker_state=task_state_update
                )
                yield f"Database updated...{os.linesep}"
            case "runner_on_failed":
                yield f"Task {data['task']} failed...{os.linesep}"
                yield f"Updating database...{os.linesep}"
                task_state_update = RemoteHostDockerState(
                    **{data["task"]: InstallationStatus.failed}
                )
                crud.update_remote_host_docker_state_by_ip_address(
                    db=db, ip_address=ip_address, updated_docker_state=task_state_update
                )
                yield f"Database updated...{os.linesep}"
            case "runner_on_unreachable":
                yield f"Task {data['task']} is unreachable...{os.linesep}"
                yield f"Updating database...{os.linesep}"
                task_state_update = RemoteHostDockerState(
                    **{data["task"]: InstallationStatus.unreachable}
                )
                crud.update_remote_host_docker_state_by_ip_address(
                    db=db, ip_address=ip_address, updated_docker_state=task_state_update
                )
                yield f"Database updated...{os.linesep}"
            case "runner_on_skipped":
                yield f"Task {data['task']} is skipped...{os.linesep}"
                yield f"Updating database...{os.linesep}"
                task_state_update = RemoteHostDockerState(
                    **{data["task"]: InstallationStatus.skipped}
                )
                crud.update_remote_host_docker_state_by_ip_address(
                    db=db, ip_address=ip_address, updated_docker_state=task_state_update
                )
                yield f"Database updated...{os.linesep}"

    return docker_installation_event_handler


async def stream_install_docker_content(ip_address: str, db: Session):
    yield f"Validating ip address {ip_address}...{os.linesep}"
    if not validate_ip_address(ip_address):
        err = f"IP address {ip_address} is not valid"
        yield f"{err}{os.linesep}"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    host = crud.get_remote_host_by_ip_address(db=db, ip_address=ip_address)
    if host == None:
        err = f"Remote host with ip address {ip_address} not found in database"
        yield f"{err}{os.linesep}"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)

    inventory_path = os.path.join(ANSIBLE_INVENTORY_DIR, str(host.fl_identifier))
    if not os.path.exists(inventory_path):
        err = f"Inventory directory for remote host with ip address {ip_address} not found"
        yield f"{err}{os.linesep}"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)

    # mock_handler = closure_docker_installation_event_handler(str(host.ip_address), db)
    # mock_handler()
    # runner_config = {
    #     "private_data_dir": os.path.join(inventory_path, "tmp"),
    #     "inventory": inventory_path,
    #     "playbook": os.path.join(ANSIBLE_PLAYBOOK_DIR, "docker.yml")
    # }


@router.post("/install/{ip_address}", response_class=StreamingResponse)
async def install_docker(
    ip_address: Annotated[str, Path()], db: Session = Depends(get_db)
) -> Any:
    """
    Install Docker on the remote host. The hostmachine is needed to be registered in the database first.
    """

    try:
        return StreamingResponse(
            stream_install_docker_content(ip_address=ip_address, db=db),
            media_type="text/html",
        )
    except HTTPException as e:
        logging.error(e.detail)
        raise e
