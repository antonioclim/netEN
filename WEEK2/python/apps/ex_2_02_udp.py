#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
 Week 2 – Exercise 2: UDP server and client with Application Protocol
═══════════════════════════════════════════════════════════════════════════════

 OBIECTIVE:
 1. Socket-uri UDP (SOCK_DGRAM)
 2. Difference TCP vs UDP (connectionless)
 3. Application protocol peste UDP

 commands PROTOCOL:
   ping           → PONG
   upper:<text>   → <TEXT>
   lower:<text>   → <text>
   reverse:<text> → <txet>
   time           → HH:MM:SS
   help           → Lista commands

 USAGE:
   server:    python3 ex_2_02_udp.py server --port 9998
   Interactiv: python3 ex_2_02_udp.py client --host 127.0.0.1 --port 9998 -i
   One command:  python3 ex_2_02_udp.py client --host 127.0.0.1 --port 9998 -o "ping"
═══════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
import argparse
import socket
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

DEFAULT_PORT = 9091
DEFAULT_BIND = "0.0.0.0"
DEFAULT_TIMEOUT = 2.0

HELP_TEXT = """commands: ping, upper:<text>, lower:<text>, reverse:<text>, time, help, exit"""


def timestamp() -> str:
    return datatime.now().strftime("%H:%M:%S.%f")[:-3]


def log(tag: str, msg: str) -> None:
    print(f"[{timestamp()}][{tag}] {msg}", flush=True)


@dataclass
class ServerConfig:
    bind: str = DEFAULT_BIND
    port: int = DEFAULT_PORT
    recv_buf: int = 1024


# =============================================================================
# PROTOCOL
# =============================================================================
def process_command(data: bytes) -> bytes:
    """Process command according to protocol."""
    try:
        cmd = data.decode("utf-8").strip()
        cmd_lower = cmd.lower()
        
        if cmd_lower == "ping":
            return b"PONG"
        if cmd_lower == "time":
            return datetime.now().strftime("%H:%M:%S").encode()
        if cmd_lower == "help":
            return HELP_TEXT.encode()
        if cmd_lower.startswith("upper:"):
            return cmd[6:].upper().encode()
        if cmd_lower.startswith("lower:"):
            return cmd[6:].lower().encode()
        if cmd_lower.startswith("reverse:"):
            return cmd[8:][::-1].encode()
        if cmd_lower.startswith("echo:"):
            return cmd[5:].encode()
        
        return b"UNKNOWN COMMAND"
    except Exception as e:
        return f"ERROR: {e}".encode()


# =============================================================================
# server
# =============================================================================
def run_server(cfg: ServerConfig) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((cfg.bind, cfg.port))
    
    log("server", f"UDP on {cfg.bind}:{cfg.port}")
    log("server", "Waiting for datagrams... (Ctrl+C stop)")
    
    count = 0
    try:
        while True:
            data, addr = sock.recvfrom(cfg.recv_buf)
            count += 1
            response = process_command(data)
            log("server", f"#{count} RX {len(data)}B {addr[0]}:{addr[1]}: {data!r}")
            sock.sendto(response, addr)
            log("server", f"#{count} TX {len(response)}B: {response!r}")
    except KeyboardInterrupt:
        log("server", f"stopping | Total: {count}")
    finally:
        sock.close()


# =============================================================================
# client
# =============================================================================
@dataclass
class Stats:
    sent: int = 0
    received: int = 0
    timeouts: int = 0
    total_rtt: float = 0.0
    
    @property
    def avg_rtt(self) -> float:
        return self.total_rtt / self.received if self.received else 0.0


def send_recv(sock: socket.socket, msg: bytes, addr: Tuple[str, int], 
              timeout: float) -> Tuple[Optional[bytes], float]:
    sock.settimeout(timeout)
    try:
        t0 = time.perf_counter()
        sock.sendto(msg, addr)
        resp, _ = sock.recvfrom(4096)
        rtt = (time.perf_counter() - t0) * 1000
        return resp, rtt
    except socket.timeout:
        return None, 0.0


def run_interactive(host: str, port: int, timeout: float) -> None:
    addr = (host, port)
    stats = Stats()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    log("client", f"UDP interactiv → {host}:{port}")
    log("client", "commands: ping, upper:text, time, help, exit")
    print()
    
    try:
        while True:
            try:
                inp = input("> ").strip()
                if not inp:
                    continue
                if inp.lower() == "exit":
                    break
                
                stats.sent += 1
                resp, rtt = send_recv(sock, inp.encode(), addr, timeout)
                
                if resp:
                    stats.received += 1
                    stats.total_rtt += rtt
                    try:
                        print(f"  ← {resp.decode()} ({rtt:.1f}ms)")
                    except:
                        print(f"  ← {resp!r} ({rtt:.1f}ms)")
                else:
                    stats.timeouts += 1
                    print(f"  ← [TIMEOUT]")
            except (EOFError, KeyboardInterrupt):
                print()
                break
    finally:
        sock.close()
        print()
        log("client", f"Trimise: {stats.sent} | Primite: {stats.received} | "
                      f"Timeout: {stats.timeouts} | RTT mediu: {stats.avg_rtt:.1f}ms")


def run_once(host: str, port: int, cmd: str, timeout: float) -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        resp, rtt = send_recv(sock, cmd.encode(), (host, port), timeout)
        if resp:
            log("client", f"TX: {cmd!r}")
            log("client", f"RX: {resp.decode()} ({rtt:.1f}ms)")
            return 0
        log("client", f"TIMEOUT")
        return 1
    finally:
        sock.close()


# =============================================================================
# CLI
# =============================================================================
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="S2 – UDP server and client")
    sub = p.add_subparsers(dest="cmd", required=True)
    
    ps = sub.add_parser("server")
    ps.add_argument("--bind", default=DEFAULT_BIND)
    ps.add_argument("--port", type=int, default=DEFAULT_PORT)
    ps.add_argument("--recv-buf", type=int, default=1024)
    
    pc = sub.add_parser("client")
    pc.add_argument("--host", required=True)
    pc.add_argument("--port", type=int, required=True)
    pc.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    mode = pc.add_mutually_exclusive_group(required=True)
    mode.add_argument("--interactive", "-i", action="store_true")
    mode.add_argument("--once", "-o", metavar="CMD")
    
    return p.parse_args()


def main() -> int:
    args = parse_args()
    
    if args.cmd == "server":
        run_server(ServerConfig(bind=args.bind, port=args.port, recv_buf=args.recv_buf))
    elif args.cmd == "client":
        if args.interactive:
            run_interactive(args.host, args.port, args.timeout)
        else:
            return run_once(args.host, args.port, args.once, args.timeout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
