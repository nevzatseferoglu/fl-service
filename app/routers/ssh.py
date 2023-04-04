
from typing import Any
from os import path, makedirs
import subprocess
from pathlib import Path
import logging

from fastapi import APIRouter

from app.internal.utils.ssh import command_exists
from app.internal.schemas.schema import StatusCheck
from app.internal.utils.exceptions import GenerateSSHKeyPairException, CopySSHKeyToRemoteException

router = APIRouter(
    prefix="/ssh",
    tags=["ssh"],
)

@router.post("/generate_ssh_key_pair")
def generate_ssh_key_pair() -> Any:
    """Generates an SSH key pair if one does not already exist."""

    ssh_key_path = path.expanduser("~/.ssh/id_rsa.pub")
    if Path(ssh_key_path).is_file():
        logging.error("SSH key already exists!")
        raise GenerateSSHKeyPairException(name="SSH key already exists!")

    ssh_path = path.expanduser("~/.ssh")
    if not Path(ssh_path).is_dir():
        makedirs("~/.ssh", mode=700, exist_ok=True)

    if not command_exists("ssh-keygen"):
        logging.error("ssh-keygen command not found!")
        raise GenerateSSHKeyPairException(name="ssh-keygen command not found!")

    result = subprocess.run(
        ["ssh-keygen", "-t", "rsa", "-b", "4096", "-N", "", "-q", "-f", ssh_key_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        logging.error("SSH key generation failed!")
        raise GenerateSSHKeyPairException(name="SSH key generation failed!")

    return StatusCheck(status="SSH key generated successfully!")


@router.post("/copy_ssh_key_to_remote")
def copy_ssh_key_to_remote() -> Any:
    # TODO: Implement with https://github.com/paramiko/paramiko
    """Copies the SSH key to the remote host."""

    ssh_key_path = path.expanduser("~/.ssh/id_rsa.pub")
    if not Path(ssh_key_path).is_file():
        logging.error("SSH key does not exist!")
        raise CopySSHKeyToRemoteException(name="SSH key does not exist!")
    
    if not command_exists("ssh-copy-id"):
        logging.error("ssh-keygen command not found!")
        raise CopySSHKeyToRemoteException(name="ssh-copy-id command not found!")
    