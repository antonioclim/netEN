#!/usr/bin/env python3
"""Exercise 1.02: Local TCP server and client (Week 1)

The goal is to demonstrate that a TCP port maps to a listening socket and that a
client can connect, exchange data and close cleanly.

The demo runs the server and client in the same process using a background thread
to keep execution deterministic for automated validation.
"""

from __future__ import annotations

import argparse
import socket
import threading
import time


def run_server(host: str, port: int, ready: threading.Event, stop: threading.Event) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(1)
        ready.set()
        s.settimeout(0.5)
        while not stop.is_set():
            try:
                conn, _addr = s.accept()
            except socket.timeout:
                continue
            with conn:
                data = conn.recv(4096)
                conn.sendall(b"ACK:" + data)
                break


def run_client(host: str, port: int, payload: bytes, timeout_s: float) -> bytes:
    with socket.create_connection((host, port), timeout=timeout_s) as c:
        c.sendall(payload)
        return c.recv(4096)


def main() -> int:
    ap = argparse.ArgumentParser(description="Run a deterministic local TCP server and client exchange.")
    ap.add_argument("--host", default="127.0.0.1", help="Bind and connect host (default: 127.0.0.1).")
    ap.add_argument("--port", type=int, default=9090, help="TCP port to use (default: 9090).")
    ap.add_argument("--message", default="hello", help="Payload message.")
    ap.add_argument("--timeout-s", type=float, default=2.0, help="Client connection timeout in seconds.")
    args = ap.parse_args()

    ready = threading.Event()
    stop = threading.Event()

    t = threading.Thread(target=run_server, args=(args.host, args.port, ready, stop), daemon=True)
    t.start()
    if not ready.wait(timeout=2.0):
        print("TCP server failed to start")
        return 1

    payload = (args.message + "\n").encode("utf-8")
    start = time.time()
    resp = run_client(args.host, args.port, payload, args.timeout_s)
    elapsed_ms = (time.time() - start) * 1000.0
    stop.set()
    t.join(timeout=1.0)

    print(f"TCP host={args.host} port={args.port} rtt_ms={elapsed_ms:.2f} response={resp.decode('utf-8', errors='replace').strip()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
