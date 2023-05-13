import os

ROOT_DIR = f"{os.path.dirname(os.path.abspath(__file__))}"
ANSIBLE_INVENTORY_DIR = os.path.join(ROOT_DIR, "ansible", "inventory")
ANSIBLE_PLAYBOOK_DIR = os.path.join(ROOT_DIR, "ansible", "playbook")


# TODO: Design a mechanism which make it possible to reference
# fl model directory under the inventory file
