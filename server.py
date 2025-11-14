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
    
    if cmd == "/read":
        if not args:
            return {"ok": False, "error": "Usage: /read <filename>"}
        fpath = normalize_path(args[0])
        if not fpath.exists() or not fpath.is_file():
            return {"ok": False, "error": "File not found"}
        try:
            content = fpath.read_text(encoding="utf-8", errors="ignore")
            return {"ok": True, "data": content}
        except Exception as e:
            return {"ok": False, "error": f"Read failed: {e}"}
        
    if cmd == "/download":
        if not args:
            return {"ok": False, "error": "Usage: /download <filename>"}
        fpath = normalize_path(args[0])
        if not fpath.exists() or not fpath.is_file():
            return {"ok": False, "error": "File not found"}
        try:
            data = fpath.read_bytes()
            return {"ok": True, "filename": fpath.name, "data_b64": base64.b64encode(data).decode("ascii")}
        except Exception as e:
            return {"ok": False, "error": f"Download failed: {e}"}

    # Admin-only below
    if cmd in ("/upload", "/delete", "/info", "/search"):
        if not info['is_admin']:
            return {"ok": False, "error": "Permission denied: admin only"}

    if cmd == "/upload":
        # args: filename, data_b64
        if len(args) < 2:
            return {"ok": False, "error": "Usage: /upload <filename> <data_b64> (or send in JSON 'data_b64')"}
        filename = args[0]
        data_b64 = args[1]
        try:
            fpath = normalize_path(filename)
            fpath.parent.mkdir(parents=True, exist_ok=True)
            data = base64.b64decode(data_b64.encode("ascii"))
            fpath.write_bytes(data)
            return {"ok": True, "data": f"Uploaded {fpath.name} ({len(data)} bytes)"}
        except Exception as e:
            return {"ok": False, "error": f"Upload failed: {e}"}

    if cmd == "/delete":
        if not args:
            return {"ok": False, "error": "Usage: /delete <filename>"}
        fpath = normalize_path(args[0])
        try:
            if fpath.is_dir():
                return {"ok": False, "error": "Refusing to delete directories"}
            if fpath.exists():
                fpath.unlink()
                return {"ok": True, "data": f"Deleted {fpath.name}"}
            else:
                return {"ok": False, "error": "File not found"}
        except Exception as e:
            return {"ok": False, "error": f"Delete failed: {e}"}
        
    if cmd == "/search":
        if not args:
            return {"ok": False, "error": "Usage: /search <keyword>"}
        keyword = args[0].lower()
        matches = []
        for dirpath, dirnames, filenames in os.walk(SERVER_ROOT):
            for name in filenames:
                if keyword in name.lower():
                    full = Path(dirpath) / name
                    rel = full.relative_to(SERVER_ROOT).as_posix()
                    matches.append(rel)
        return {"ok": True, "data": matches}
    
    if cmd == "/info":
        if not args:
            return {"ok": False, "error": "Usage: /info <filename>"}
        fpath = normalize_path(args[0])
        if not fpath.exists():
            return {"ok": False, "error": "File not found"}
        st = fpath.stat()
        return {"ok": True, "data": {
            "name": fpath.name,
            "size": st.st_size,
            "created": datetime.fromtimestamp(st.st_ctime).isoformat(sep=' ', timespec='seconds'),
            "modified": datetime.fromtimestamp(st.st_mtime).isoformat(sep=' ', timespec='seconds'),
            "is_dir": fpath.is_dir()
        }}

    return {"ok": False, "error": f"Unknown command: {cmd}"}