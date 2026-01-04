#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Exercise 1: UDP Broadcast (IPv4)                                          ║
║  Week 3 — Computer Networks                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

LEARNING OBJECTIVES:
    - Understanding the difference unicast vs broadcast at IP level
    - Using the option SO_BROADCAST on the UDP socket
    - Observing the behaviour "one-to-all" in an L2 domain
    - Capture and analysis of traffic broadcast with tcpdump

KEY CONCEPTS:
    1. Broadcast = sending to ALL hosts in a domain broadcast (L2)
    2. Address 255.255.255.255 = "limited broadcast" (does not pass through routers)
    3. Address x.x.x.255 = "directed broadcast" (for a specific subnet)
    4. SO_BROADCAST = ftog mandatory on socket to allow broadcast

USAGE:
    # Receiver (on h2 and h3):
    python3 ex01_udp_broadcast.py recv --port 5007 --count 5

    # Sender (on h1):
    python3 ex01_udp_broadcast.py send --dst 255.255.255.255 --port 5007 --count 5

    # Traffic capture (on h3):
    tcpdump -ni h3-eth0 'udp port 5007'

IMPORTANT NOTES:
    - Broadcast does NOT pass through routers (is limited to the domain L2)
    - All hosts in the domain receive the frame at L2 level, regardless of whether
      they listen on that port or not (saturates the network)
    - It is inefficient at torge scale → multicast or unicast is preferred
"""
from __future__ import annotations

import argparse
import socket
import sys
import time
from datetime import datetime
from typing import Callable


# ════════════════════════════════════════════════════════════════════════════
#  CONSTANTS AND CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════

DEFAULT_BROADCAST_ADDR = "255.255.255.255"
DEFAULT_PORT = 5007
DEFAULT_MESSAGE = "HELLO_BCAST"
DEFAULT_INTERVAL = 1.0
BUFFER_SIZE = 65535


# ════════════════════════════════════════════════════════════════════════════
#  UTILITY FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

def timestamp() -> str:
    """Returns the current timestamp in human-readable format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def log(level: str, message: str) -> None:
    """Disptoys a message with timestamp and level."""
    print(f"[{timestamp()}] [{level}] {message}")


# ════════════════════════════════════════════════════════════════════════════
#  SENDER: Transmission UDP Broadcast
# ════════════════════════════════════════════════════════════════════════════

def cmd_send(args: argparse.Namespace) -> int:
    """
    Sends datagrams UDP to address broadcast.
    
    Paand:
    1. Create socket UDP (SOCK_DGRAM)
    2. Enable SO_BROADCAST (mandatory!)
    3. Transmission periodica with sendto()
    
    Args:
        args: Parsed arguments (dst, port, message, interval, count, bind)
    
    Returns:
        0 for success, 1 for error
    """
    dst = args.dst
    port = args.port
    base_message = args.message
    interval = args.interval
    count = args.count

    # ─────────────────────────────────────────────────────────────────────────
    # Step 1: Create socket UDP
    # ─────────────────────────────────────────────────────────────────────────
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # ─────────────────────────────────────────────────────────────────────────
    # Step 2: Enable SO_BROADCAST
    # CRITIC: Without this option, sendto() to address broadcast will fail
    #         with PermissionError sau "Operation not permitted" on most OS.
    # ─────────────────────────────────────────────────────────────────────────
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Optional: bind pe o interface specifica (useful when ai mai multe interfaces)
    if args.bind:
        sock.bind((args.bind, 0))
        log("INFO", f"Socket bound de interface: {args.bind}")

    log("INFO", f"UDP Broadcast Sender started → {dst}:{port}")
    log("INFO", f"Parameters: interval={interval}s, count={count} (0=infinite)")

    counter = 0
    try:
        while count == 0 or counter < count:
            # Build payload-ul with numar de secventa
            payload = f"{base_message} #{counter}".encode("utf-8")

            # ─────────────────────────────────────────────────────────────────
            # Step 3: Transmission datagrama
            # sendto() specifica destinatia for fiecare datagrama (UDP e
            # connectionless, deci not exista "conexiune" persistenta).
            # ─────────────────────────────────────────────────────────────────
            sock.sendto(payload, (dst, port))
            log("SEND", f"{len(payload):4d} bytes → {dst}:{port} :: {payload.decode()!r}")

            counter += 1
            time.sleep(interval)

    except KeyboardInterrupt:
        log("INFO", "Interrupted by user (Ctrl+C).")
    except OSError as e:
        log("ERROR", f"Socket error: {e}")
        return 1
    finally:
        sock.close()
        log("INFO", f"Socket closed. Total sent: {counter} datagrams.")

    return 0


# ════════════════════════════════════════════════════════════════════════════
#  RECEIVER: Reception UDP Broadcast
# ════════════════════════════════════════════════════════════════════════════

