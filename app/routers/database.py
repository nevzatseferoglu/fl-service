import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.internal.sql import crud, models
from app.internal.sql.database import SesssionLocal, engine
from app.internal.utils.validator import validate_ip_address

router = APIRouter(
    prefix="/remote_machines",
    tags=["remote_machines"],
)

models.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SesssionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_remote_machines(db: Session = Depends(get_db)) -> Any:
    machines = crud.get_remote_machines(db=db, skip=0, limit=100)
    if len(machines) == 0:
        err = "No machines found"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)
    return [
        {
            "ip_address": machine.ip_address,
            "description": machine.description,
            "contact_info": machine.contact_info,
        }
        for machine in machines
    ]


@router.get("/{ip_address}")
def get_remote_machine_by_ip_address(
    ip_address: Annotated[str, Query(max_length=40)], db: Session = Depends(get_db)
) -> Any:
    if validate_ip_address(ip_address) == False:
        err = f"Invalid IP address: {ip_address}"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    machine = crud.get_remote_machine_by_ip_address(db=db, ip_address=ip_address)
    if machine == None:
        err = f"Machine with IP address {ip_address} not found"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)
    return {
        "ip_address": machine.ip_address,
        "description": machine.description,
        "contact_info": machine.contact_info,
    }


@router.get("/contact_info/{contact_info}")
def get_remote_machines_by_contact_info(
    contact_info: Annotated[str, Query()], db: Session = Depends(get_db)
) -> Any:
    machines = crud.get_remote_machines_by_contact_info(
        db=db, contact_info=contact_info
    )
    if len(machines) == 0:
        err = f"No machines found with contact info {contact_info}"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)
    return [
        {
            "ip_address": machine.ip_address,
            "description": machine.description,
            "contact_info": machine.contact_info,
        }
        for machine in machines
    ]
