from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.internal.schemas import RemoteMachine
from app.internal.sql import crud, models
from app.internal.sql.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(
    prefix="/remote_machines",
    tags=["remote_machines"],
)


@router("GET", "/", response_model=list[RemoteMachine])
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


@router("GET", "/{ip_address}", response_model=RemoteMachine)
def get_remote_machine(ip_address: str, db: Session = Depends(get_db)) -> Any:
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
