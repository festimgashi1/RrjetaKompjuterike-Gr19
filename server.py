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