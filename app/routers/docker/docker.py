import logging
import os
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ...internal.schema import RemoteHostDockerState
from ...internal.sql import crud
from ...internal.utils.enum import InstallationStatus
from ...routers.database import get_db

router = APIRouter(
    prefix="/docker",
    tags=["docker"],
)


async def docker_installation_event_handler(data: dict):
    match data["event"]:
        case "runner_on_start":
            yield f"Starting task {data['task']}...{os.linesep}"
        case "runner_on_ok":
            yield f"Task {data['task']} completed successfully...{os.linesep}"
            yield f"Updating database...{os.linesep}"
            crud.update_docker_state_by_host_pattern(
                db=Depends(get_db),
                host_pattern=data["host_pattern"],
                remote_host_docker_state=RemoteHostDockerState(
                    **{data["task"]: InstallationStatus.ok}
                ),
            )
            yield f"Database updated...{os.linesep}"
        case "runner_on_failed":
            yield f"Task {data['task']} failed...{os.linesep}"
            yield f"Updating database...{os.linesep}"
            crud.update_docker_state_by_host_pattern(
                db=Depends(get_db),
                host_pattern=data["host_pattern"],
                remote_host_docker_state=RemoteHostDockerState(
                    **{data["task"]: InstallationStatus.failed}
                ),
            )
            yield f"Database updated...{os.linesep}"
        case "runner_on_unreachable":
            yield f"Task {data['task']} is unreachable...{os.linesep}"
            yield f"Updating database...{os.linesep}"
            crud.update_docker_state_by_host_pattern(
                db=Depends(get_db),
                host_pattern=data["host_pattern"],
                remote_host_docker_state=RemoteHostDockerState(
                    **{data["task"]: InstallationStatus.unreachable}
                ),
            )
            yield f"Database updated...{os.linesep}"
        case "runner_on_skipped":
            yield f"Task {data['task']} is skipped...{os.linesep}"
            yield f"Updating database...{os.linesep}"
            crud.update_docker_state_by_host_pattern(
                db=Depends(get_db),
                host_pattern=data["host_pattern"],
                remote_host_docker_state=RemoteHostDockerState(
                    **{data["task"]: InstallationStatus.skipped}
                ),
            )
            yield f"Database updated...{os.linesep}"


async def stream_install_docker_content(host_pattern: str, db: Session):
    yield f"Validating host pattern {host_pattern}...{os.linesep}"
    host = crud.get_remote_host_by_host_pattern(db=db, host_pattern=host_pattern)
    if host == None:
        err = f"Remote host with host pattern {host_pattern} not found in database"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)


@router.post("/install/{host_pattern}", response_class=StreamingResponse)
async def install_docker(
    host_pattern: Annotated[str, Path()], db: Session = Depends(get_db)
) -> Any:
    """
    Install Docker on the remote host. The hostmachine is needed to be registered in the database first.
    """

    try:
        return StreamingResponse(
            stream_install_docker_content(host_pattern=host_pattern, db=db),
            media_type="text/html",
        )
    except HTTPException as e:
        logging.error(e.detail)
        raise e
