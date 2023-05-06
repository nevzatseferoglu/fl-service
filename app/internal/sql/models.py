from sqlalchemy import Column, Integer, String

from .database import Base


class RemoteHost(Base):
    """
    Model for remote hosts.
    """

    __tablename__ = "remote_hosts"

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
