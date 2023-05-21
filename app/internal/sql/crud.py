from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from .. import schema
from ..utils.enum import DOCKER_INSTALLATION_NAME
from . import models

# NOTE:
# - All crud functions should throw appropriate HTTPException instead of SQLAlchemyError when an error occurs.

# def from_task_enum_to_model_column(name: str) -> Column | None:
#     match name:
#         case DOCKER_INSTALLATION_NAME.state_install_aptitude:
#             return models.RemoteHostDockerState.state_install_aptitude
#         case DOCKER_INSTALLATION_NAME.state_install_required_system_packages:
#             return models.RemoteHostDockerState.state_install_required_system_packages
#         case DOCKER_INSTALLATION_NAME.state_add_docker_gpg_apt_key:
#             return models.RemoteHostDockerState.state_add_docker_gpg_apt_key
#         case DOCKER_INSTALLATION_NAME.state_add_docker_repository:
#             return models.RemoteHostDockerState.state_add_docker_repository
#         case DOCKER_INSTALLATION_NAME.state_update_apt_and_install_docker_ce:
#             return models.RemoteHostDockerState.state_update_apt_and_install_docker_ce
#         case DOCKER_INSTALLATION_NAME.state_install_docker_module_for_python:
#             return models.RemoteHostDockerState.state_install_docker_module_for_python
#         case DOCKER_INSTALLATION_NAME.state_check_docker_command:
#             return models.RemoteHostDockerState.state_check_docker_command
#         case _:
#             return None


def get_remote_host_docker_state(db: Session, ip_address: str) -> dict:
    "Returns the result of given task, if the task does not exist returns an empty string"

    try:
        remote_host = (
            db.query(models.RemoteHost)
            .options(joinedload(models.RemoteHost.docker_state))
            .filter(
                models.RemoteHost.ip_address == ip_address,
            )
            .first()
        )
        if remote_host == None:
            err = f"Remote host with ip address {ip_address} not found"
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)

        docker_state_id = remote_host.docker_state.id

        result = (
            db.query(models.RemoteHostDockerState)
            .filter(models.RemoteHostDockerState.id == docker_state_id)
            .first()
        )

        if result == None:
            err = f"Remote host docker state with id {docker_state_id} not found"
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)

        return {
            DOCKER_INSTALLATION_NAME.state_install_aptitude: result.state_install_aptitude,
            DOCKER_INSTALLATION_NAME.state_install_required_system_packages: result.state_install_required_system_packages,
            DOCKER_INSTALLATION_NAME.state_add_docker_gpg_apt_key: result.state_add_docker_gpg_apt_key,
            DOCKER_INSTALLATION_NAME.state_add_docker_repository: result.state_add_docker_repository,
            DOCKER_INSTALLATION_NAME.state_update_apt_and_install_docker_ce: result.state_update_apt_and_install_docker_ce,
            DOCKER_INSTALLATION_NAME.state_install_docker_module_for_python: result.state_install_docker_module_for_python,
            DOCKER_INSTALLATION_NAME.state_check_docker_command: result.state_check_docker_command,
        }

    except SQLAlchemyError as e:
        err = f"SQLAlchemy error occurred while getting remote host docker state: {e}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )


