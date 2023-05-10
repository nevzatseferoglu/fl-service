import os

import ansible_runner

DEFAULT_VERBOSITY = 4
INVENTORY_DIRECTORY = f"{os.path.dirname(__file__)}/inventory.yaml"
PLAYBOOK_DIRECTORY = f"{os.path.dirname(__file__)}/playbook.yaml"


# def generator(extravar):
#     def event_handler(data: dict):
#         if "event_data" in data:
#             print("My extravar: ", extravar)

#     return event_handler


if __name__ == "__main__":
    my_object = {"key1": "value1", "key2": "value2", "key3": "value3"}

    runner_config = {
        "private_data_dir": "./tmp/ansible-runner/",
        "inventory": INVENTORY_DIRECTORY,
        "playbook": PLAYBOOK_DIRECTORY,
        "verbosity": DEFAULT_VERBOSITY,
    }

    my_object = {"key1": "value4", "key2": "value4", "key3": "value4"}

    runner = ansible_runner.run(**runner_config)
    print(runner.status)
