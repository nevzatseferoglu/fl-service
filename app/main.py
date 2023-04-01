from fastapi import FastAPI
from ansible_runner import run
from os import path
from tempfile import TemporaryDirectory

app = FastAPI()


@app.post("/run_playbook")
def run_playbook():
    prefix = "mkdir_ansible_test_"
    with TemporaryDirectory(prefix=prefix) as tempdir:
        playbook = path.abspath("app/ansible-resources/playbook.yml")
        inventory = path.abspath("app/ansible-resources/inventory.ini")

        runner = run(
            private_data_dir=tempdir, playbook=playbook, inventory=inventory
        )

        if runner.status == "failed":
            return {"status": "Playbook failed!"}
        elif runner.status == "successful":
            return {"status": "Playbook ran successfully!"}
