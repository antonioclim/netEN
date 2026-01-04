"""UDP sender for Week 7 demos."""

from __future__ import annotations

import argparse
import socket
import time
from pathlib import Path
from typing import Optional


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Simple UDP sender (Week 7).")
    p.add_argument("--host", required=True, help="Destination address or name")
    p.add_argument("--port", type=int, default=9091, help="Destination port (default: 9091)")
    p.add_argument("--message", default="hello", help="Message to send (default: hello)")
    p.add_argument("--count", type=int, default=1, help="Number of datagrams to send (default: 1)")
    p.add_argument("--delay", type=float, default=0.1, help="Delay between sends in seconds (default: 0.1)")
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
    payload = (args.message + "\n").encode("utf-8")
    for i in range(args.count):
        s.sendto(payload, (args.host, args.port))
        log_line(log_path, f"sent datagram {i+1}/{args.count} to {args.host}:{args.port}")
        time.sleep(args.delay)
    try:
        s.close()
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
