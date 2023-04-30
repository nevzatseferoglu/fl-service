import copy

from ...ansible.inventory.dynamic_inventory import (FLOWER_CLIENTS_GROUP,
                                                    FLOWER_SERVER_GROUP)
from ...internal.utils.enum import FlowerType

INSTALL_DOCKER_PLAYBOOK = {
    "name": "Install ansible",
    "hosts": None,
    "become": True,
    "vars": {
        "default_container_name": "hello-world-test-container",
        "default_container_image": "hello-world",
    },
    "tasks": [
        {
            "name": "Install aptitude",
            "ansible.builtin.apt": {
                "name": "aptitude",
                "state": "present",
                "update_cache": True,
            },
        },
        {
            "name": "Install required system packages",
            "ansible.builtin.apt": {
                "pkg": [
                    "apt-transport-https",
                    "ca-certificates",
                    "curl",
                    "software-properties-common",
                    "python3-pip",
                    "virtualenv",
                    "python3-setuptools",
                ],
                "state": "present",
                "update_cache": True,
            },
        },
        {
            "name": "Add Docker GPG apt Key",
            "ansible.builtin.apt_key": {
                "url": "https://download.docker.com/linux/ubuntu/gpg",
                "state": "present",
            },
        },
        {
            "name": "Add Docker Repository",
            "ansible.builtin.apt_repository": {
                "repo": "deb https://download.docker.com/linux/ubuntu focal stable",
                "state": "present",
            },
        },
        {
            "name": "Update apt and instal docker-ce",
            "ansible.builtin.apt": {
                "name": "docker-ce",
                "state": "present",
                "update_cache": True,
            },
        },
        {
            "name": "Install Docker Module for Python",
            "ansible.builtin.pip": {
                "name": "docker",
            },
        },
    ],
}


def new_remote_host_dict_docker_playbook(host_identifier: str, flower_type: FlowerType):
    """
    Create a new playbook to install docker on a remote host.

    hostname: It should be valid with ansible inventory file hostname pattern.
    depends_on: Given host is need to be an ubuntu 20,04. And it should be in the inventory file.
    """

    newcopy = copy.deepcopy(INSTALL_DOCKER_PLAYBOOK)["hosts"]

    if flower_type == FlowerType.client:
        newcopy["hosts"] = f"{FLOWER_CLIENTS_GROUP}:{host_identifier}"
    else:
        newcopy["hosts"] = f"{FLOWER_SERVER_GROUP}:{host_identifier}"
    return newcopy
