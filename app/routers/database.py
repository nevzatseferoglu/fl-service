import logging
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.internal.schemas import RemoteMachineCreate
from app.internal.sql import crud, models
from app.internal.sql.database import SesssionLocal, engine

models.Base.metadata.create_all(bind=engine)

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
    if machines == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No machines found"
        )
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
    ip_address: str, db: Session = Depends(get_db)
) -> Any:
    machine = crud.get_remote_machine_by_ip_address(db=db, ip_address=ip_address)
    if machine == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Machine not found"
        )
    return {
        "ip_address": machine.ip_address,
        "description": machine.description,
        "contact_info": machine.contact_info,
    }


@router.post("/register_remote_machine")
def create_remote_machine(
    machine: Annotated[RemoteMachineCreate, Body()], db: Session = Depends(get_db)
) -> Any:
    machine, err = crud.register_remote_machine(db=db, machine=machine)
    if machine == None:
        logging.error(err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Machine cannot be added",
        )
    return {
        "ip_address": machine.ip_address,
        "description": machine.description,
        "contact_info": machine.contanct_info,
    }
