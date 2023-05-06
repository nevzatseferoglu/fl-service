from pydantic import BaseModel

from .utils.enum import FlowerType, OsType, StatusType


class Status(BaseModel):
    """
    Pydantic Model: Status check.
    """

    status: StatusType
    description: str | None = None


class RemoteHostBase(BaseModel):
    """
    Pydantic Model: Remote host to connect to.
    """

    contact_info: str
    ip_address: str
    description: str | None = None


class RemoteHostCreate(RemoteHostBase):
    """
    Pydantic Model: Remote host to connect to.
    """

    fl_identifier: str
    flower_type: FlowerType
    ssh_username: str
    ssh_password: str = ""

    os_type: OsType = OsType.linux

    ssh_port: int = 22
    ssh_key: str | None = None
    ssh_key_passphrase: str | None = None


class RemoteHost(RemoteHostBase):
    """
    Pydantic Model: Remote host to connect to.
    """

    id: int

    class Config:
        orm_mode = True
