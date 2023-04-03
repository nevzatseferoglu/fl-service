
from os import path, makedirs
import subprocess
from pathlib import Path
import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from core.utils.ssh import command_exists
from core.schemas.schema import StatusCheck
from core.utils.exceptions import GenerateSSHKeyPairException, CopySSHKeyToRemoteException


logging.basicConfig(
    filename="uvicorn.log",
    filemode="a",
    format="%(asctime)s:%(levelname)s:%(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG,
)

logging.info("Starting a fresh uvicorn!")

app = FastAPI(debug=True)

@app.exception_handler(GenerateSSHKeyPairException)
async def generate_ssh_key_pair_failed_exception_handler(
    request: Request,
    exc: GenerateSSHKeyPairException):
    
    logging.error(f"Machine Info: {request.client}") 
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": f"GenerateSSHKeyPairException: {exc.name}"
        }
    )

@app.post("/generate_ssh_key_pair")
def generate_ssh_key_pair():
    """Generates an SSH key pair if one does not already exist."""

    ssh_key_path = path.expanduser("~/.ssh/id_rsa.pub")
    if Path(ssh_key_path).is_file():
        logging.error("SSH key already exists!")
        # raise HTTPException(status_code=400, detail="SSH key already exists!")
        raise GenerateSSHKeyPairException(name="SSH key already exists!")

    ssh_path = path.expanduser("~/.ssh")
    if not Path(ssh_path).is_dir():
        makedirs("~/.ssh", mode=700, exist_ok=True)

    if not command_exists("ssh-keygen"):
        logging.error("ssh-keygen command not found!")
        # raise HTTPException(status_code=400, detail="ssh-keygen command not found!")
        raise GenerateSSHKeyPairException(name="ssh-keygen command not found!")

    result = subprocess.run(
        ["ssh-keygen", "-t", "rsa", "-b", "4096", "-N", "", "-q", "-f", ssh_key_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        logging.error("SSH key generation failed!")
        # raise HTTPException(status_code=400, detail="SSH key generation failed!")
        raise GenerateSSHKeyPairException(name="SSH key generation failed!")

    return StatusCheck(status="SSH key generated successfully!")


@app.post("/copy_ssh_key_to_remote")
def copy_ssh_key_to_remote():
    """Copies the SSH key to the remote host."""

    ssh_key_path = path.expanduser("~/.ssh/id_rsa.pub")
    if not Path(ssh_key_path).is_file():
        logging.error("SSH key does not exist!")
        raise CopySSHKeyToRemoteException(name="SSH key does not exist!")
    
    if not command_exists("ssh-copy-id"):
        logging.error("ssh-keygen command not found!")
        raise CopySSHKeyToRemoteException(name="ssh-copy-id command not found!")
    








