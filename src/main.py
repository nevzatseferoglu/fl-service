import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import ansible_runner

app = FastAPI()

class StatusCheck(BaseModel):
    status: str
    timestamp: str

@app.post("/run_playbook")
async def run_playbook():
    # Define the path to the private data directory
    private_data_dir = "/tmp/private"

    # Define the path to the playbook file
    playbook_path = os.path.abspath("src/ansible-resources/test.yml")

    # Create a Runner object with the private data directory and playbook path
    runner = ansible_runner.run(
        private_data_dir=private_data_dir,
        playbook=playbook_path,
    )

    if runner.rc != 0:
        raise HTTPException(status_code=400, detail="Playbook failed!")
    else:
        return {"status": "Success", "message": "Playbook ran successfully"}


@app.post("/check_status")
async def check_status(status_check: StatusCheck):
    if status_check.status != "OK":
        raise HTTPException(status_code=400, detail="Status check failed")
    return {"status": "Success", "message": f"Received status check at {status_check.timestamp}"}

