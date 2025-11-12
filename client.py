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

def interactive_loop(host, port, username, token):
    backoff = 1
    sock = None
    while True:
        if sock is None:
            try:
                sock = connect(host, port, username, token)
                if sock is None:
                    time.sleep(min(backoff, 10))
                    backoff = min(backoff * 2, 10)
                    continue
                backoff = 1
            except Exception as e:
                print("[CLIENT] Connect error:", e)
                time.sleep(min(backoff, 10))
                backoff = min(backoff * 2, 10)
                continue

               try:
            line = input("client> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[CLIENT] Bye.")
            try:
                sock.close()
            except Exception:
                pass
            return


 if line and not line.startswith("/"):
            try:
                sock.sendall((line + "\n").encode("utf-8"))
                resp = recv_json_line(sock)
                print(resp)
            except Exception as e:
                print("[CLIENT] Send error:", e)
                sock.close()
                sock = None
            continue

        parts = line.split()
        if not parts:
            continue

 cmd = parts[0]
        args = parts[1:]



