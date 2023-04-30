import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.internal.sql import crud, models
from app.internal.sql.database import SesssionLocal, engine
from app.internal.utils.validator import validate_ip_address

router = APIRouter(
    prefix="/remote_hosts",
    tags=["remote_hosts"],
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
def get_remote_hosts(db: Session = Depends(get_db)) -> Any:
    hosts = crud.get_remote_hosts(db=db, skip=0, limit=100)
    if len(hosts) == 0:
        err = "No hosts found"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)
    return [
        {
            "ip_address": host.ip_address,
            "description": host.description,
            "contact_info": host.contact_info,
        }
        for host in hosts
    ]


@router.get("/{ip_address}")
def get_remote_host_by_ip_address(
    ip_address: Annotated[str, Query(max_length=40)], db: Session = Depends(get_db)
) -> Any:
    if validate_ip_address(ip_address) == False:
        err = f"Invalid IP address: {ip_address}"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    host = crud.get_remote_host_by_ip_address(db=db, ip_address=ip_address)
    if host == None:
        err = f"Host with IP address {ip_address} not found"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)
    return {
        "ip_address": host.ip_address,
        "description": host.description,
        "contact_info": host.contact_info,
    }


@router.get("/contact_info/{contact_info}")
def get_remote_hosts_by_contact_info(
    contact_info: Annotated[str, Query()], db: Session = Depends(get_db)
) -> Any:
    hosts = crud.get_remote_hosts_by_contact_info(db=db, contact_info=contact_info)
    if len(hosts) == 0:
        err = f"No hosts found with contact info {contact_info}"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)
    return [
        {
            "ip_address": host.ip_address,
            "description": host.description,
            "contact_info": host.contact_info,
        }
        for host in hosts
    ]
