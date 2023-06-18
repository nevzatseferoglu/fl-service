import logging
import os
import subprocess
from typing import Annotated, Any

import paramiko
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ansible.inventory import dynamic_inventory
from app.internal.schema import RemoteHostCreate, Status, StatusType
from app.internal.sql import crud
from app.internal.utils.enum import OsType
from app.internal.utils.ssh import validate_command
from app.internal.utils.validator import validate_ip_address
from app.routers.database import get_db

router = APIRouter(
    prefix="/ssh",
    tags=["ssh"],
)

DEFAULT_SSH_PRIVATE_KEY_PATH = os.path.expanduser("~/.ssh/id_rsa")
DEFAULT_SSH_PUBLIC_KEY_PATH = os.path.expanduser("~/.ssh/id_rsa.pub")
DEFAULT_SSH_PATH = os.path.expanduser("~/.ssh")

# NOTE:
# - All endpoints validates ip address (syntax only) before doing any operation, if needed.
# - All endpoints validates given host is in the inventory before doing any operation, if needed.


@router.post("/generate-ssh-key-pair", response_model=Status)
def generate_ssh_key_pair() -> Any:
    """
    Generate SSH key pair for the API running environment.
    """

    if os.path.exists(DEFAULT_SSH_PRIVATE_KEY_PATH):
        err = "SSH key already exists!"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err)

    if not os.path.exists(DEFAULT_SSH_PATH):
        os.makedirs(DEFAULT_SSH_PATH, exist_ok=True)

    if not validate_command("ssh-keygen"):
        err = "ssh-keygen command not found!"
        logging.error(err)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=err,
        )

    result = subprocess.run(
        [
            "ssh-keygen",
            "-t",
            "rsa",
            "-b",
            "4096",
            "-N",
            "",
            "-q",
            "-f",
            DEFAULT_SSH_PRIVATE_KEY_PATH,
            "-y",
        ],
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        err = f"SSH key generation failed: {result.stderr}"
        logging.error(err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err,
        )

    logging.info("SSH key generated successfully!")
    return Status(
        status=StatusType.success, description="SSH key generated successfully!"
    )


@router.post("/copy-ssh-key-to-remote-host", response_model=Status)
def copy_ssh_key_to_remote(
    host: Annotated[RemoteHostCreate, Body()], db: Session = Depends(get_db)
) -> Any:
    """
    Copies the SSH key to the remote host.

    host: Remote host information.
    """

    if not validate_ip_address(host.ip_address):
        err = f"Invalid IP address: {host.ip_address}"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    # only linux is supported for now
    if host.os_type != OsType.linux:
        err = f"Invalid os_type! (os_type: {host.os_type})"
        logging.error(err)
        raise HTTPException(
            status_code=400,
            detail=err,
        )

    if host.fl_identifier.isspace():
        err = "Invalid flower identifier, it cannot contain whitespace characters."
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    if host.host_pattern != None and host.host_pattern.isspace():
        err = "Invalid host pattern, it cannot contain whitespace characters."
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    if not os.path.exists(DEFAULT_SSH_PUBLIC_KEY_PATH):
        err = "SSH public key does not exist!"
        logging.error(err)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=err,
        )

    client = paramiko.SSHClient()

    try:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=host.ip_address,
            username=host.ssh_username,
            password=host.ssh_password,
            port=host.ssh_port,
        )

        _, _, _ = client.exec_command("mkdir -p ~/.ssh")
        _, _, _ = client.exec_command("touch ~/.ssh/authorized_keys")

        with open(DEFAULT_SSH_PUBLIC_KEY_PATH, "r") as f:
            content = f.read()

        cmd = f'grep -q "{content}" ~/.ssh/authorized_keys || echo "{content}" >> ~/.ssh/authorized_keys'
        logging.info(f"{host.ip_address}: {cmd}")

        _, _, stderr = client.exec_command(cmd)

        stderr_output = stderr.read().decode("utf-8")
        if stderr_output:
            err = f"SSH key copy failed: {stderr_output}"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=err,
            )

        crud.register_remote_host(db=db, remote_host=host)
        dynamic_inventory.add_new_host_to_flower_inventory(
            inventory_dirname=host.fl_identifier,
            host_pattern=host.host_pattern,
            ansible_host=host.ip_address,
            ansible_user=host.ssh_username,
            flower_type=host.flower_type,
            db=db,
        )

        logging.info("SSH key copied to remote host successfully!")
        return Status(
            status=StatusType.success,
            description="SSH key copied to remote host successfully!",
        )

    except paramiko.BadHostKeyException as e:
        err = f"Host key could not be verified: \n{e}"
        logging.error(err)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=err,
        )

    except paramiko.AuthenticationException as e:
        err = f"Authentication failed: \n{e}"
        logging.error(err)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=err,
        )

    except paramiko.SSHException as e:
        err = f"SSH connection failed: \n{e}"
        logging.error(err)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=err,
        )

    except HTTPException as e:
        logging.error(e.detail)
        # intentionally to avoid double logging
        raise e

    except Exception as e:
        err = f"Unknown error: \n{e}"
        logging.error(err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err,
        )

    finally:
        client.close()
