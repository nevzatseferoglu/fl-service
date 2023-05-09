import os

import ansible_runner

DEFAULT_VERBOSITY = 3
INVENTORY_DIRECTORY = f"{os.path.dirname(__file__)}/inventory.yaml"
PLAYBOOK_DIRECTORY = f"{os.path.dirname(__file__)}/playbook.yaml"


async def event_handler(event_data: dict):
    print(event_data["event"])


if __name__ == "__main__":
    runner_config = {
        "private_data_dir": "./tmp/ansible-runner/",
        "inventory": INVENTORY_DIRECTORY,
        "playbook": PLAYBOOK_DIRECTORY,
        "verbosity": DEFAULT_VERBOSITY,
        "event_handler": event_handler,
    }
    thread, runner = ansible_runner.run_async(**runner_config)
    thread.join()
    print(runner.status)
