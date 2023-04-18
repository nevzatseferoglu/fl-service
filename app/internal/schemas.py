from pydantic import BaseModel, IPvAnyAddress

from .utils.enums import OsType, StatusType


class Status(BaseModel):
    """Status check"""

    status: StatusType
    description: str | None = None


class RemoteMachineBase(BaseModel):
    """Remote machine to connect to"""

    contact_info: str
    ip_address: IPvAnyAddress
    description: str | None = None


class RemoteMachineCreate(RemoteMachineBase):
    """Remote machine to connect to"""

    ssh_username: str
    ssh_password: str | None = ""

    # TODO: Ensure that given os_type is valid
    os_type: OsType = OsType.linux

    ssh_port: int | None = 22
    ssh_key: str | None = None
    ssh_key_passphrase: str | None = None


class RemoteMachine(RemoteMachineBase):
    """Remote machine to connect to"""

    id: int

    class Config:
        orm_mode = True
