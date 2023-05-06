import os


def create_file(filepath: str) -> bool:
    """
    Create a file if it doesn't exist.

    Side effect: creates intermediate directories if they don't exist.
    """

    if os.path.exists(filepath):
        return False

    os.makedirs(name=os.path.dirname(filepath), exist_ok=True)

    try:
        with open(filepath, "w"):
            # intentionally left blank
            pass
    except OSError:
        return False
    else:
        return True
