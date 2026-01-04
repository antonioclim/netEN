"""Defensive port probe for Week 7.

This is intentionally limited:
- it probes a small list of ports you provide
- it is meant only for the local lab network created by this kit
"""

from __future__ import annotations

import argparse
import socket
import time
from pathlib import Path
from typing import Optional


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Defensive TCP port probe (Week 7).")
    p.add_argument("--host", required=True, help="Target host (lab only)")
    p.add_argument("--ports", required=True, help="Comma separated list, for example: 22,80,9090")
    p.add_argument("--timeout", type=float, default=0.5, help="Timeout in seconds (default: 0.5)")
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


def probe(host: str, port: int, timeout: float) -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        r = s.connect_ex((host, port))
        if r == 0:
            return "open"
        return f"closed ({r})"
    except socket.timeout:
        return "timeout"
    except Exception as exc:
        return f"error ({exc})"
    finally:
        try:
            s.close()
        except Exception:
            pass


def main() -> int:
    args = build_parser().parse_args()
    log_path = Path(args.log) if args.log else None
    ports = []
    for part in args.ports.split(","):
        part = part.strip()
        if not part:
            continue
        ports.append(int(part))

    log_line(log_path, f"probing {args.host} ports: {', '.join(str(p) for p in ports)}")
    for port in ports:
        status = probe(args.host, port, args.timeout)
        log_line(log_path, f"{args.host}:{port} -> {status}")

    log_line(log_path, "done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