def get_remote_hosts_by_contact_info(
    db: Session, contact_info: str
) -> list[models.RemoteHost]:
    """
    Returns a list of remote hosts that have the given contact info.
    """

    try:
        return (
            db.query(models.RemoteHost)
            .filter(models.RemoteHost.contact_info == contact_info)
            .all()
        )
    except SQLAlchemyError as e:
        err = (
            f"SQLAlchemy error occurred while getting remote hosts by contact info: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )


def get_remote_hosts(
    db: Session, skip: int = 0, limit: int = 100
) -> list[models.RemoteHost]:
    """
    Returns a list of remote hosts.
    """
    # TODO: Add sorting logic so that the returned list is sorted in a predictable order

    try:
        return db.query(models.RemoteHost).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        err = f"SQLAlchemy error occurred while getting remote hosts: {e}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )


def get_remote_host_by_ip_address(db: Session, ip_address: str) -> models.RemoteHost:
    """
    Returns a remote host with the given ip address.
    """

    try:
        return (
            db.query(models.RemoteHost)
            .filter(models.RemoteHost.ip_address == ip_address)
            .first()
        )
    except SQLAlchemyError as e:
        err = f"SQLAlchemy error occurred while getting remote host by ip address: {e}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )


def update_remote_host_docker_state_by_ip_address(
    db: Session, ip_address: str, updated_docker_state: dict
) -> None:
    try:
        remote_host = (
            db.query(models.RemoteHost)
            .options(joinedload(models.RemoteHost.docker_state))
            .filter(
                models.RemoteHost.ip_address == ip_address,
            )
            .first()
        )
        if remote_host == None:
            err = f"Remote host with ip address {ip_address} not found"
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)

        docker_state_id = remote_host.docker_state.id

        db.query(models.RemoteHostDockerState).filter(
            models.RemoteHostDockerState.id == docker_state_id
        ).update(updated_docker_state)
        db.commit()

    except SQLAlchemyError as e:
        db.rollback()
        err = f"SQLAlchemy error occurred while updating docker state by host pattern: {e}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )
    except AttributeError as e:
        db.rollback()
        err = (
            f"Attribute error occurred while updating docker state by host pattern: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )


def get_remote_hosts_by_fl_identifier(
    db: Session, fl_identifier: str
) -> list[models.RemoteHost]:
    """
    Returns a list of remote hosts that have the given fl_identifier.
    """

    try:
        return (
            db.query(models.RemoteHost)
            .filter(models.RemoteHost.fl_identifier == fl_identifier)
            .all()
        )
    except SQLAlchemyError as e:
        err = (
            f"SQLAlchemy error occurred while getting remote host by fl_identifier: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )


def update_remote_host_host_pattern_by_ip_address(
    db: Session, ip_address: str, host_pattern: str
):
    try:
        db.query(models.RemoteHost).filter(
            models.RemoteHost.ip_address == ip_address
        ).update({"host_pattern": host_pattern})
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        err = f"SQLAlchemy error occurred while updating remote host host pattern by ip address: {e}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )


def register_remote_host(db: Session, remote_host: schema.RemoteHostCreate):
    """
    Registers a new remote host.

    This function doesn't validate the given remote host. The caller should validate the remote host (IPAddress, OS type) before calling this function.
    """

    try:
        db_remote_host = models.RemoteHost(**remote_host.dict())
        db.add(db_remote_host)
        db.commit()
        db.refresh(db_remote_host)

        state_docker_installation = {
            "host_id": db_remote_host.id,
            DOCKER_INSTALLATION_NAME.state_install_aptitude: "",
            DOCKER_INSTALLATION_NAME.state_install_required_system_packages: "",
            DOCKER_INSTALLATION_NAME.state_add_docker_gpg_apt_key: "",
            DOCKER_INSTALLATION_NAME.state_add_docker_repository: "",
            DOCKER_INSTALLATION_NAME.state_update_apt_and_install_docker_ce: "",
            DOCKER_INSTALLATION_NAME.state_install_docker_module_for_python: "",
            DOCKER_INSTALLATION_NAME.state_check_docker_command: "",
        }

        db_remote_host_docker_state = models.RemoteHostDockerState(
            **state_docker_installation
        )
        db.add(db_remote_host_docker_state)
        db.commit()
        db.refresh(db_remote_host_docker_state)

    except IntegrityError as e:
        db.rollback()
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Remote host with the given IP address already exists",
            )
        else:
            err = f"IntegrityError occurred while registering remote host: {e}"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
            )

    except SQLAlchemyError as e:
        db.rollback()
        err = f"SQLAlchemyError occurred while registering remote host: {e}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )

    except Exception as e:
        db.rollback()
        err = f"Unknown error occurred while registering remote host: {e}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )
