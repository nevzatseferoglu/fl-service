from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from .. import schema
from . import models

# NOTE:
# - Don't use logging in crud functions. Instead, use logging in the calling function.
# - All crud functions should throw appropriate HTTPException instead of SQLAlchemyError when an error occurs.


def get_remote_host_by_contact_info(
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


def get_remote_host_by_host_pattern(
    db: Session, host_pattern: str
) -> models.RemoteHost:
    """
    Returns a remote host with the given host pattern.
    """

    try:
        return (
            db.query(models.RemoteHost)
            .filter(models.RemoteHost.host_pattern == host_pattern)
            .first()
        )
    except SQLAlchemyError as e:
        err = (
            f"SQLAlchemy error occurred while getting remote host by host pattern: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )


def get_docker_state_by_ip_address(
    db: Session, ip_address: str
) -> models.RemoteHostDockerState | None:
    """
    Get docker state of a remote host by ip address.
    """

    try:
        remote_host = (
            db.query(models.RemoteHost)
            .filter(models.RemoteHost.ip_address == ip_address)
            .first()
        )
        if remote_host != None:
            return remote_host.docker_state
        return None

    except SQLAlchemyError as e:
        err = f"SQLAlchemy error occurred while getting docker state by ip address: {e}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )


def update_docker_state_by_host_pattern(
    db: Session,
    host_pattern: str,
    remote_host_docker_state: schema.RemoteHostDockerState,
):
    try:
        remote_host = (
            db.query(models.RemoteHost)
            .filter(models.RemoteHost.host_pattern == host_pattern)
            .first()
        )

        if not remote_host:
            err = f"Remote host with ip address {host_pattern} not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)

        docker_state_id = remote_host.docker_state.id
        updated = remote_host_docker_state.dict()

        update_dict = {f"{k}": v for k, v in updated.items() if v is not None}

        if update_dict:
            db.query(models.RemoteHostDockerState).filter(
                models.RemoteHostDockerState.id == docker_state_id
            ).update(update_dict)
            db.commit()

    except SQLAlchemyError as e:
        err = (
            f"SQLAlchemy error occurred while updating docker state by ip address: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )


def get_remote_host_by_fl_identifier(
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
    except SQLAlchemyError as e:
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
        # initiate remote host
        db_remote_host = models.RemoteHost(**remote_host.dict())
        db.add(db_remote_host)
        db.commit()
        db.refresh(db_remote_host)

        state_docker_installation = models.RemoteHostDockerState(
            {
                "host_id": db_remote_host.id,
                "state_install_aptitude": "",
                "state_install_required_system_packages": "",
                "state_add_docker_gpg_apt_key": "",
                "state_add_docker_repository": "",
                "state_update_apt_and_install_docker_ce": "",
                "state_install_docker_module_for_python": "",
                "general_state": False,
            }
        )
        # initiate remote host docker state
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
