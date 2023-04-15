import logging

from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy.orm import Session

from .. import schemas
from ..utils.enums import OsType
from . import models


def get_remote_machine(db: Session, remote_machine_id: int) -> models.RemoteMachine:
    """Returns a remote machine with the given id"""

    return (
        db.query(models.RemoteMachine)
        .filter(models.RemoteMachine.id == remote_machine_id)
        .first()
    )


def get_remote_machines_by_contact_info(
    db: Session, contact_info: str
) -> list[models.RemoteMachine]:
    """Returns a list of remote machines that have the given contact info"""

    return (
        db.query(models.RemoteMachine)
        .filter(models.RemoteMachine.contact_info == contact_info)
        .all()
    )


def get_remote_machine_by_ip_address(
    db: Session, ip_address: str
) -> models.RemoteMachine:
    """Returns a remote machine with the given ip address"""

    return (
        db.query(models.RemoteMachine)
        .filter(models.RemoteMachine.ip_address == ip_address)
        .first()
    )


def get_remote_machines(
    db: Session, skip: int = 0, limit: int = 100
) -> list[models.RemoteMachine]:
    # TODO: Add sorting logic so that the returned list is sorted in a predictable order
    """Returns a list of remote machines"""

    return db.query(models.RemoteMachine).offset(skip).limit(limit).all()


def create_remote_machine(
    db: Session, remote_machine: schemas.RemoteMachineCreate
) -> tuple[models.RemoteMachine, str]:
    # TODO ip_address can be used as a unique identifier (primary key)
    """Creates a new remote machine"""

    try:
        # only linux is supported for now
        if remote_machine.os_type != OsType.linux:
            err = f"Invalid os_type! (os_type: {remote_machine.os_type})"
            logging.error(err)
            return None, err

        if get_remote_machine_by_ip_address(db, remote_machine.ip_address) != None:
            err = f"Remote machine with the given ip address already exists! (ip_address: {remote_machine.ip_address})"
            logging.error(err)
            return None, err

        db_remote_machine = models.RemoteMachine(**remote_machine.dict())
        db.add(db_remote_machine)
        db.commit()
        db.refresh(db_remote_machine)
        return db_remote_machine

    except DBAPIError as e:
        err = f"An error occurred while creating remote machine: {e.orig.args}"
        logging.error(err)
        db.rollback()
        return None, err

    except SQLAlchemyError as e:
        err = f"An error occurred while creating remote machine: {e}"
        logging.error(err)
        db.rollback()
        return None, err

    except Exception as e:
        err = f"An unknown error occurred while creating remote machine: {e}"
        logging.error(err)
        db.rollback()
        return None, err
