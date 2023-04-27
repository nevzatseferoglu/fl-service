import os
import sys

# Get the parent directory of the current file (i.e. the "tests" directory)
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the parent directory to the Python path
sys.path.append(parent_dir)

import app.ansible.inventory.dynamic_inventory as dy


def test_export_to_yaml():
    try:
        dy.add_new_host_to_flower_inventory(
            "nevzat", "172.144.12.22", "dummy_username", False
        )
        dy.export_to_yaml(dy.FLOWER_INVENTORY, "test_inventory.yaml")
    except Exception as e:
        raise e
    else:
        print("Test passed")


if __name__ == "__main__":
    test_export_to_yaml()
