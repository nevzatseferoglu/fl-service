

class GenerateSSHKeyPairException(Exception):
    def __init__(self, name: str):
        self.name = name


class CopySSHKeyToRemoteException(Exception):
    def __init__(self, name: str):
        self.name = name