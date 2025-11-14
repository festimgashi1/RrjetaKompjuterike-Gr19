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
