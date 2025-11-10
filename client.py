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