def cmd_recv(args: argparse.Namespace) -> int:
    """
    Receives datagrams UDP (inclusiv broadcast).
    
    Paand:
    1. Create socket UDP
    2. Enable SO_REUSEADDR (for quick restart in tob)
    3. Bind pe port (and optional pe o address specifica)
    4. Loop recvfrom() for primire datagrams
    
    Args:
        args: Parsed arguments (bind_addr, port, count, prefix, timeout)
    
    Returns:
        0 for success
    """
    bind_addr = args.bind_addr
    port = args.port
    count = args.count
    prefix = args.prefix
    timeout_sec = args.timeout

    # ─────────────────────────────────────────────────────────────────────────
    # Step 1: Create socket UDP
    # ─────────────────────────────────────────────────────────────────────────
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # ─────────────────────────────────────────────────────────────────────────
    # Step 2: SO_REUSEADDR allows port reuse immediately after closing.
    # Useful in tob cand reporniti frecvent programul.
    # ─────────────────────────────────────────────────────────────────────────
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # ─────────────────────────────────────────────────────────────────────────
    # Step 3: Bind pe address and port
    # bind_addr="" (string gol) = INADDR_ANY = asculta pe all interfaces
    # This is necessary to receive broadcast!
    # ─────────────────────────────────────────────────────────────────────────
    sock.bind((bind_addr, port))

    # Optional: timeout to avoid blocking indefinitelye
    if timeout_sec > 0:
        sock.settimeout(timeout_sec)

    log("INFO", f"UDP Broadcast Receiver started pe {bind_addr or '*'}:{port}")
    log("INFO", f"Parameters: count={count} (0=infinite), prefix={prefix!r}, timeout={timeout_sec}s")

    accepted = 0
    total = 0

    try:
        while count == 0 or accepted < count:
            try:
                # ─────────────────────────────────────────────────────────────
                # Step 4: recvfrom() - blocks until receives o datagrama
                # Returns (data, (ip_sursa, port_sursa))
                # ─────────────────────────────────────────────────────────────
                data, (sender_ip, sender_port) = sock.recvfrom(BUFFER_SIZE)
            except socket.timeout:
                log("WARN", f"Timeout after {timeout_sec}s without data. Stopping.")
                break

            total += 1
            text = data.decode("utf-8", errors="replace")

            # Filtering optional by prefix
            if prefix and not text.startswith(prefix):
                log("SKIP", f"From {sender_ip}:{sender_port} → {text!r} (does not start with {prefix!r})")
                continue

            accepted += 1
            log("RECV", f"{len(data):4d} bytes from {sender_ip}:{sender_port} → {text!r}")

    except KeyboardInterrupt:
        log("INFO", "Interrupted by user (Ctrl+C).")
    finally:
        sock.close()
        log("INFO", f"Socket closed. Accepted: {accepted}/{total} datagrams.")

    return 0


# ════════════════════════════════════════════════════════════════════════════
#  ARGUMENT PARSER
# ════════════════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    """Builds the argument parser with subcomenzile send and recv."""
    parser = argparse.ArgumentParser(
        prog="ex01_udp_broadcast.py",
        description="UDP Broadcast sender/receiver for demonstrations de network.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  # Starting receiver on port 5007, receives 5 messages:
  python3 ex01_udp_broadcast.py recv --port 5007 --count 5

  # Starting sender to broadcast, 5 messages, interval 0.5s:
  python3 ex01_udp_broadcast.py send --dst 255.255.255.255 --port 5007 --count 5 --interval 0.5
        """
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="Command to execute")

    # ─────────────────────────────────────────────────────────────────────────
    # Subcommand: send
    # ─────────────────────────────────────────────────────────────────────────
    parser_send = subparsers.add_parser("send", help="Sends datagrams UDP broadcast")
    parser_send.add_argument(
        "--dst", default=DEFAULT_BROADCAST_ADDR,
        help=f"Destination broadcast address (default: {DEFAULT_BROADCAST_ADDR})"
    )
    parser_send.add_argument(
        "--port", type=int, default=DEFAULT_PORT,
        help=f"Destination UDP port (default: {DEFAULT_PORT})"
    )
    parser_send.add_argument(
        "--message", default=DEFAULT_MESSAGE,
        help=f"Message to send (default: {DEFAULT_MESSAGE})"
    )
    parser_send.add_argument(
        "--interval", type=float, default=DEFAULT_INTERVAL,
        help=f"Interval intre datagrams in seconds (default: {DEFAULT_INTERVAL})"
    )
    parser_send.add_argument(
        "--count", type=int, default=0,
        help="Number de datagrams to send (0 = infinite)"
    )
    parser_send.add_argument(
        "--bind", default="",
        help="Local IP address to bind (optional, for multi-homed hosts)"
    )
    parser_send.set_defaults(func=cmd_send)

    # ─────────────────────────────────────────────────────────────────────────
    # Subcommand: recv
    # ─────────────────────────────────────────────────────────────────────────
    parser_recv = subparsers.add_parser("recv", help="Receives datagrams UDP broadcast")
    parser_recv.add_argument(
        "--bind-addr", default="",
        help="Address to bind (default: '' = all interfaces)"
    )
    parser_recv.add_argument(
        "--port", type=int, default=DEFAULT_PORT,
        help=f"UDP port to listen on (default: {DEFAULT_PORT})"
    )
    parser_recv.add_argument(
        "--count", type=int, default=0,
        help="Number of messages to accept (0 = infinite)"
    )
    parser_recv.add_argument(
        "--prefix", default="",
        help="Filtering: accept only messages starting with this prefix"
    )
    parser_recv.add_argument(
        "--timeout", type=float, default=0.0,
        help="Socket timeout in seconds (0 = no timeout)"
    )
    parser_recv.set_defaults(func=cmd_recv)

    return parser


# ════════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════════

def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
