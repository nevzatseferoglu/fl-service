import os

import ansible_runner

DEFAULT_VERBOSITY = 0
INVENTORY_DIRECTORY = f"{os.path.dirname(__file__)}/inventory.yaml"
PLAYBOOK_DIRECTORY = f"{os.path.dirname(__file__)}/playbook.yaml"

if __name__ == "__main__":
    limitation = "192.168.1.105"

    runner_config = {
        "private_data_dir": "./tmp/ansible-runner/",
        "inventory": INVENTORY_DIRECTORY,
        "playbook": PLAYBOOK_DIRECTORY,
        "verbosity": DEFAULT_VERBOSITY,
        "limit": limitation,
    }

    runner = ansible_runner.run(**runner_config)
