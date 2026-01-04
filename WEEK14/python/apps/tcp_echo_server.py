#!/usr/bin/env python3
"""tcp_echo_server.py — Simple TCP echo server for demonstrations.

Features:
  - Accepts TCP connections
  - Returns received data (echo)
  - Logging with timestamp

Usage:
  python3 tcp_echo_server.py --host 0.0.0.0 --port 9000
"""

from __future__ import annotations

import argparse
import socket
import threading
from datetime import datetime


def log(msg: str) -> None:
    """Logging with timestamp."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{ts}] [echo-server] {msg}")


def handle_client(client_socket: socket.socket, client_addr: tuple) -> None:
    """Processes a client connection."""
    addr_str = f"{client_addr[0]}:{client_addr[1]}"
    log(f"Connection from {addr_str}")
    
    try:
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            
            log(f"Received from {addr_str}: {data!r}")
            client_socket.sendall(data)
            log(f"Echoed back to {addr_str}: {len(data)} bytes")
    except (ConnectionResetError, BrokenPipeError) as e:
        log(f"Connection error with {addr_str}: {e}")
    finally:
        client_socket.close()
        log(f"Connection closed: {addr_str}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TCP Echo Server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address")
    parser.add_argument("--port", type=int, default=9000, help="Listening port")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((args.host, args.port))
    server_socket.listen(5)
    
    log(f"TCP Echo Server listening on {args.host}:{args.port}")
    
    try:
        while True:
            client_socket, client_addr = server_socket.accept()
            thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_addr),
                daemon=True
            )
            thread.start()
    except KeyboardInterrupt:
        log("Shutting down...")
    finally:
        server_socket.close()
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
