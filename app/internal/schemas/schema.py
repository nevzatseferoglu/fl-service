
from enum import Enum
from pydantic import BaseModel, IPvAnyAddress

class StatusCheck(BaseModel):
    '''Status check'''

    status: str

class Architecture(str, Enum):
    '''Architecture type'''

    x86 = "x86"
    x64 = "x64"
    arm = "arm"
    arm64 = "arm64"

class OsType(str, Enum):
    '''Operating system type'''
    
    linux = "linux"
    windows = "windows"
    macos = "macos"
    raspberry_pi = "raspberry_pi"
    android = "android"
    ios = "ios"
    freebsd = "freebsd"
    netbsd = "netbsd"
    openbsd = "openbsd"

class OS(BaseModel):
    '''Operating system'''

    type_os: OsType
    name: str | None = None
    arch: Architecture | None = None
    version: str | None = None
    description: str | None = None


class RemoteMachine(BaseModel):
    '''Remote machine to connect to'''

    os: OS
    ip_address: IPvAnyAddress
    ssh_port: int | None = 22
    ssh_username: str
    ssh_password: str | None = None
    ssh_key: str | None = None
    ssh_key_passphrase: str | None = None
    descriotion: str | None = None
