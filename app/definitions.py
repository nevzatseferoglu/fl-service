import os

ROOT_DIR = f"{os.path.dirname(os.path.abspath(__file__))}"
ANSIBLE_INVENTORY_DIR = os.path.join(ROOT_DIR, "ansible", "inventory")
ANSIBLE_PLAYBOOK_DIR = os.path.join(ROOT_DIR, "ansible", "playbook")
