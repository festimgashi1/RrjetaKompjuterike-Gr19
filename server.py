import os
import sys
import socket
import threading
import json
import time
import base64
import traceback
from datetime import datetime
from pathlib import Path

HOST = os.environ.get("TCP_HOST", "127.0.0.1")
PORT = int(os.environ.get("TCP_PORT", "9099"))
SERVER_ROOT = Path(os.environ.get("SERVER_ROOT", "./server_root")).resolve()
MAX_ACTIVE = int(os.environ.get("MAX_ACTIVE", "8"))  
IDLE_TIMEOUT = int(os.environ.get("IDLE_TIMEOUT", "120")) 
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "letmein")  
LOG_FILE = Path(os.environ.get("LOG_FILE", "server_stats.txt")).resolve()
ARTIFICIAL_DELAY_READONLY = float(os.environ.get("READONLY_DELAY", "0.12"))  
STATS_WRITE_INTERVAL = int(os.environ.get("STATS_WRITE_INTERVAL", "5"))  
MESSAGE_LOG = Path(os.environ.get("MESSAGE_LOG", "messages.log")).resolve()

SERVER_ROOT.mkdir(parents=True, exist_ok=True)

clients_lock = threading.Lock()
clients = {} 

total_bytes_in = 0
total_bytes_out = 0
server_running = True

def safe_send(sock, payload: dict):
    global total_bytes_out
    data = (json.dumps(payload) + "\n").encode('utf-8')
    try:
        sock.sendall(data)
        with clients_lock:
            info = clients.get(sock)
            if info:
                info['bytes_out'] += len(data)
            total_record_out = True
        total_bytes_out += len(data)
    except Exception:
        pass

def record_message(username, addr, text):
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {addr[0]}:{addr[1]} {username}: {text}\n"
    with MESSAGE_LOG.open("a", encoding="utf-8") as f:
        f.write(line)

def normalize_path(p: str) -> Path:
   
    candidate = (SERVER_ROOT / p).resolve()
    if SERVER_ROOT not in candidate.parents and candidate != SERVER_ROOT:
        raise ValueError("Access outside server root is not allowed")
    return candidate

def handle_command(sock, info, cmd: str, args: list, raw_text: str):
     record_message(info['username'], info['addr'], raw_text.strip())

    if not info['is_admin'] and ARTIFICIAL_DELAY_READONLY > 0:
        time.sleep(ARTIFICIAL_DELAY_READONLY)

    if cmd == "/ping":
        return {"ok": True, "data": "pong"}

    if cmd == "/list":
        directory = normalize_path(args[0]) if args else SERVER_ROOT
        if not directory.exists() or not directory.is_dir():
            return {"ok": False, "error": "Directory not found"}
         items = []
        for entry in sorted(directory.iterdir()):
            items.append({
                "name": entry.name,
                "is_dir": entry.is_dir(),
                "size": entry.stat().st_size
            })
        return {"ok": True, "data": items}