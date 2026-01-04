"""TCP echo server for Week 7.

The server is intentionally small and predictable:
- logs each connection and message
- can stop after one connection (useful for Docker Compose demos)
"""

from __future__ import annotations

import argparse
import socket
import threading
import time
from pathlib import Path
from typing import Optional


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Simple TCP echo server (Week 7).")
    p.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    p.add_argument("--port", type=int, default=9090, help="Bind port (default: 9090)")
    p.add_argument("--log", default="", help="Optional log file path")
    p.add_argument("--once", action="store_true", help="Exit after handling a single client")
    p.add_argument("--timeout", type=float, default=10.0, help="Socket timeout in seconds (default: 10)")
    return p


def log_line(path: Optional[Path], line: str) -> None:
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{stamp}] {line}"
    print(msg, flush=True)
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(msg + "\n")


def handle_client(conn: socket.socket, addr: tuple[str, int], log_path: Optional[Path], timeout: float) -> None:
    conn.settimeout(timeout)
    log_line(log_path, f"client connected from {addr[0]}:{addr[1]}")
    try:
        data = conn.recv(4096)
        if not data:
            log_line(log_path, "client sent no data")
            return
        # Keep bytes but log as safe text
        try:
            text = data.decode("utf-8", errors="replace").strip()
        except Exception:
            text = "<decode error>"
        log_line(log_path, f"received: {text}")
        conn.sendall(data)
        log_line(log_path, "echoed back data")
    except socket.timeout:
        log_line(log_path, "client read timed out")
    except Exception as exc:
        log_line(log_path, f"error: {exc}")
    finally:
        try:
            conn.close()
        except Exception:
            pass
        log_line(log_path, "client connection closed")


def main() -> int:
    args = build_parser().parse_args()
    log_path = Path(args.log) if args.log else None

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((args.host, args.port))
    srv.listen(50)
    log_line(log_path, f"listening on {args.host}:{args.port}")

    handled = 0
    try:
        while True:
            conn, addr = srv.accept()
            th = threading.Thread(target=handle_client, args=(conn, addr, log_path, args.timeout), daemon=True)
            th.start()
            handled += 1
            if args.once and handled >= 1:
                # Give the handler a moment to flush logs.
                time.sleep(0.2)
                break
    except KeyboardInterrupt:
        log_line(log_path, "interrupted")
    finally:
        try:
            srv.close()
        except Exception:
            pass
        log_line(log_path, "server stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
