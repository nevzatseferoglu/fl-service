from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class RemoteHost(Base):
    """
    Model for remote hosts.
    """

    __tablename__ = "remote_host"

    id = Column(Integer, primary_key=True, index=True)
    flower_type = Column(String)
    ip_address = Column(String(45), unique=True, index=True)
    ssh_username = Column(String)
    ssh_password = Column(String)

    os_type = Column(String)

    ssh_port = Column(Integer)
    ssh_key = Column(String)
    ssh_key_passphrase = Column(String)
    description = Column(String)
    contact_info = Column(String)
    fl_identifier = Column(String, unique=True, index=True)
    docker_state = relationship("RemoteHostDockerState", back_populates="remote_host")
    host_pattern = Column(String)


class RemoteHostDockerState(Base):
    """
    Model for docker state of the remote host.
    """

    __tablename__ = "remote_host_docker_states"

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(Integer, ForeignKey("remote_hosts.id"))
    host = relationship("RemoteHost", back_populates="docker_state")

    # each task completion state
    state_install_aptitude = Column(String)
    state_install_required_system_packages = Column(String)
    state_add_docker_gpg_apt_key = Column(String)
    state_add_docker_repository = Column(String)
    state_update_apt_and_install_docker_ce = Column(String)
    state_install_docker_module_for_python = Column(String)
    general_state = Column(Boolean)
