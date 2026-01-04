#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
 Week 2 – Exercise 1: Concurrent TCP server and client
═══════════════════════════════════════════════════════════════════════════════

 LEARNING OBJECTIVES:
 ────────────────────
 1. Understanding sockets for TCP (SOCK_STREAM)
 2. Difference: iterative server vs. concurrent server (threading)
 3. Correlating handshake TCP (SYN-SYN/ACK-ACK) with the code
 4. Observing encapsulation: data → TCP segment → IP packet

 APPLICATION PROTOCOL:
 ──────────────────
 Request:  <text message> (bytes)
 Response: b"OK: " + upper(message)

 USAGE:
   server:  python3 ex_2_01_tcp.py server --port 9999
   client:  python3 ex_2_01_tcp.py client --host 127.0.0.1 --port 9999 -m "test"
   Load:    python3 ex_2_01_tcp.py load --host 127.0.0.1 --port 9999 --clients 10
═══════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
import argparse
import socket
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

# =============================================================================
# CONSTANTS
# =============================================================================
DEFAULT_PORT = 9090
DEFAULT_BIND = "0.0.0.0"
DEFAULT_BACKLOG = 32
DEFAULT_RECV_BUF = 1024
DEFAULT_TIMEOUT = 5.0


def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def log(tag: str, msg: str) -> None:
    print(f"[{timestamp()}][{tag}] {msg}", flush=True)


@dataclass
class ServerConfig:
    bind: str = DEFAULT_BIND
    port: int = DEFAULT_PORT
    backlog: int = DEFAULT_BACKLOG
    recv_buf: int = DEFAULT_RECV_BUF
    mode: str = "threaded"


# =============================================================================
# HANDLER client
# =============================================================================
def handle_client(conn: socket.socket, addr: tuple[str, int], recv_buf: int) -> None:
    """processes connectiona TCP of at client."""
    client_ip, client_port = addr
    thread_name = threading.current_thread().name
    
    try:
        data = conn.recv(recv_buf)
        if not data:
            log(thread_name, f"{client_ip}:{client_port} disconnected")
            return
        
        data_clean = data.rstrip(b"\r\n")
        response = b"OK: " + data_clean.upper()
        
        log(thread_name, f"RX {len(data):4d}B of at {client_ip}:{client_port}: {data_clean!r}")
        conn.sendall(response)
        log(thread_name, f"TX {len(response):4d}B to {client_ip}:{client_port}: {response!r}")
        
    except Exception as exc:
        log(thread_name, f"error {client_ip}:{client_port}: {exc}")
    finally:
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        conn.close()


# =============================================================================
# server
# =============================================================================
def run_server(cfg: ServerConfig) -> None:
    """starts serverul TCP."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((cfg.bind, cfg.port))
    sock.listen(cfg.backlog)
    
    log("server", f"TCP on {cfg.bind}:{cfg.port} | mod={cfg.mode}")
    log("server", "waiting connections... (Ctrl+C stopping)")
    
    try:
        while True:
            conn, addr = sock.accept()
            log("MAIN", f"connection new: {addr[0]}:{addr[1]}")
            
            if cfg.mode == "iterative":
                handle_client(conn, addr, cfg.recv_buf)
            else:
                t = threading.Thread(
                    target=handle_client,
                    args=(conn, addr, cfg.recv_buf),
                    daemon=True,
                    name=f"Worker-{addr[1]}"
                )
                t.start()
    except KeyboardInterrupt:
        log("server", "stopping (Ctrl+C)")
    finally:
        sock.close()


# =============================================================================
# client
# =============================================================================
def tcp_client(host: str, port: int, message: bytes, timeout: float) -> Optional[bytes]:
    """client TCP simplu."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            t0 = time.perf_counter()
            sock.connect((host, port))
            sock.sendall(message)
            response = sock.recv(4096)
            rtt = (time.perf_counter() - t0) * 1000
            log("client", f"RX {len(response)}B in {rtt:.1f}ms: {response!r}")
            return response
    except socket.timeout:
        log("client", f"TIMEOUT {host}:{port}")
    except ConnectionRefusedError:
        log("client", f"connection refuzata {host}:{port}")
    except Exception as exc:
        log("client", f"error: {exc}")
    return None


def run_load_test(host: str, port: int, num_clients: int, message: bytes,
                  timeout: float, stagger_ms: int) -> None:
    """Test of incarcare with N clients concurenti."""
    log("LOAD", f"Start: {num_clients} clients → {host}:{port}")
    
    results: List[Optional[bytes]] = [None] * num_clients
    
    def worker(i: int) -> None:
        results[i] = tcp_client(host, port, message, timeout)
    
    threads = []
    t0 = time.perf_counter()
    
    for i in range(num_clients):
        t = threading.Thread(target=worker, args=(i,))
        t.start()
        threads.append(t)
        if stagger_ms > 0:
            time.sleep(stagger_ms / 1000)
    
    for t in threads:
        t.join()
    
    duration = (time.perf_counter() - t0) * 1000
    ok = sum(1 for r in results if r)
    log("LOAD", f"result: {ok}/{num_clients} in {duration:.0f}ms")


# =============================================================================
# CLI
# =============================================================================
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="S2 – server/client TCP")
    sub = p.add_subparsers(dest="cmd", required=True)
    
    # server
    ps = sub.add_parser("server")
    ps.add_argument("--bind", default=DEFAULT_BIND)
    ps.add_argument("--port", type=int, default=DEFAULT_PORT)
    ps.add_argument("--backlog", type=int, default=DEFAULT_BACKLOG)
    ps.add_argument("--recv-buf", type=int, default=DEFAULT_RECV_BUF)
    ps.add_argument("--mode", choices=["threaded", "iterative"], default="threaded")
    
    # client
    pc = sub.add_parser("client")
    pc.add_argument("--host", required=True)
    pc.add_argument("--port", type=int, required=True)
    pc.add_argument("--message", "-m", required=True)
    pc.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    
    # Load
    pl = sub.add_parser("load")
    pl.add_argument("--host", required=True)
    pl.add_argument("--port", type=int, required=True)
    pl.add_argument("--clients", "-n", type=int, default=10)
    pl.add_argument("--message", "-m", default="ping")
    pl.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    pl.add_argument("--stagger-ms", type=int, default=50)
    
    return p.parse_args()


def main() -> int:
    args = parse_args()
    
    if args.cmd == "server":
        run_server(ServerConfig(
            bind=args.bind, port=args.port, backlog=args.backlog,
            recv_buf=args.recv_buf, mode=args.mode
        ))
    elif args.cmd == "client":
        r = tcp_client(args.host, args.port, args.message.encode(), args.timeout)
        return 0 if r else 1
    elif args.cmd == "load":
        run_load_test(args.host, args.port, args.clients,
                      args.message.encode(), args.timeout, args.stagger_ms)
    return 0


if __name__ == "__main__":
    sys.exit(main())
