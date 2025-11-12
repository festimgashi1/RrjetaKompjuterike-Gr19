import argparse
import socket
import json
import time
import sys
import base64
from pathlib import Path

def recv_json_line(sock):
    buff = b""
    while True:
        ch = sock.recv(1)
        if not ch:
            return None
        buff += ch
        if ch == b"\n":
            break
    try:
        return json.loads(buff.decode("utf-8"))
    except Exception:
        return {"raw": buff.decode("utf-8", errors="ignore")}
    
    def connect(host, port, username, token):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    # auth
    auth = {"username": username, "token": token}
    s.sendall((json.dumps(auth) + "\n").encode("utf-8"))
    welcome = recv_json_line(s)
    if not welcome or not welcome.get("ok", False):
        print("[CLIENT] Auth failed or server busy:", welcome)
        s.close()
        return None
    print(f"[CLIENT] Connected. Role={welcome.get('role')} ServerRoot={welcome.get('server_root')}")
    return s

def send_cmd(sock, cmd, args=None):
    obj = {"cmd": cmd}
    if args:
        obj["args"] = args
    sock.sendall((json.dumps(obj) + "\n").encode("utf-8"))
    return recv_json_line(sock)

