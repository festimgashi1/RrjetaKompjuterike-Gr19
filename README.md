# RrjetaKompjuterike – Gr19
### TCP Server & Client with Authentication, File Commands, Logging, Timeout & Monitoring

This project contains a fully functional TCP Server and Client written in Python using only the standard library.  
The system supports user authentication, admin/read-only permissions, file operations, automatic reconnect, idle timeout, safe path handling, and real-time monitoring.

---

## 🚀 Features Overview

### 🖥️ Server
- Configurable host and port via environment variables
- Limits active connections (`MAX_ACTIVE`)
- Supports admin and read-only roles
- Logs all client messages to **`messages.log`**
- Idle timeout disconnection (`IDLE_TIMEOUT`)
- Safe file access inside `SERVER_ROOT` only
- Base64 file upload/download support
- Real-time monitoring of:
  - Active connections  
  - Client IP addresses  
  - Client message counts  
  - Bytes in/out per client  
  - Total bytes in/out  
- Print live stats by typing **`STATS`** in the server console
- Periodic stats writing to **`server_stats.txt`**
- Artificial delay for read-only users (admin users respond faster)
- Thread-per-client architecture

---

### 👤 Client
- Connects and authenticates using a JSON handshake
- Admin access if the token matches `ADMIN_TOKEN`
- Automatically reconnects if server disconnects or timeout occurs
- Sends commands using JSON frames (`\n` delimited)
- Upload/download files using Base64 encoding
- Supports free-text messages (logged by server)
- Pretty-print responses

---

## 🗂️ Command List

| Command | Description | Admin Only |
|--------|-------------|------------|
| `/list [dir]` | List directory contents | No |
| `/read <file>` | Read a file as text | No |
| `/download <file>` | Download file (Base64) | No |
| `/ping` | Latency check | No |
| `/upload <filename> <data_b64>` | Upload file | Yes |
| `/delete <file>` | Delete file | Yes |
| `/search <keyword>` | Search filenames | Yes |
| `/info <file>` | Show file metadata | Yes |

### Free-text message
Any line **not starting with `/`** is treated as a normal message:  
- Server logs it in `messages.log`
- Responds with:

```json
{"ok": true, "data": "message logged"}
🔐 Authentication Protocol
Client must send this as the first message:

json
Copy code
{"username": "alice", "token": "letmein"}
Server responds:

json
Copy code
{
  "ok": true,
  "msg": "WELCOME",
  "server_root": "/abs/path/server_root",
  "role": "admin" | "readonly"
}
If token == ADMIN_TOKEN → admin.
Otherwise → readonly.

🕒 Idle Timeout & Auto-Reconnect
If a client is inactive longer than IDLE_TIMEOUT seconds, server sends:

json
Copy code
{"ok": false, "error": "Idle timeout, disconnecting"}
Then disconnects.

The client automatically:

Detects the disconnect

Waits with exponential backoff

Reconnects automatically

📊 Real-Time Monitoring
Type:

nginx
Copy code
STATS
in the server terminal to view:

Active clients

Client usernames & roles

Messages per client

Bytes in/out

Last active timestamps

Total server traffic

Server also writes stats every few seconds into:

Copy code
server_stats.txt
📁 Safe File System Access
All file paths are normalized:

python
Copy code
candidate = (SERVER_ROOT / p).resolve()
This prevents escaping outside server root (no ../.. traversal allowed).

Deleting directories is blocked. Only files may be deleted.

⚙️ Environment Variables
Variable	Default	Description
TCP_HOST	127.0.0.1	Server bind IP
TCP_PORT	9099	Server port
SERVER_ROOT	./server_root	Sandbox directory
MAX_ACTIVE	8	Max active connections
IDLE_TIMEOUT	120	Idle timeout (seconds)
ADMIN_TOKEN	letmein	Admin token
READONLY_DELAY	0.12	Delay for readonly users
MESSAGE_LOG	messages.log	Free-text log file
LOG_FILE	server_stats.txt	Stats output file
STATS_WRITE_INTERVAL	5	Stats write interval

▶️ Running the Server
bash
Copy code
export TCP_HOST=127.0.0.1
export TCP_PORT=9099
python server.py
Server output:

csharp
Copy code
[SERVER] Starting on 127.0.0.1:9099
[SERVER] Listening...
💻 Running a Read-Only Client
bash
Copy code
python client.py --host 127.0.0.1 --port 9099 --username bob
Example usage:

bash
Copy code
/list
/read notes.txt
/download notes.txt
Hello server! This will be logged.
🔑 Running an Admin Client
bash
Copy code
python client.py --host 127.0.0.1 --port 9099 --username admin --token letmein
Admin examples:

bash
Copy code
/upload README.md
/search .txt
/info data.txt
/delete old.txt
🔗 JSON Command Protocol
Send command:
json
Copy code
{"cmd": "/list", "args": []}
Server response:
json
Copy code
{"ok": true, "data": [...]}
Error example:
json
Copy code
{"ok": false, "error": "File not found"}

 Security Notes
Path traversal is blocked using .resolve()

Directory deletion is not allowed

Admin token is for demo only (not production secure)

All file operations stay inside SERVER_ROOT



