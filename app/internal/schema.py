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
    host_pattern: str | None


class RemoteHost(RemoteHostBase):
    """
    Pydantic Model: Remote host to connect to.
    """

    id: int

    class Config:
        orm_mode = True


class RemoteHostDockerState(BaseModel):
    host_id: str
    state_install_aptitude: str
    state_install_required_system_packages: str
    state_add_docker_gpg_apt_key: str
    state_add_docker_repository: str
    state_update_apt_and_install_docker_ce: str
    state_install_docker_module_for_python: str
    state_check_docker_command: str

    class Config:
        orm_mode = True
