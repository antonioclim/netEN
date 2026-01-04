"""UDP receiver for Week 7 demos."""

from __future__ import annotations

import argparse
import socket
import time
from pathlib import Path
from typing import Optional


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Simple UDP receiver (Week 7).")
    p.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    p.add_argument("--port", type=int, default=9091, help="Bind port (default: 9091)")
    p.add_argument("--count", type=int, default=1, help="Number of messages before exit (default: 1)")
    p.add_argument("--timeout", type=float, default=8.0, help="Receive timeout in seconds (default: 8)")
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

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((args.host, args.port))
    s.settimeout(args.timeout)
    log_line(log_path, f"listening on {args.host}:{args.port}")

    received = 0
    try:
        while received < args.count:
            data, addr = s.recvfrom(65535)
            text = data.decode("utf-8", errors="replace").strip()
            log_line(log_path, f"received from {addr[0]}:{addr[1]}: {text}")
            received += 1
        log_line(log_path, "done")
        return 0
    except socket.timeout:
        log_line(log_path, "timeout")
        return 2
    finally:
        try:
            s.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
