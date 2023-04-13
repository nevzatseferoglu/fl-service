from enum import Enum


class StatusType(str, Enum):
    """Status type"""

    success = "success"
    error = "error"


class Architecture(str, Enum):
    """Architecture type"""

    x86 = "x86"
    x64 = "x64"
    arm = "arm"
    arm64 = "arm64"


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
