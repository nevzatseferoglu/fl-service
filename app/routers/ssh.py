import logging
import subprocess
from os import makedirs, path
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Body

from app.internal.exceptions import (CopySSHKeyToRemoteException,
                                     GenerateSSHKeyPairException)
from app.internal.schemas.schema import RemoteMachine, StatusCheck
from app.internal.utils.ssh import command_exists

router = APIRouter(
    prefix="/ssh",
    tags=["ssh"],
)

remote_machines: list[RemoteMachine] = []

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


@router.post("/copy_ssh_key_to_remote_machine")
def copy_ssh_key_to_remote(machine: Annotated[RemoteMachine, Body()]) -> Any:
    # TODO: Use subprocess.run() with input parameter to pass the password
    """Copies the SSH key to the remote host."""

    ssh_key_path = path.expanduser("~/.ssh/id_rsa.pub")
    if not Path(ssh_key_path).is_file():
        logging.error("SSH key does not exist!")
        raise CopySSHKeyToRemoteException(name="SSH key does not exist!")

    if not command_exists("ssh-copy-id"):
        logging.error("ssh-keygen command not found!")
        raise CopySSHKeyToRemoteException(name="ssh-copy-id command not found!")

    cmd = f"ssh-copy-id {machine.ssh_username}@{machine.ip_address}"
    subprocess.run(cmd, input=machine.ssh_password, shell=True)

    