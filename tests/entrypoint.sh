#!/bin/sh

# Description: Entrypoint script for the test container

# Allow root login with public key authentication in sshd_config
sed -i 's/#\?PermitRootLogin.*/PermitRootLogin prohibit-password/g' /etc/ssh/sshd_config
sed -i 's/#\?PubkeyAuthentication.*/PubkeyAuthentication yes/g' /etc/ssh/sshd_config

/bin/sh
