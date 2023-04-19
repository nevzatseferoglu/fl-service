from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from .. import schemas
from ..utils.enums import OsType
from . import models


def get_remote_machine(db: Session, remote_machine_id: int) -> models.RemoteMachine:
    # TODO: Add exception handling
    """Returns a remote machine with the given id"""

    return (
        db.query(models.RemoteMachine)
        .filter(models.RemoteMachine.id == remote_machine_id)
        .first()
    )


def get_remote_machines_by_contact_info(
    db: Session, contact_info: str
) -> list[models.RemoteMachine]:
    # TODO: Add exception handling
    """Returns a list of remote machines that have the given contact info"""

    return (
        db.query(models.RemoteMachine)
        .filter(models.RemoteMachine.contact_info == contact_info)
        .all()
    )


def get_remote_machines(
    db: Session, skip: int = 0, limit: int = 100
) -> list[models.RemoteMachine]:
    # TODO: Add sorting logic so that the returned list is sorted in a predictable order
    # TODO: Add exception handling
    """Returns a list of remote machines"""

    return db.query(models.RemoteMachine).offset(skip).limit(limit).all()


def get_remote_machine_by_ip_address(
    db: Session, ip_address: str
) -> models.RemoteMachine:
    """Returns a remote machine with the given ip address"""

    try:
        return (
            db.query(models.RemoteMachine)
            .filter(str(models.RemoteMachine.ip_address) == ip_address)
            .first()
        )
    except SQLAlchemyError as e:
        err = (
            f"SQLAlchemy error occurred while getting remote machine by ip address: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )


def register_remote_machine(db: Session, remote_machine: schemas.RemoteMachineCreate):
    # TODO ip_address can be used as a unique identifier (primary key)
    """Creates a new remote machine"""

    try:
        # only linux is supported for now
        if remote_machine.os_type != OsType.linux:
            raise HTTPException(
                status_code=400,
                detail="Invalid os_type! (os_type: {remote_machine.os_type})",
            )

        # ensure that the remote machine doesn't already exist
        if get_remote_machine_by_ip_address(db, remote_machine.ip_address) != None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Remote machine with the given IP address already exists",
            )

        # TODO prevent explicit convertion to string
        db_remote_machine = models.RemoteMachine(
            **remote_machine.dict(exclude={"ip_address"}),
            ip_address=str(remote_machine.ip_address),
        )

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

    except Exception as e:
        db.rollback()
        err = f"Unknown error occurred while creating remote machine: {e}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )
