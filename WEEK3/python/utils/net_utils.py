#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Utilitati de Retea — Functii Helper Reutilizabile                           ║
║  Week 3 — Computer Networks                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Acest modul contine functii helper folosite in mai multe exemple.
"""
from __future__ import annotations

import socket
import struct
from datetime import datetime
from typing import Tuple, Optional


# ════════════════════════════════════════════════════════════════════════════
#  LOGGING
# ════════════════════════════════════════════════════════════════════════════

def timestamp() -> str:
    """Returns timestamp-ul curent in format HH:MM:SS.mmm"""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def log(level: str, message: str) -> None:
    """Disptoys a message with timestamp and level."""
    print(f"[{timestamp()}] [{level:5s}] {message}")


# ════════════════════════════════════════════════════════════════════════════
#  PARSING
# ════════════════════════════════════════════════════════════════════════════

def parse_address(addr_str: str, default_host: str = "0.0.0.0", default_port: int = 8080) -> Tuple[str, int]:
    """
    Parseaza un string de address in format host:port.
    
    Exemple:
        "192.168.1.1:8080" → ("192.168.1.1", 8080)
        "8080" → ("0.0.0.0", 8080)
        ":8080" → ("0.0.0.0", 8080)
        "localhost" → ("localhost", 8080)
    """
    if not addr_str:
        return default_host, default_port
    
    if ":" in addr_str:
        parts = addr_str.rsplit(":", 1)
        host = parts[0] or default_host
        port = int(parts[1]) if parts[1] else default_port
        return host, port
    
    # Doar port sau doar host?
    try:
        port = int(addr_str)
        return default_host, port
    except ValueError:
        return addr_str, default_port


# ════════════════════════════════════════════════════════════════════════════
#  VALIDARE IP
# ════════════════════════════════════════════════════════════════════════════

def is_valid_ipv4(ip: str) -> bool:
    """Check if string-ul este o address IPv4 valida."""
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def is_multicast_addr(ip: str) -> bool:
    """Check if address IP este in range-ul multicast (224.0.0.0 - 239.255.255.255)."""
    try:
        octets = list(map(int, ip.split(".")))
        return len(octets) == 4 and 224 <= octets[0] <= 239
    except (ValueError, IndexError):
        return False


def is_broadcast_addr(ip: str) -> bool:
    """Check if address este broadcast (255.255.255.255 sau x.x.x.255)."""
    return ip == "255.255.255.255" or ip.endswith(".255")


# ════════════════════════════════════════════════════════════════════════════
#  SOCKET HELPERS
# ════════════════════════════════════════════════════════════════════════════

def create_tcp_server(host: str, port: int, backlog: int = 10, reuse: bool = True) -> socket.socket:
    """Creeaza and configureaza un socket TCP server."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if reuse:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(backlog)
    return sock


def create_udp_socket(broadcast: bool = False, reuse: bool = True) -> socket.socket:
    """Creeaza and configureaza un socket UDP."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if reuse:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if broadcast:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    return sock


def create_multicast_receiver(group: str, port: int, iface: Optional[str] = None) -> socket.socket:
    """
    Creeaza un socket UDP care face JOIN to un group multicast.
    
    Args:
        group: Address grupului multicast (ex: "239.1.1.1")
        port: Portul de ascultare
        iface: Address IP a interfetei (optional)
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except AttributeError:
        pass
    
    sock.bind(("", port))
    
    # Join to group
    if iface:
        mreq = socket.inet_aton(group) + socket.inet_aton(iface)
    else:
        mreq = socket.inet_aton(group) + struct.pack("=I", socket.INADDR_ANY)
    
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    return sock


# ════════════════════════════════════════════════════════════════════════════
#  RECV HELPERS
# ════════════════════════════════════════════════════════════════════════════

def recv_exact(sock: socket.socket, n: int) -> bytes:
    """
    Receives EXACT n bytes din socket.
    Useful for protocoale with lungime fixa sau length-prefix.
    """
    buffer = b""
    while len(buffer) < n:
        remaining = n - len(buffer)
        chunk = sock.recv(remaining)
        if not chunk:
            raise ConnectionError(f"Connection closed. Received {len(buffer)}/{n} bytes.")
        buffer += chunk
    return buffer


def recv_until(sock: socket.socket, delimiter: bytes = b"\n", max_size: int = 65535) -> bytes:
    """
    Receives date pana to intalnirea delimitatorului.
    Returns datele FARA delimitator.
    """
    buffer = b""
    while delimiter not in buffer and len(buffer) < max_size:
        chunk = sock.recv(1)
        if not chunk:
            raise ConnectionError("Connection closed inainte de delimitator.")
        buffer += chunk
    
    if delimiter in buffer:
        message, _ = buffer.split(delimiter, 1)
        return message
    
    return buffer


def recv_length_prefixed(sock: socket.socket, header_size: int = 4, big_endian: bool = True) -> bytes:
    """
    Receives un mesaj with lungime prefixata.
    
    Args:
        sock: Socket TCP
        header_size: Dimensiunea header-ului (bytes)
        big_endian: True for big-endian, False for little-endian
    """
    fmt = ">" if big_endian else "<"
    if header_size == 1:
        fmt += "B"
    elif header_size == 2:
        fmt += "H"
    elif header_size == 4:
        fmt += "I"
    else:
        raise ValueError(f"Header size invalid: {header_size}")
    
    length_bytes = recv_exact(sock, header_size)
    length = struct.unpack(fmt, length_bytes)[0]
    
    return recv_exact(sock, length)


def send_length_prefixed(sock: socket.socket, data: bytes, header_size: int = 4, big_endian: bool = True) -> None:
    """
    sends a message with lungime prefixata.
    """
    fmt = ">" if big_endian else "<"
    if header_size == 1:
        fmt += "B"
    elif header_size == 2:
        fmt += "H"
    elif header_size == 4:
        fmt += "I"
    else:
        raise ValueError(f"Header size invalid: {header_size}")
    
    header = struct.pack(fmt, len(data))
    sock.sendall(header + data)


# ════════════════════════════════════════════════════════════════════════════
#  NETWORK INFO
# ════════════════════════════════════════════════════════════════════════════

def get_local_ip() -> str:
    """
    Determina address IP locala (non-loopback).
    Works through crearea unei connections UDP temporare.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Nu Sends nimic, doar determina interface de ieandre
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def get_hostname() -> str:
    """Returns hostname-ul local."""
    return socket.gethostname()


def resolve_hostname(hostname: str) -> str:
    """Rezolva un hostname to address IP."""
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return hostname


# ════════════════════════════════════════════════════════════════════════════
#  TEST
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=== Test net_utils ===")
    
    print(f"\nLocal IP: {get_local_ip()}")
    print(f"Hostname: {get_hostname()}")
    
    print(f"\nParse '192.168.1.1:8080': {parse_address('192.168.1.1:8080')}")
    print(f"Parse '8080': {parse_address('8080')}")
    print(f"Parse 'localhost': {parse_address('localhost')}")
    
    print(f"\nIs multicast '239.1.1.1': {is_multicast_addr('239.1.1.1')}")
    print(f"Is multicast '192.168.1.1': {is_multicast_addr('192.168.1.1')}")
    
    print(f"\nIs broadcast '255.255.255.255': {is_broadcast_addr('255.255.255.255')}")
    print(f"Is broadcast '192.168.1.255': {is_broadcast_addr('192.168.1.255')}")
