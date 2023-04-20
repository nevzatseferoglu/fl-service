from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from .. import schema
from ..utils.enum import OsType
from ..utils.validator import validate_ip_address
from . import models

# NOTE: Don't use logging in crud functions. Instead, use logging in the calling function.


def get_remote_machines_by_contact_info(
    db: Session, contact_info: str
) -> list[models.RemoteMachine]:
    """Returns a list of remote machines that have the given contact info"""

    try:
        return (
            db.query(models.RemoteMachine)
            .filter(models.RemoteMachine.contact_info == contact_info)
            .all()
        )
    except SQLAlchemyError as e:
        err = f"SQLAlchemy error occurred while getting remote machines by contact info: {e}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )


def get_remote_machines(
    db: Session, skip: int = 0, limit: int = 100
) -> list[models.RemoteMachine]:
    """Returns a list of remote machines"""
    # TODO: Add sorting logic so that the returned list is sorted in a predictable order

    try:
        return db.query(models.RemoteMachine).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        err = f"SQLAlchemy error occurred while getting remote machines: {e}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )


def get_remote_machine_by_ip_address(
    db: Session, ip_address: str
) -> models.RemoteMachine:
    """Returns a remote machine with the given ip address"""

    try:
        return (
            db.query(models.RemoteMachine)
            .filter(models.RemoteMachine.ip_address == ip_address)
            .first()
        )
    except SQLAlchemyError as e:
        err = (
            f"SQLAlchemy error occurred while getting remote machine by ip address: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )


def register_remote_machine(db: Session, remote_machine: schema.RemoteMachineCreate):
    """Creates a new remote machine"""

    # only linux is supported for now
    if remote_machine.os_type != OsType.linux:
        raise HTTPException(
            status_code=400,
            detail="Invalid os_type! (os_type: {remote_machine.os_type})",
        )

    if validate_ip_address(remote_machine.ip_address) == False:
        raise HTTPException(
            status_code=400,
            detail="Invalid IP address! (ip_address: {remote_machine.ip_address})",
        )

    try:
        # ensure that the remote machine doesn't already exist
        if get_remote_machine_by_ip_address(db, remote_machine.ip_address) != None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Remote machine with the given IP address already exists",
            )

        # TODO prevent explicit convertion to string
        db_remote_machine = models.RemoteMachine(**remote_machine.dict())

        db.add(db_remote_machine)
        db.commit()
        db.refresh(db_remote_machine)

    except IntegrityError as e:
        db.rollback()
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Remote machine with the given IP address already exists",
            )
        else:
            err = f"IntegrityError occurred while creating remote machine: {e}"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
            )

    except SQLAlchemyError as e:
        db.rollback()
        err = f"SQLAlchemyError occurred while creating remote machine: {e}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )

    except HTTPException as e:
        # intentionally to avoid double logging
        raise e

    except Exception as e:
        db.rollback()
        err = f"Unknown error occurred while creating remote machine: {e}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )
