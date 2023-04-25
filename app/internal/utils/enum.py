from enum import Enum


class StatusType(str, Enum):
    """Status type"""

    success = "success"
    error = "error"


class OsType(str, Enum):
    """Operating system type"""

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
    """Flower component type"""

    server = "server"
    client = "client"
