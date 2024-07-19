#!/bin/bash

set -e

SSH_TUNNEL_USER="sshtunnel"
SSH_TUNNEL_PASSWORD="feihuo321"

# 端口，允许密码登陆，允许root密码登陆
echo "Port 2222
PasswordAuthentication yes
PermitRootLogin yes
AllowAgentForwarding yes
AllowTcpForwarding yes
" | sudo tee /etc/ssh/sshd_config > /dev/null

#用户不存在就先添加一个。
set +e
id ${SSH_TUNNEL_USER} > /dev/null
if [ $? -ne 0 ]; then
    echo "添加ssh tunnel用户：${SSH_TUNNEL_USER}"
    sudo useradd -ms /bin/bash ${SSH_TUNNEL_USER}
    echo "${SSH_TUNNEL_USER}:${SSH_TUNNEL_PASSWORD}" | sudo chpasswd
fi
set -e




