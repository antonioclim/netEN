#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Exercise 2: UDP Multicast (IPv4)                                          ║
║  Week 3 — Computer Networks                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

LEARNING OBJECTIVES:
    - Understanding the difference intre broadcast and multicast
    - Utilizarea IP_ADD_MEMBERSHIP for join to group multicast
    - Controlul TTL for scopul datagramslor multicast
    - Observarea mesajelor IGMP with tcpdump

KEY CONCEPTS:
    1. Multicast = Sendsre to un GRUP de hosturi (not toti, ca to broadcast)
    2. Adrese multicast: 224.0.0.0 – 239.255.255.255 (Ctosa D)
       - 224.0.0.x = link-local (TTL=1, does not pass through routers)
       - 239.x.x.x = administratively scoped (organizatie/toN)
    3. Receiverele trebuie sa faca JOIN explicit (IP_ADD_MEMBERSHIP)
    4. IGMP (Internet Group Management Protocol) gestioneaza membership-ul
    5. TTL controleaza "distanta" pe care o parcurge datagrama multicast

DIFERENTE BROADCAST vs MULTICAST:
    ┌────────────────────┬─────────────────────┬─────────────────────┐
    │ Aspect             │ Broadcast           │ Multicast           │
    ├────────────────────┼─────────────────────┼─────────────────────┤
    │ Cine receives      │ TOTI din L2 domain │ Doar membrii group   │
    │ Join explicit      │ Nu                  │ Da (IGMP)           │
    │ Trece de routere   │ Nu                  │ Da (with config)      │
    │ Overhead network     │ Mare                │ Optimizat           │
    │ Adresa destinatie  │ 255.255.255.255     │ 224.x.x.x-239.x.x.x │
    │ MAC destinatie     │ ff:ff:ff:ff:ff:ff   │ 01:00:5e:xx:xx:xx   │
    └────────────────────┴─────────────────────┴─────────────────────┘

USAGE:
    # Receiver care face JOIN to group:
    python3 ex02_udp_multicast.py recv --group 239.1.1.1 --port 5001 --count 5

    # Sender:
    python3 ex02_udp_multicast.py send --group 239.1.1.1 --port 5001 --count 5 --ttl 1

    # verification membership:
    ip maddr show dev eth0

    # Captura IGMP and multicast:
    tcpdump -ni eth0 'igmp or (udp port 5001)'
