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
    """Returns a list of remote hosts that have the given contact info"""

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
    """Returns a list of remote hosts"""
    # TODO: Add sorting logic so that the returned list is sorted in a predictable order

    try:
        return db.query(models.RemoteHost).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        err = f"SQLAlchemy error occurred while getting remote hosts: {e}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )


def get_remote_host_by_ip_address(db: Session, ip_address: str) -> models.RemoteHost:
    """Returns a remote host with the given ip address"""

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


def get_remote_host_by_fl_identifier(
    db: Session, fl_identifier: str
) -> list[models.RemoteHost]:
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
