from enum import Enum

class DOCKER_INSTALLATION_NAME(str, Enum):
    state_install_aptitude = "state_install_aptitude"
    state_install_required_system_packages = "state_install_required_system_packages"
    state_add_docker_gpg_apt_key = "state_add_docker_gpg_apt_key"
    state_add_docker_repository = "state_add_docker_repository"
    state_update_apt_and_install_docker_ce = "state_update_apt_and_install_docker_ce"
    state_install_docker_module_for_python = "state_install_docker_module_for_python"


class InstallationStatus(str, Enum):
    ok = "ok"
    failed = "failed"
    unreachable = "unreachable"
    skipped = "skipped"


class StatusType(str, Enum):
    """
    Status type.
    """

    success = "success"
    error = "error"


class OsType(str, Enum):
    """
    Operating system type.
    """

    linux = "linux"
    windows = "windows"
    macos = "macos"
    raspberry_pi = "raspberry_pi"
    android = "android"
    ios = "ios"
    freebsd = "freebsd"
    netbsd = "netbsd"
    openbsd = "openbsd"


class FlowerType(str, Enum):
    """
    Flower component type.
    """

    server = "server"
    client = "client"
