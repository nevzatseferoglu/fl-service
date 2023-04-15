import logging
import subprocess
from os import makedirs, path
from pathlib import Path
from typing import Annotated, Any

import paramiko
from fastapi import APIRouter, Body, status

from app.internal.exceptions import (CopySSHKeyToRemoteException,
                                     GenerateSSHKeyPairException)
from app.internal.schemas import RemoteMachine, Status, StatusType
from app.internal.utils.ssh import command_exists

router = APIRouter(
    prefix="/ssh",
    tags=["ssh"],
)

remote_machines: list[RemoteMachine] = []


@router.post("/generate_ssh_key_pair", response_model=Status)
def generate_ssh_key_pair() -> Any:
    """Generates an SSH key pair if one does not already exist."""

    ssh_key_path = path.expanduser("~/.ssh/id_rsa")
    if Path(ssh_key_path).is_file():
        logging.error("SSH key already exists!")
        raise GenerateSSHKeyPairException(
            detail="SSH key already exists!", status_code=status.HTTP_400_BAD_REQUEST
        )

    ssh_path = path.expanduser("~/.ssh")
    if not Path(ssh_path).is_dir():
        makedirs("~/.ssh", mode=700, exist_ok=True)

    if not command_exists("ssh-keygen"):
        logging.error("ssh-keygen command not found!")
        raise GenerateSSHKeyPairException(
            detail="ssh-keygen command not found!",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    result = subprocess.run(
        ["ssh-keygen", "-t", "rsa", "-b", "4096", "-N", "", "-q", "-f", ssh_key_path],
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        logging.error(f"SSH key generation failed: \n{result.stderr}")
        raise GenerateSSHKeyPairException(
            detail=f"SSH key generation failed: \n{result.stderr}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    logging.info("SSH key generated successfully!")
    return Status(
        status=StatusType.success, description="SSH key generated successfully!"
    )


@router.post("/copy_ssh_key_to_remote_machine", response_model=Status)
def copy_ssh_key_to_remote(machine: Annotated[RemoteMachine, Body()]) -> Any:
    # TODO: Convert into async function for the improving performance
    """Copies the SSH key to the remote host."""

    ssh_pub_key_path = path.expanduser("~/.ssh/id_rsa.pub")
    if not Path(ssh_pub_key_path).is_file():
        logging.error("SSH public key does not exist!")
        raise CopySSHKeyToRemoteException(
            detail="SSH public key does not exist!",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=str(machine.ip_address),
            username=machine.ssh_username,
            password=machine.ssh_password,
        )

        _, _, _ = client.exec_command("mkdir -p ~/.ssh")
        _, _, _ = client.exec_command("touch ~/.ssh/authorized_keys")

        with open(ssh_pub_key_path, "r") as f:
            content = f.read()

        _, _, _ = client.exec_command(
            f'grep -q "{content}" ~/.ssh/authorized_keys || echo "{content}" >> ~/.ssh/authorized_keys'
        )
        client.close()

    except paramiko.BadHostKeyException as e:
        logging.error(f"Host key could not be verified: \n{e}")
        client.close()
        raise CopySSHKeyToRemoteException(
            detail=f"Host key could not be verified: \n{e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except paramiko.AuthenticationException as e:
        logging.error(f"Authentication failed: \n{e}")
        client.close()
        raise CopySSHKeyToRemoteException(
            detail=f"Authentication failed: \n{e}",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    except paramiko.SSHException as e:
        logging.error(f"Error connecting to remote machine: \n{e}")
        client.close()
        raise CopySSHKeyToRemoteException(
            detail=f"Error connecting to remote machine: \n{e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        logging.error(f"Unknown error: \n{e}")
        client.close()
        raise CopySSHKeyToRemoteException(
            detail=f"Unknown error: \n{e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    logging.info("SSH key copied to remote machine successfully!")
    return Status(
        status=StatusType.success,
        description="SSH key copied to remote machine successfully!",
    )
