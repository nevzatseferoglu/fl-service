import os
from enum import Enum

ROOT_DIR = f"{os.path.dirname(os.path.abspath(__file__))}"
 


# TODO : Add useful directory path.
class AnsibleDirectory(str, Enum):
    TMP_DIR = os.path.join(ROOT_DIR, "ansible", "tmp")
