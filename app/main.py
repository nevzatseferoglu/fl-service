from os import path, makedirs
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
import logging

from app.utils.ssh import command_exists

from fastapi import FastAPI, HTTPException

from ansible_runner import run


logging.basicConfig(
    filename="uvicorn.log",
    filemode="a",
    format="%(asctime)s:%(levelname)s:%(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG,
)

logging.info("Starting a fresh uvicorn!")

app = FastAPI(debug=True)


@app.post("/generate_ssh_key_pair")
def generate_ssh_key_pair():
    """Generates an SSH key pair if one does not already exist."""

    ssh_key_path = path.expanduser("~/.ssh/id_rsa.pub")
    if Path(ssh_key_path).is_file():
        logging.error("SSH key already exists!")
        return HTTPException(status_code=400, detail="SSH key already exists!")

    ssh_path = path.expanduser("~/.ssh")
    if not Path(ssh_path).is_dir():
        makedirs("~/.ssh", mode=700, exist_ok=True)

    if not command_exists("ssh-keygen"):
        logging.error("ssh-keygen command not found!")
        return HTTPException(status_code=400, detail="ssh-keygen command not found!")

    result = subprocess.run(
        ["ssh-keygen", "-t", "rsa", "-b", "4096", "-N", "", "-q", "-f", ssh_key_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        logging.error("SSH key generation failed!")
        return HTTPException(status_code=400, detail="SSH key generation failed!")

    return {"status": "SSH key generated successfully!"}


@app.post("/run_playbook")
def run_playbook():
    prefix = "mkdir_ansible_test_"
    with TemporaryDirectory(prefix=prefix) as tempdir:
        playbook = path.abspath("app/ansible-resources/playbook.yml")
        inventory = path.abspath("app/ansible-resources/inventory.ini")

        runner = run(private_data_dir=tempdir, playbook=playbook, inventory=inventory)

        if runner.status == "failed":
            return {"status": "Playbook failed!"}
        elif runner.status == "successful":
            return {"status": "Playbook ran successfully!"}
