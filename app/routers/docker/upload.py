import logging
import os
import shutil
import subprocess
import zipfile
from typing import Annotated

import ansible_runner
import yaml
from fastapi import (APIRouter, Depends, File, HTTPException, Path, UploadFile,
                     status)
from sqlalchemy.orm import Session

from app.routers.docker.docker import router

from ...definitions import ANSIBLE_INVENTORY_DIR
from ...internal.schema import Status
from ...internal.sql import crud
from ...internal.utils.enum import StatusType
from ...internal.utils.validator import validate_ip_address
from ...routers.database import get_db

# Have in mind that this means that the whole contents will be stored in memory.
# This will work well for small files.

# take ip address
# source files which will be deployed
# whether given is a zip or not
# entrypointCmd of the image
# data source directory as an absolute path (which will be deployed)
# platform information (pytorch, terserflow)

router = APIRouter(
    prefix="/docker",
    tags=["docker"],
)


# Assumes that there is a definition.yaml in the given zip file which includes
# entrypoint command string and datadir in it.
# entrypoint will be used in the dockerfile but the datadir will be mount in the ansible docker playbook.


def generate_deployment_ansible_playbook(
    dest: str, image: str, sourcedir: str, targetdir: str
):
    content = f"""- name: Deploy given docker image
  hosts: all
  become: yes

  tasks:
  - name: 
    community.docker.docker_container:
      name: linuxfederated
      image: {image}
      network_mode: host
      mounts:
        - type: "bind"
          read_only: true
          source: {sourcedir}
          target: {targetdir}
    async: 600
    poll: 5
"""
    logging.info(f"Creating ansible playbook in {sourcedir}...")
    try:
        with open(os.path.join(dest, "deployment.yaml"), "w") as file:
            file.write(content)
    except (IOError, OSError) as e:
        err = f"Failed to create ansible playbook in {dest}, {e}"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)


def generate_dockerfile_pytorch(entrypoint: str, sourcedir: str):
    content = f"""#syntax=docker/dockerfile:1
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

RUN apt-get update \
    && apt install iputils-ping -y \
    && apt install telnet -y

WORKDIR /app

# Scripts needed for Flower client
ADD . .

# update pip
RUN pip3 install --upgrade pip

# install dependencies
RUN if [ -e requirements.txt ]; then pip install -r requirements.txt; \
    else pip install flwr>=1.0.0; fi

ENTRYPOINT {entrypoint}"""

    logging.info(f"Creating dockerfile in {sourcedir}...")
    try:
        with open(os.path.join(sourcedir, "dockerfile"), "w") as file:
            file.write(content)
    except (IOError, OSError) as e:
        err = f"Failed to create dockerfile, {e}"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)


@router.post("/upload-source-files/{ip_address}/{platform}/{arch}/")
async def create_upload_file(
    ip_address: Annotated[str, Path()],
    platform: Annotated[str, Path()],
    arch: Annotated[str, Path()],
    file: UploadFile = File(description="Zip file which includes project source code"),
    db: Session = Depends(get_db),
):
    logging.info(f"Validating ip address {ip_address}...")
    if not validate_ip_address(ip_address):
        err = f"IP address {ip_address} is not valid"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    logging.info(
        f"Checking if remote host with ip address {ip_address} exists in database..."
    )

    host = crud.get_remote_host_by_ip_address(db=db, ip_address=ip_address)
    if host == None:
        err = f"Remote host with ip address {ip_address} not found in database"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)

    upload_dir = os.path.join(ANSIBLE_INVENTORY_DIR, host.fl_identifier, "source")
    # Create the upload directory if it doesn't exist
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # destination of the new zip file in the server filesystem
    zipsource = os.path.join(upload_dir, file.filename)
    with open(zipsource, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # extract the zip to the regarding host directory
    with zipfile.ZipFile(zipsource, "r") as zip_ref:
        zip_ref.extractall(upload_dir)

    os.remove(os.path.join(upload_dir, file.filename))

    defyaml = os.path.join(upload_dir, "definition.yaml")
    image_name = ""
    sourcedir = ""
    targetdir = ""
    try:
        with open(defyaml, "r") as yaml_file:
            content = yaml.safe_load(yaml_file)
            cmds = [f'"{i}"' for i in content["entrypoint"]]
            cmdstr = ""
            for i, cmd in enumerate(cmds):
                if i == 0:
                    cmdstr += f"[{cmd}, "
                elif i == len(cmds) - 1:
                    cmdstr += f"{cmd}]"
                else:
                    cmdstr += f"{cmd}, "

            generate_dockerfile_pytorch(cmdstr, upload_dir)
            image_name = content["image_name"]
            sourcedir = content["sourcedir"]
            targetdir = content["targetdir"]
            logging.info(f"Successfully created dockerfile in {upload_dir}")

    except (yaml.YAMLError, OSError) as e:
        err = f"Failed to read {defyaml} as a yaml file, {e}"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)

    logging.info("Starting to build an image in server host")

    match arch:
        case "amd64":
            command = [
                "docker",
                "buildx",
                "build",
                "--load",
                "--platform",
                "linux/amd64",
                "--tag",
                image_name,
                ".",
            ]
            p = subprocess.Popen(command, cwd=upload_dir)
            p.wait()
        case "arm64":
            command = [
                "docker",
                "buildx",
                "build",
                "--load",
                "--platform",
                "linux/arm64",
                "--tag",
                image_name,
                ".",
            ]
            p = subprocess.Popen(command, cwd=upload_dir)
            p.wait()

    logging.info("Docker image is successfully built in server host")

    generate_deployment_ansible_playbook(upload_dir, image_name, sourcedir, targetdir)


@router.post("/deploy/{ip_address}/")
async def deploy(ip_address: Annotated[str, Path()], db: Session = Depends(get_db)):
    logging.info(f"Validating ip address {ip_address}...")
    if not validate_ip_address(ip_address):
        err = f"IP address {ip_address} is not valid"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    logging.info(
        f"Checking if remote host with ip address {ip_address} exists in database..."
    )

    host = crud.get_remote_host_by_ip_address(db=db, ip_address=ip_address)
    if host == None:
        err = f"Remote host with ip address {ip_address} not found in database"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)

    dplfile = os.path.join(
        ANSIBLE_INVENTORY_DIR, host.fl_identifier, "source", "deployment.yaml"
    )
    # Create the upload directory if it doesn't exist
    if not os.path.exists(dplfile):
        err = f"Deployment file {dplfile} not found"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)

    inventory_path = os.path.join(ANSIBLE_INVENTORY_DIR, str(host.fl_identifier))
    if not os.path.exists(inventory_path):
        err = f"Inventory directory for remote host with ip address {ip_address} not found"
        logging.error(err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)

    tmp_path = os.path.join(inventory_path, "tmp")
    if os.path.exists(tmp_path):
        shutil.rmtree(tmp_path)
    os.makedirs(os.path.join(inventory_path, "tmp"), exist_ok=True)

    runner_config = {
        "private_data_dir": os.path.join(inventory_path, "tmp"),
        "inventory": os.path.join(inventory_path, f"{host.fl_identifier}.yaml"),
        "playbook": dplfile,
        "verbosity": 4,
        "limit": str(host.host_pattern),
    }

    runner = ansible_runner.run(**runner_config)
    if runner.status == "successful":
        return Status(
            status=StatusType.success, description="Ansible playbook run successfully"
        )
    else:
        err = "Ansible docker installation playbook failed!"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )
