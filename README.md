# RrjetaKompjuterike-Gr19

This project implements a TCP server and client in Python that satisfy the full set of requirements:

## Features Summary

### Server
1. **Configurable IP/Port** via environment variables `TCP_HOST`, `TCP_PORT`.
2. **Connection limiting** with `MAX_ACTIVE`; excess connections are refused with a JSON error.
3. **Request handling**: every connected client can issue at least one command; all incoming text is logged.
4. **Message logging**: all client messages are stored in `welcome.txt` for monitoring.
5. **Idle timeout**: If a client is silent for `IDLE_TIMEOUT` seconds, the server closes the connection. The client auto-reconnects.
6. **File access**: Full access (rwx) granted to **admin** clients. Read-only clients can `/list`, `/read`, `/download`. Admins can also `/upload`, `/delete`, `/search`, `/info`.

7. **Traffic monitoring** in real-time:
   - Active connection count
   - Active client IP addresses
   - Per-client message count
   - Total bytes sent/received

   View via typing `STATS` into the server console, or by reading `server_stats.txt` (updated every few seconds).

### Client
1. Creates a TCP socket connection.
2. One client can have full privileges using an **admin token** (`--token letmein` by default).
3. Supported commands:

| Command | Description |
|---|---|
| `/list [dir]` | List files under server root or directory |
| `/read <file>` | Read a text file |
| `/upload <localfile> [remote_name]` | Upload local file (admin) |
| `/download <file> [save_as]` | Download from server |
| `/delete <file>` | Delete a file (admin) |
| `/search <keyword>` | Search filenames (admin) |
| `/info <file>` | Show size/created/modified (admin) |
| `/ping` | Check latency |

4. Non-admin clients have **read-only** permissions.
5. Connect using the correct IP/port and role; protocol uses JSON over newline-delimited frames for reliability.
6. Sockets are fully defined; failures print clear errors.
7. Client reads responses from the server and prints them.
8. Client can send free-form text (not starting with `/`) to be logged by the server.
9. Admin clients have **lower latency**: the server applies a small artificial delay to read-only clients (`READONLY_DELAY`), making admin responses faster.
10. Automatic **reconnect** if the server drops the connection due to idle timeout or network errors.

## Quick Start

### 1 Create a Python venv (optional)
```bash
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install --upgrade pip
```

> No external packages required (standard library only).

### 2 Start the server
```bash
export TCP_HOST=127.0.0.1
export TCP_PORT=9099
python server.py
```
- Type `STATS` in the server terminal anytime for live metrics.
- Server writes periodic stats to `server_stats.txt`.

Optional env vars:
```
SERVER_ROOT=./server_root
MAX_ACTIVE=8
IDLE_TIMEOUT=120
ADMIN_TOKEN=letmein
READONLY_DELAY=0.12
STATS_WRITE_INTERVAL=5
MESSAGE_LOG=messages.log
LOG_FILE=server_stats.txt
```

### 3  Run a read-only client
```bash
python client.py --host 127.0.0.1 --port 9099 --username bob
```

Try:
```
/list
/read welcome.txt
/download notes.md
Hello server, this is a free text message that will be logged!
```

### 4) Run an admin client (full access)
```bash
python client.py --host 127.0.0.1 --port 9099 --username admin --token letmein
```
Now you can also:
```
/upload README.md
/search .md
/info notes.md
/delete somefile.txt
```

### Protocol

- Client authenticates first by sending a single JSON line:
  ```json
  {"username": "alice", "token": "letmein"}
  ```
- Then each command is sent as JSON line:
  ```json
  {"cmd": "/list", "args": []}
  ```
- The server responds with JSON per line:
  ```json
  {"ok": true, "data": [...]}
  ```
- If user types **raw text** (not starting with `/`) in the client shell, it is sent as-is and the server logs it to `messages.log`.

### Security Notes

- Paths are normalized so clients cannot escape the configured `SERVER_ROOT` (blocks `..` traversal).
- Deleting directories is refused for safety (only file delete allowed).
- Admin token is a simple shared secret for demo/academic purposes. For production, use TLS + proper authentication.

### GitHub Guidance

- Push **early and often**. Commit in small, incremental steps to avoid penalty points.
- Make the repository public.
- Each team member should:
  - Fork or clone the repo
  - Add/commit their contributions
  - Open PRs for review history
  - Ensure both `server.py` and `client.py` run on their machines

### Grading/Defense Tips

- Be ready to explain:
  - Socket lifecycle, JSON framing, idle timeout, reconnect behavior
  - Permission model and why admins are faster
  - Monitoring metrics & how `STATS` works
  - How path normalization protects the server
  - How uploads/downloads are Base64-encoded over the TCP stream
```