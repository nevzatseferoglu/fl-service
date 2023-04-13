from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .database import Base

# ssh_port: int | None = 22
# ssh_username: str
# ssh_password: str | None = None
# ssh_key: str | None = None
# ssh_key_passphrase: str | None = None
# description: str | None = None


class OSModel(Base):
    __tablename__ = "oses"

    id = Column(Integer, primary_key=True, index=True)
    type_os = Column(String)
    name = Column(String)
    arch = Column(String)
    version = Column(String)
    description = Column(String)

    machines = relationship("RemoteMachineModel", back_populates="os_type")


class RemoteMachineModel(Base):
    __tablename__ = "remote_machines"

    id = Column(Integer, primary_key=True, index=True)
    os_type = relationship("OS", back_populates="owner")
    ip_address = Column(String, unique=True, index=True)
    ssh_port = Column(Integer)
    ssh_username = Column(String)
    ssh_password = Column(String)
    ssh_key = Column(String)
    ssh_key_passphrase = Column(String)
    description = Column(String)
