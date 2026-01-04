#!/usr/bin/env python3
"""
Exercise 11.02 – Minimal load balancer (reverse proxy), implemented in Python.

Educational objective:
- to see concretely what "accept, pick backend, forward, return response" means
- to implement distribution algorithms (round-robin, least_conn, ip_hash)
- to understand passive failover (similar to max_fails/fail_timeout in Nginx)

Note:
- the proxy is at simplified TCP/HTTP level (for common GET/HEAD).
- does not fully implement HTTP keep-alive/pipelining.

Usage (proxy):
  python3 ex_11_02.py --listen 0.0.0.0:8080 \
    --backends 10.0.0.2:8000,10.0.0.3:8000,10.0.0.4:8000 \
    --algo rr

Load generator (alternative to ab):
  python3 ex_11_02.py loadgen --url http://10.0.0.1:8080/ --n 200 --c 10
"""
from __future__ import annotations

import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import argparse
import socket
import threading
import time
import urllib.parse
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from python.utils.net_utils import (
    recv_until, parse_http_content_length, recv_exact, connect_tcp, set_timeouts, now_s
)

BUFFER_SIZE = 4096


@dataclass
class Backend:
    host: str
    port: int
    active: int = 0
    fails: int = 0
    down_until: float = 0.0

    def addr(self) -> Tuple[str, int]:
        return (self.host, self.port)

    def is_down(self, t: float) -> bool:
        return t < self.down_until


class LoadBalancer:
    def __init__(self,
                 backends: List[Backend],
                 algo: str,
                 passive_failures: int,
                 fail_timeout_s: float,
                 sock_timeout: float):
        self.backends = backends
        self.algo = algo
        self.passive_failures = passive_failures
        self.fail_timeout_s = fail_timeout_s
        self.sock_timeout = sock_timeout

        self._rr_idx = 0
        self._lock = threading.Lock()

    def _pick_rr(self, client_ip: str) -> Optional[Backend]:
        with self._lock:
            n = len(self.backends)
            for _ in range(n):
                b = self.backends[self._rr_idx]
                self._rr_idx = (self._rr_idx + 1) % n
                if not b.is_down(now_s()):
                    return b
        return None

    def _pick_least_conn(self, client_ip: str) -> Optional[Backend]:
        with self._lock:
            alive = [b for b in self.backends if not b.is_down(now_s())]
            if not alive:
                return None
            # tie-break: active, fails, then stable ordering
            alive.sort(key=lambda b: (b.active, b.fails, b.host, b.port))
            return alive[0]

    def _pick_ip_hash(self, client_ip: str) -> Optional[Backend]:
        with self._lock:
            alive = [b for b in self.backends if not b.is_down(now_s())]
            if not alive:
                return None
            h = 0
            for ch in client_ip:
                h = (h * 131 + ord(ch)) & 0xFFFFFFFF
            return alive[h % len(alive)]

    def pick(self, client_ip: str) -> Optional[Backend]:
        if self.algo == "rr":
            return self._pick_rr(client_ip)
        if self.algo == "least_conn":
            return self._pick_least_conn(client_ip)
        if self.algo == "ip_hash":
            return self._pick_ip_hash(client_ip)
        raise ValueError(f"Unknown algorithm: {self.algo}")

    def mark_success(self, b: Backend) -> None:
        with self._lock:
            b.fails = 0  # reset on success (simplification)

    def mark_failure(self, b: Backend) -> None:
        with self._lock:
            b.fails += 1
            if self.passive_failures > 0 and b.fails >= self.passive_failures:
                b.down_until = now_s() + self.fail_timeout_s

    def inc_active(self, b: Backend) -> None:
        with self._lock:
            b.active += 1

    def dec_active(self, b: Backend) -> None:
        with self._lock:
            b.active = max(0, b.active - 1)


def parse_backends(s: str) -> List[Backend]:
    out: List[Backend] = []
    for item in s.split(","):
        item = item.strip()
        if not item:
            continue
        host, port_s = item.split(":")
        out.append(Backend(host=host, port=int(port_s)))
    if not out:
        raise ValueError("Backend list is empty.")
    return out


def forward_one_request(client_sock: socket.socket,
                        client_addr: Tuple[str, int],
                        lb: LoadBalancer) -> None:
    """
    Read an HTTP request (headers + body if present) and forward it to backend.
    """
    client_ip = client_addr[0]
    set_timeouts(client_sock, lb.sock_timeout)

    req_head = recv_until(client_sock)
    if not req_head:
        return

    # Body (if present)
    content_len = parse_http_content_length(req_head)
    body = b""
    if content_len > 0:
        body = recv_exact(client_sock, content_len)

    request_data = req_head + body

    b = lb.pick(client_ip)
    if b is None:
        client_sock.sendall(b"HTTP/1.1 503 Service Unavailable\r\nConnection: close\r\n\r\nNo backends available\n")
        return

    lb.inc_active(b)
    try:
        # try 1 backend; on failure, try once more with another backend (simplified failover)
        for attempt in (1, 2):
            try:
                with connect_tcp(b.host, b.port, timeout=lb.sock_timeout) as be:
                    be.sendall(request_data)
                    response = b""
                    while True:
                        chunk = be.recv(BUFFER_SIZE)
                        if not chunk:
                            break
                        response += chunk
                        if len(response) > 5_000_000:
                            break
                    client_sock.sendall(response)
                    lb.mark_success(b)
                    return
            except Exception:
                lb.mark_failure(b)
                if attempt == 2:
                    client_sock.sendall(b"HTTP/1.1 502 Bad Gateway\r\nConnection: close\r\n\r\nBad Gateway\n")
                    return
                # pick another backend
                b = lb.pick(client_ip)
                if b is None:
                    client_sock.sendall(b"HTTP/1.1 503 Service Unavailable\r\nConnection: close\r\n\r\nNo backends available\n")
                    return
    finally:
        lb.dec_active(b)


