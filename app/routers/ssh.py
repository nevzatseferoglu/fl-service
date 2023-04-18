import logging
import subprocess
from os import makedirs, path
from pathlib import Path
from typing import Annotated, Any

import paramiko
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.internal.schemas import RemoteMachineCreate, Status, StatusType
from app.internal.sql import crud
from app.internal.utils.ssh import command_exists
from app.routers.database import get_db

router = APIRouter(
    prefix="/ssh",
    tags=["ssh"],
)


@router.post("/generate_ssh_key_pair", response_model=Status)
def generate_ssh_key_pair() -> Any:
    """Generates an SSH key pair if one does not already exist."""

    ssh_key_path = path.expanduser("~/.ssh/id_rsa")
    if Path(ssh_key_path).is_file():
        err = "SSH key already exists!"
        logging.error(err)
        raise HTTPException(detail=err, status_code=status.HTTP_400_BAD_REQUEST)

    ssh_path = path.expanduser("~/.ssh")
    if not Path(ssh_path).is_dir():
        makedirs("~/.ssh", mode=700, exist_ok=True)

    if not command_exists("ssh-keygen"):
        err = "ssh-keygen command not found!"
        logging.error(err)
        raise HTTPException(
            detail=err,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    result = subprocess.run(
        ["ssh-keygen", "-t", "rsa", "-b", "4096", "-N", "", "-q", "-f", ssh_key_path],
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        err = f"SSH key generation failed: \n{result.stderr}"
        logging.error(err)
        raise HTTPException(
            detail=err,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    logging.info("SSH key generated successfully!")
    return Status(
        status=StatusType.success, description="SSH key generated successfully!"
    )


@router.post("/copy_ssh_key_to_remote_machine", response_model=Status)
def copy_ssh_key_to_remote(
    machine: Annotated[RemoteMachineCreate, Body()], db: Session = Depends(get_db)
) -> Any:
    # TODO: Convert into async function for the improving performance
    """Copies the SSH key to the remote host."""

    ssh_pub_key_path = path.expanduser("~/.ssh/id_rsa.pub")
    if not Path(ssh_pub_key_path).is_file():
        err = "SSH public key does not exist!"
        logging.error(err)
        raise HTTPException(
            detail=err,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    client = paramiko.SSHClient()

    try:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=str(machine.ip_address),
            username=machine.ssh_username,
            password=machine.ssh_password,
            port=machine.ssh_port,
        )

        _, _, _ = client.exec_command("mkdir -p ~/.ssh")
        _, _, _ = client.exec_command("touch ~/.ssh/authorized_keys")

        with open(ssh_pub_key_path, "r") as f:
            content = f.read()

        _, _, _ = client.exec_command(
            f'grep -q "{content}" ~/.ssh/authorized_keys || echo "{content}" >> ~/.ssh/authorized_keys'
        )

        if crud.register_remote_machine(db=db, remote_machine=machine) == None:
            err = "Given machine cannot be registered"
            logging.error(err)
            raise HTTPException(
                detail=err,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        logging.info("SSH key copied to remote machine successfully!")
        return Status(
            status=StatusType.success,
            description="SSH key copied to remote machine successfully!",
        )

    except paramiko.BadHostKeyException as e:
        err = f"Host key could not be verified: \n{e}"
        logging.error(err)
        raise HTTPException(
            detail=err,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    except paramiko.AuthenticationException as e:
        err = f"Authentication failed: \n{e}"
        logging.error(err)
        raise HTTPException(
            detail=err,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    except paramiko.SSHException as e:
        err = f"SSH connection failed: \n{e}"
        logging.error(err)
        raise HTTPException(
            detail=err,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    except HTTPException as e:
        # intentionally to avoid double logging
        raise e

    except Exception as e:
        err = f"Unknown error: \n{e}"
        logging.error(err)
        raise HTTPException(
            detail=err,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    finally:
        client.close()
