import os
from enum import Enum
from time import sleep
from ...app.internal.schema import RemoteHostDockerState


import ansible_runner

DEFAULT_VERBOSITY = 0
INVENTORY_DIRECTORY = f"{os.path.dirname(__file__)}/inventory.yaml"
PLAYBOOK_DIRECTORY = f"{os.path.dirname(__file__)}/playbook.yaml"


def event_handler(data):
    if data["event"] in ["playbook_on_task_start", "runner_on_ok"]:
        sleep(5)
        print("Event Type:", data["event"])
        print("Instance:", data["event_data"]["task"])

def get_variable_name(var, namespace=globals()):
    return [name for name, value in namespace.items() if value is var][0]

class DOCKER_INSTALLATION_NAME(str, Enum):
    state_install_aptitude = "state_install_aptitude"
    state_install_required_system_packages = "state_install_required_system_packages"
    state_add_docker_gpg_apt_key = "state_add_docker_gpg_apt_key"
    state_add_docker_repository = "state_add_docker_repository"
    state_update_apt_and_install_docker_ce = "state_update_apt_and_install_docker_ce"
    state_install_docker_module_for_python = "state_install_docker_module_for_python"

if __name__ == "__main__":
    print(RemoteHostDockerState.state_install_docker_module_for_python)