def run_proxy(args: argparse.Namespace) -> None:
    backends = parse_backends(args.backends)
    lb = LoadBalancer(
        backends=backends,
        algo=args.algo,
        passive_failures=args.passive_failures,
        fail_timeout_s=args.fail_timeout,
        sock_timeout=args.sock_timeout,
    )

    host, port_s = args.listen.split(":")
    port = int(port_s)

    print(f"[LB] listen {host}:{port} | algo={args.algo} | backends={[(b.host,b.port) for b in backends]}")
    print(f"[LB] passive_failures={args.passive_failures} fail_timeout={args.fail_timeout}s sock_timeout={args.sock_timeout}s")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(128)

        while True:
            client_sock, client_addr = s.accept()
            t = threading.Thread(target=_handle_client, args=(client_sock, client_addr, lb), daemon=True)
            t.start()


def _handle_client(client_sock: socket.socket, client_addr, lb: LoadBalancer) -> None:
    try:
        forward_one_request(client_sock, client_addr, lb)
    except Exception as e:
        try:
            client_sock.sendall(b"HTTP/1.1 500 Internal Server Error\r\nConnection: close\r\n\r\nInternal Error\n")
        except Exception:
            pass
    finally:
        try:
            client_sock.close()
        except Exception:
            pass


# -------------------- Load generator -------------------- #
def http_get_once(url: str, timeout: float = 2.5) -> Tuple[int, float]:
    """
    Returns (status_code, latency_s). Minimal HTTP/1.1 implementation.
    """
    u = urllib.parse.urlparse(url)
    host = u.hostname or "127.0.0.1"
    port = u.port or (443 if u.scheme == "https" else 80)
    path = u.path or "/"
    if u.query:
        path += "?" + u.query

    t0 = time.time()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        s.connect((host, port))
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"User-Agent: s11-loadgen/0.1\r\n"
            f"Connection: close\r\n\r\n"
        ).encode("ascii", errors="replace")
        s.sendall(req)
        head = recv_until(s, max_bytes=65536)
        # status line
        status = 0
        try:
            line = head.split(b"\r\n", 1)[0].decode("ascii", errors="replace")
            status = int(line.split()[1])
        except Exception:
            status = 0
        # consume the rest (we don't care)
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
    return status, (time.time() - t0)


def run_loadgen(args: argparse.Namespace) -> None:
    url = args.url
    n = args.n
    c = args.c
    timeout = args.timeout

    latencies: List[float] = []
    statuses: Dict[int, int] = {}
    lock = threading.Lock()

    start = time.time()
    counter = {"sent": 0}

    def worker():
        while True:
            with lock:
                if counter["sent"] >= n:
                    return
                counter["sent"] += 1
            st, lat = http_get_once(url, timeout=timeout)
            with lock:
                latencies.append(lat)
                statuses[st] = statuses.get(st, 0) + 1

    threads = [threading.Thread(target=worker) for _ in range(c)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    dur = time.time() - start
    latencies_sorted = sorted(latencies)

    def pct(p: float) -> float:
        if not latencies_sorted:
            return 0.0
        idx = int((p / 100.0) * (len(latencies_sorted) - 1))
        return latencies_sorted[idx]

    ok = statuses.get(200, 0)
    rps = (n / dur) if dur > 0 else 0.0

    print(f"[loadgen] url={url}")
    print(f"[loadgen] n={n} c={c} duration={dur:.3f}s rps={rps:.2f}")
    print(f"[loadgen] status_counts={dict(sorted(statuses.items(), key=lambda kv: kv[0]))}")
    print(f"[loadgen] latency_s: p50={pct(50):.4f} p90={pct(90):.4f} p95={pct(95):.4f} p99={pct(99):.4f}")


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")

    # proxy
    p.add_argument("--listen", type=str, default="0.0.0.0:8080")
    p.add_argument("--backends", type=str, required=False, default="127.0.0.1:8001,127.0.0.1:8002,127.0.0.1:8003")
    p.add_argument("--algo", type=str, choices=["rr", "least_conn", "ip_hash"], default="rr")
    p.add_argument("--passive-failures", type=int, default=1)
    p.add_argument("--fail-timeout", type=float, default=10.0)
    p.add_argument("--sock-timeout", type=float, default=2.5)

    # loadgen
    p_lg = sub.add_parser("loadgen")
    p_lg.add_argument("--url", type=str, required=True)
    p_lg.add_argument("--n", type=int, default=200)
    p_lg.add_argument("--c", type=int, default=10)
    p_lg.add_argument("--timeout", type=float, default=2.5)

    return p


def main() -> None:
    p = build_argparser()
    args = p.parse_args()

    if args.cmd == "loadgen":
        run_loadgen(args)
        return

    run_proxy(args)


if __name__ == "__main__":
    main()