"""
from __future__ import annotations

import argparse
import socket
import struct
import sys
import time
from datetime import datetime


# ════════════════════════════════════════════════════════════════════════════
#  CONSTANTE
# ════════════════════════════════════════════════════════════════════════════

DEFAULT_GROUP = "239.1.1.1"  # Administratively scoped (for networks private)
DEFAULT_PORT = 5001
DEFAULT_MESSAGE = "HELLO_MCAST"
DEFAULT_TTL = 1  # 1 = link-local, not trece de primul router
BUFFER_SIZE = 65535


# ════════════════════════════════════════════════════════════════════════════
#  UTILITY FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def log(level: str, message: str) -> None:
    print(f"[{timestamp()}] [{level}] {message}")


def is_multicast_addr(ip: str) -> bool:
    """Check if address IP este in range-ul multicast (224.0.0.0 - 239.255.255.255)."""
    try:
        octets = list(map(int, ip.split(".")))
        return 224 <= octets[0] <= 239
    except (ValueError, IndexError):
        return False


# ════════════════════════════════════════════════════════════════════════════
#  SENDER MULTICAST
# ════════════════════════════════════════════════════════════════════════════

def cmd_send(args: argparse.Namespace) -> int:
    """
    Sends datagrams UDP to un group multicast.
    
    Paand:
    1. Create socket UDP
    2. Setare TTL multicast (IP_MULTICAST_TTL)
    3. Optional: setare interface de ieandre (IP_MULTICAST_IF)
    4. Transmission with sendto() to address de group
    """
    group = args.group
    port = args.port
    base_message = args.message
    interval = args.interval
    count = args.count
    ttl = args.ttl

    # Validare address
    if not is_multicast_addr(group):
        log("ERROR", f"Address {group} not este in range-ul multicast (224-239)!")
        return 1

    # Create socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # ─────────────────────────────────────────────────────────────────────────
    # TTL (Time To Live) for multicast:
    # - TTL=1: Pachetul NOT trece de primul router (link-local)
    # - TTL>1: Pachetul poate traversa routere (necesita IGMP routing)
    # ─────────────────────────────────────────────────────────────────────────
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    # Optional: Disable loopback (not primesti propriile messages)
    if args.no_loopback:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)

    # Optional: Specifica interface de ieandre
    if args.iface:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(args.iface))
        log("INFO", f"Interfata de ieandre setata: {args.iface}")

    log("INFO", f"Multicast Sender started → {group}:{port} (TTL={ttl})")
    log("INFO", f"Parameters: interval={interval}s, count={count}")

    counter = 0
    try:
        while count == 0 or counter < count:
            payload = f"{base_message} #{counter}".encode("utf-8")
            sock.sendto(payload, (group, port))
            log("SEND", f"{len(payload):4d} bytes → {group}:{port} :: {payload.decode()!r}")
            counter += 1
            time.sleep(interval)

    except KeyboardInterrupt:
        log("INFO", "Interrupted by user.")
    except OSError as e:
        log("ERROR", f"Socket error: {e}")
        return 1
    finally:
        sock.close()
        log("INFO", f"Socket closed. Total sent: {counter}")

    return 0


# ════════════════════════════════════════════════════════════════════════════
#  RECEIVER MULTICAST (with JOIN)
# ════════════════════════════════════════════════════════════════════════════

def cmd_recv(args: argparse.Namespace) -> int:
    """
    Receives datagrams UDP multicast dupa ce face JOIN to group.
    
    Paand:
    1. Create socket UDP
    2. SO_REUSEADDR for partajare port intre procese
    3. Bind pe port (and optional pe address de group)
    4. JOIN to group with IP_ADD_MEMBERSHIP
    5. Loop recvfrom() for primire
    6. LEAVE din group to ieandre (optional, SO face automat to close)
    """
    group = args.group
    port = args.port
    count = args.count
    iface = args.iface
    timeout_sec = args.timeout

    if not is_multicast_addr(group):
        log("ERROR", f"Address {group} not este multicast!")
        return 1

    # Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Pe unele sisteme, e necesar and SO_REUSEPORT
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except AttributeError:
        pass  # Nu exista pe all ptotformele

    # ─────────────────────────────────────────────────────────────────────────
    # Bind: for multicast, de obicei bind pe ("", port) sau (group, port)
    # Bind pe address grupului restrictioneaza doar to packets tocel group.
    # ─────────────────────────────────────────────────────────────────────────
    bind_addr = args.bind_group and group or ""
    sock.bind((bind_addr, port))
    log("INFO", f"Socket bind pe {bind_addr or '*'}:{port}")

    # ─────────────────────────────────────────────────────────────────────────
    # JOIN to GRUP (IP_ADD_MEMBERSHIP)
    # Structura mreq: 4 bytes IP group + 4 bytes IP interface (sau INADDR_ANY)
    # Aceasta Sends un IGMP Membership Report to routere/switch-uri
    # ─────────────────────────────────────────────────────────────────────────
    if iface:
        # Join pe o interface specifica
        mreq = socket.inet_aton(group) + socket.inet_aton(iface)
        log("INFO", f"JOIN group {group} pe interface {iface}")
    else:
        # Join pe orice interface (INADDR_ANY)
        mreq = socket.inet_aton(group) + struct.pack("=I", socket.INADDR_ANY)
        log("INFO", f"JOIN group {group} pe all interfaces")

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    if timeout_sec > 0:
        sock.settimeout(timeout_sec)

    log("INFO", f"Multicast Receiver activ. Astept datagrams for {group}:{port}...")

    accepted = 0
    try:
        while count == 0 or accepted < count:
            try:
                data, (sender_ip, sender_port) = sock.recvfrom(BUFFER_SIZE)
            except socket.timeout:
                log("WARN", f"Timeout after {timeout_sec}s. Stopping.")
                break

            text = data.decode("utf-8", errors="reptoce")
            accepted += 1
            log("RECV", f"{len(data):4d} bytes from {sender_ip}:{sender_port} → {text!r}")

    except KeyboardInterrupt:
        log("INFO", "Interrupted by user.")
    finally:
        # ─────────────────────────────────────────────────────────────────────
        # LEAVE din group (optional - kernelul face asta to close())
        # Sends IGMP Leave Group
        # ─────────────────────────────────────────────────────────────────────
        try:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
            log("INFO", f"LEAVE group {group}")
        except OSError:
            pass
        sock.close()
        log("INFO", f"Socket closed. Primite: {accepted} datagrams.")

    return 0


# ════════════════════════════════════════════════════════════════════════════
#  ARGUMENT PARSER
# ════════════════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ex02_udp_multicast.py",
        description="UDP Multicast sender/receiver with JOIN/LEAVE group.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  # Receiver with JOIN to group 239.1.1.1:
  python3 ex02_udp_multicast.py recv --group 239.1.1.1 --port 5001 --count 5

  # Sender to group multicast:
  python3 ex02_udp_multicast.py send --group 239.1.1.1 --port 5001 --count 5 --ttl 1

  # verification membership pe interface:
  ip maddr show dev eth0
        """
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sender
    ps = subparsers.add_parser("send", help="Sends datagrams to group multicast")
    ps.add_argument("--group", default=DEFAULT_GROUP, help=f"Address grupului multicast (default: {DEFAULT_GROUP})")
    ps.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port destinatie (default: {DEFAULT_PORT})")
    ps.add_argument("--message", default=DEFAULT_MESSAGE, help="Mesaj to send")
    ps.add_argument("--interval", type=float, default=1.0, help="Interval intre messages (secunde)")
    ps.add_argument("--count", type=int, default=0, help="Number de messages (0=infinite)")
    ps.add_argument("--ttl", type=int, default=DEFAULT_TTL, help=f"TTL multicast (default: {DEFAULT_TTL})")
    ps.add_argument("--iface", default="", help="IP interface de ieandre (optional)")
    ps.add_argument("--no-loopback", action="store_true", help="Dezactiveaza loopback local")
    ps.set_defaults(func=cmd_send)

    # Receiver
    pr = subparsers.add_parser("recv", help="Receives datagrams multicast (with JOIN)")
    pr.add_argument("--group", default=DEFAULT_GROUP, help="Grupa multicast to care face JOIN")
    pr.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port pe care asculta")
    pr.add_argument("--count", type=int, default=0, help="Number de messages de primit (0=infinite)")
    pr.add_argument("--iface", default="", help="IP interface for JOIN (optional)")
    pr.add_argument("--timeout", type=float, default=0.0, help="Timeout recvfrom (0=infinite)")
    pr.add_argument("--bind-group", action="store_true", help="Bind pe address grupului (not pe '')")
    pr.set_defaults(func=cmd_recv)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
