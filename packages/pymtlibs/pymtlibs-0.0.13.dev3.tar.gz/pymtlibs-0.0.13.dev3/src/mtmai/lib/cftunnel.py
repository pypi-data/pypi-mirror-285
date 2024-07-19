import os
import subprocess
from subprocess import PIPE, Popen
def startCfTunnel():
    command = """command -v cloudflared || (
        curl -o ${HOME}/.local/bin/cloudflared -sSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
    && chmod +x ${HOME}/.local/bin/cloudflared
)

"""
    with Popen(command, stdout=PIPE, stderr=None, shell=True) as process:
        output = process.communicate()[0].decode("utf-8")
        print(output)
    cloudflaredTunnelToken="eyJhIjoiNjIzZmFmNzJlZTBkMmFmM2U1ODZlN2NkOWRhZGI3MmIiLCJ0IjoiNmUyMWMwNjAtZjRkOC00NmJjLTk2NjEtODA1M2M0ZGE0MzRlIiwicyI6Ill6TmpPREpoWWpVdE5EWTRNUzAwTVdSbExUazVZbVl0TXpGalpHSmlNRE14WXpOaSJ9"

    print("dddddddddddddddd")
    cmd="sudo ${HOME}/.local/bin/cloudflared tunnel --no-autoupdate run --token "+cloudflaredTunnelToken
    with Popen(cmd, stdout=PIPE, stderr=None, shell=True) as process:
        output = process.communicate()[0].decode("utf-8")
        print ("ssssssssssssssss")
        print(output)