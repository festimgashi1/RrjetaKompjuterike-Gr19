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