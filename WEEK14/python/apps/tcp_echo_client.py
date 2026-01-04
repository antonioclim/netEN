#!/usr/bin/env python3
"""tcp_echo_client.py — TCP echo client for demonstrations.

Features:
  - Connects to a TCP server
  - Sends a message and verifies the echo
  - Reports latency and validity

Usage:
  python3 tcp_echo_client.py --host 10.0.0.2 --port 9000 --message "hello"
"""

from __future__ import annotations

import argparse
import socket
import sys
import time
from datetime import datetime


def log(msg: str) -> None:
    """Logging with timestamp."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{ts}] [echo-client] {msg}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TCP Echo Client")
    parser.add_argument("--host", required=True, help="Server address")
    parser.add_argument("--port", type=int, default=9000, help="Server port")
    parser.add_argument("--message", default="hello", help="Message to send")
    parser.add_argument("--timeout", type=float, default=5.0, help="Timeout (s)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    
    log(f"Connecting to {args.host}:{args.port}...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(args.timeout)
    
    try:
        start = time.time()
        sock.connect((args.host, args.port))
        connect_time = (time.time() - start) * 1000
        log(f"Connected (connect time: {connect_time:.2f} ms)")
        
        message = args.message.encode("utf-8")
        log(f"Sending: {message!r}")
        
        start = time.time()
        sock.sendall(message)
        
        response = sock.recv(4096)
        rtt = (time.time() - start) * 1000
        
        log(f"Received: {response!r}")
        log(f"RTT: {rtt:.2f} ms")
        
        if response == message:
            log("✓ Echo valid")
            return 0
        else:
            log("✗ Echo mismatch!")
            return 1
    
    except socket.timeout:
        log("✗ Connection timeout")
        return 1
    except ConnectionRefusedError:
        log("✗ Connection refused")
        return 1
    except Exception as e:
        log(f"✗ Error: {e}")
        return 1
    finally:
        sock.close()


if __name__ == "__main__":
    raise SystemExit(main())
