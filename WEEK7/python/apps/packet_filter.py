"""User space TCP proxy that acts as a simple filter.

This is an educational tool:
- it demonstrates interception in user space (application layer)
- it can allow or reject connections based on source IP allow or block lists

It is not a replacement for iptables based filtering.
"""

from __future__ import annotations

import argparse
import socket
import threading
import time
from pathlib import Path
from typing import Optional, Set


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="TCP proxy filter (Week 7).")
    p.add_argument("--listen-host", default="0.0.0.0", help="Proxy bind address (default: 0.0.0.0)")
    p.add_argument("--listen-port", type=int, default=8888, help="Proxy bind port (default: 8888)")
    p.add_argument("--upstream-host", required=True, help="Upstream server host")
    p.add_argument("--upstream-port", type=int, default=9090, help="Upstream server port (default: 9090)")
    p.add_argument("--allow", default="", help="Comma separated allowed source IPs (empty means allow all)")
    p.add_argument("--block", default="", help="Comma separated blocked source IPs (empty means block none)")
    p.add_argument("--log", default="", help="Optional log file path")
    p.add_argument("--timeout", type=float, default=5.0, help="Socket timeout in seconds (default: 5)")
    return p


def parse_ip_set(s: str) -> Set[str]:
    out: Set[str] = set()
    for part in s.split(","):
        part = part.strip()
        if part:
            out.add(part)
    return out


def log_line(path: Optional[Path], line: str) -> None:
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{stamp}] {line}"
    print(msg, flush=True)
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(msg + "\n")


def pipe(src: socket.socket, dst: socket.socket, buf: int = 4096) -> None:
    try:
        while True:
            data = src.recv(buf)
            if not data:
                break
            dst.sendall(data)
    except Exception:
        pass
    finally:
        try:
            dst.shutdown(socket.SHUT_WR)
        except Exception:
            pass


def handle(conn: socket.socket, addr: tuple[str, int], upstream: tuple[str, int], allow: Set[str], block: Set[str], log_path: Optional[Path], timeout: float) -> None:
    src_ip = addr[0]
    conn.settimeout(timeout)

    if src_ip in block or (allow and src_ip not in allow):
        log_line(log_path, f"blocked connection from {src_ip}:{addr[1]}")
        try:
            conn.close()
        except Exception:
            pass
        return

    log_line(log_path, f"allowed connection from {src_ip}:{addr[1]} to upstream {upstream[0]}:{upstream[1]}")

    up = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    up.settimeout(timeout)
    try:
        up.connect(upstream)
    except Exception as exc:
        log_line(log_path, f"upstream connect failed: {exc}")
        try:
            conn.close()
        except Exception:
            pass
        return

    t1 = threading.Thread(target=pipe, args=(conn, up), daemon=True)
    t2 = threading.Thread(target=pipe, args=(up, conn), daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    try:
        conn.close()
    except Exception:
        pass
    try:
        up.close()
    except Exception:
        pass

    log_line(log_path, f"connection closed for {src_ip}:{addr[1]}")


def main() -> int:
    args = build_parser().parse_args()
    allow = parse_ip_set(args.allow)
    block = parse_ip_set(args.block)
    log_path = Path(args.log) if args.log else None

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((args.listen_host, args.listen_port))
    srv.listen(50)

    upstream = (args.upstream_host, args.upstream_port)
    log_line(log_path, f"proxy listening on {args.listen_host}:{args.listen_port} forwarding to {upstream[0]}:{upstream[1]}")

    try:
        while True:
            conn, addr = srv.accept()
            th = threading.Thread(target=handle, args=(conn, addr, upstream, allow, block, log_path, args.timeout), daemon=True)
            th.start()
    except KeyboardInterrupt:
        log_line(log_path, "interrupted")
    finally:
        try:
            srv.close()
        except Exception:
            pass
        log_line(log_path, "proxy stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
