
from enum import Enum
from ipaddress import IPv4Address
from typing import Optional
from pydantic import BaseModel, validator


class OS(str, Enum):
    Linux = 'linux'
    Windows = 'windows'
    Macos = 'macos'


class IPAddress(BaseModel):
    address: str
    
    @validator('address')
    def validate_address(cls, value):
        try:
            ip_address = IPv4Address(value)
        except ValueError as e:
            raise ValueError('Invalid IP address') from e
        return str(ip_address)


class RemoteMachine(BaseModel):
    hostname: str
    ip_address: IPAddress
    ssh_port: Optional[int] = 22
    ssh_username: str
    ssh_password: Optional[str] = None
    ssh_key: Optional[str] = None
    ssh_key_passphrase: Optional[str] = None
    os: OS
    descriotion: Optional[str] = None
