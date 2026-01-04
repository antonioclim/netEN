"""TCP client for Week 7 demos.

Sends a single message and checks the echo response.
"""

from __future__ import annotations

import argparse
import socket
import time
from pathlib import Path
from typing import Optional


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Simple TCP client (Week 7).")
    p.add_argument("--host", required=True, help="Server address or name")
    p.add_argument("--port", type=int, default=9090, help="Server port (default: 9090)")
    p.add_argument("--message", default="hello", help="Message to send (default: hello)")
    p.add_argument("--timeout", type=float, default=3.0, help="Timeout in seconds (default: 3)")
    p.add_argument("--log", default="", help="Optional log file path")
    return p


def log_line(path: Optional[Path], line: str) -> None:
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{stamp}] {line}"
    print(msg, flush=True)
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(msg + "\n")


def main() -> int:
    args = build_parser().parse_args()
    log_path = Path(args.log) if args.log else None

    msg_bytes = (args.message + "\n").encode("utf-8")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(args.timeout)

    try:
        log_line(log_path, f"connecting to {args.host}:{args.port}")
        s.connect((args.host, args.port))
        s.sendall(msg_bytes)
        data = s.recv(4096)
        if not data:
            log_line(log_path, "no response received")
            return 2
        echoed = data.decode("utf-8", errors="replace").strip()
        log_line(log_path, f"received: {echoed}")
        if echoed != args.message:
            log_line(log_path, "echo mismatch")
            return 3
        log_line(log_path, "ok")
        return 0
    except socket.timeout:
        log_line(log_path, "timeout")
        return 4
    except ConnectionRefusedError:
        log_line(log_path, "connection refused")
        return 5
    except Exception as exc:
        log_line(log_path, f"error: {exc}")
        return 6
    finally:
        try:
            s.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
