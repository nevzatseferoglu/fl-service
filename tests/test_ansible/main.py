import os
from time import sleep

import ansible_runner

DEFAULT_VERBOSITY = 0
INVENTORY_DIRECTORY = f"{os.path.dirname(__file__)}/inventory.yaml"
PLAYBOOK_DIRECTORY = f"{os.path.dirname(__file__)}/playbook.yaml"


def event_handler(data):
    if data["event"] in ["playbook_on_task_start", "runner_on_ok"]:
        sleep(5)
        print("Event Type:", data["event"])
        print("Instance:", data["event_data"]["task"])


if __name__ == "__main__":
    limitation = "host_1"

    runner_config = {
        "private_data_dir": "./tmp/ansible-runner/",
        "inventory": INVENTORY_DIRECTORY,
        "playbook": PLAYBOOK_DIRECTORY,
        "verbosity": DEFAULT_VERBOSITY,
        "limit": limitation,
        "event_handler": event_handler,
    }

    runner = ansible_runner.run(**runner_config)
