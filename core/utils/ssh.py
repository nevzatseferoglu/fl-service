
import os
import subprocess
import logging

def command_exists(cmd: str) -> bool:
    """
    Check if a command exists in the system path.
    """
    try:
        if os.name == "nt":
            # On Windows, use the 'where' command to find the executable.
            result = subprocess.run(["where", cmd], stdout=subprocess.PIPE, shell=True)
        else:
            # On Unix-based systems, use the 'which' command to find the executable.
            result = subprocess.run(
                ["which", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
    except subprocess.CalledProcessError or subprocess.TimeoutExpired as e:
        logging.warning(f"Exception while checking if command {cmd} exists: {e}")
        return False
    return result.returncode == 0
