import os
import subprocess
from subprocess import PIPE, Popen
from pathlib import Path
def startCfTunnel():
    # gitpod
    # cloudflaredTunnelToken="eyJhIjoiNjIzZmFmNzJlZTBkMmFmM2U1ODZlN2NkOWRhZGI3MmIiLCJ0IjoiNmUyMWMwNjAtZjRkOC00NmJjLTk2NjEtODA1M2M0ZGE0MzRlIiwicyI6Ill6TmpPREpoWWpVdE5EWTRNUzAwTVdSbExUazVZbVl0TXpGalpHSmlNRE14WXpOaSJ9"
    # colab
    cloudflaredTunnelToken="eyJhIjoiNjIzZmFmNzJlZTBkMmFmM2U1ODZlN2NkOWRhZGI3MmIiLCJ0IjoiYmZlNDA2YTMtM2E1OC00MDRiLWI0OWItNmMxYzA2NjlkYjg3IiwicyI6IllUazBOemhqTnpJdE5URTJZeTAwWTJGaUxUbGhOakl0WW1ZNE1HTXdOV0V5TVRReSJ9"
    my_file = Path(".vol/bin/cloudflared")
    if not my_file.is_file():
        print("安装cloudflared")
        cmd=f"mkdir -p .vol/bin && curl -o {my_file} -sSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
    && chmod +x {my_file}"
        with Popen(cmd, stdout=PIPE, stderr=None, shell=True) as process:
            output = process.communicate()[0].decode("utf-8")
            print(output)
    print("启动cloudflared")
    cmd=f"sudo {my_file} tunnel --no-autoupdate run --token {cloudflaredTunnelToken}"
    with Popen(cmd, stdout=PIPE, stderr=None, shell=True) as process:
        output = process.communicate()[0].decode("utf-8")
        print(output)