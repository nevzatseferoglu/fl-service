from pydantic import BaseModel, IPvAnyAddress

from ..utils.enums import Architecture, OsType, StatusType


class Status(BaseModel):
    """Status check"""

    status: StatusType
    description: str | None = None


class RemoteMachineBase(BaseModel):
    """Remote machine to connect to"""

    contanct_info: int
    description: str | None = None


class RemoteMachineCreate(RemoteMachineBase):
    """Remote machine to connect to"""

    os_type: OsType
    ip_address: IPvAnyAddress
    ssh_username: str
    ssh_password: str | None = ""
    ssh_port: int | None = 22
    ssh_key: str | None = None
    ssh_key_passphrase: str | None = None


class RemoteMachine(RemoteMachineCreate):
    """Remote machine to connect to"""

    id: int

    class Config:
        orm_mode = True


class OSBase(BaseModel):
    """Operating system"""

    os_type: OsType


class OSCreate(OSBase):
    """Operating system"""

    name: str | None = None
    arch: Architecture | None = None
    version: str | None = None
    description: str | None = None


class OS(OSCreate):
    """Operating system"""

    machines: list[RemoteMachine] = []

    class Config:
        orm_mode = True
