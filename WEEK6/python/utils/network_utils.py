#!/usr/bin/env python3
"""
Common utilities for network applications - Week 6

This module consolidates common functionalities to avoid
code duplication between different client-server applications.

Week 6 Port Plan:
    TCP_APP_PORT = 9090
    UDP_APP_PORT = 9091
    WEEK_PORT_BASE = 5600 (for custom ports)
    WEEK_PORT_RANGE = 5600..5699

Week 6 IP Plan:
    SUBNET = 10.0.6.0/24
    GATEWAY = 10.0.6.1
    H1 = 10.0.6.11
    H2 = 10.0.6.12
    H3 = 10.0.6.13
    SERVER = 10.0.6.100

Rezolvix&Hypotheticalandrei | MIT License | ASE-CSIE 2025-2026
"""

from __future__ import annotations

import logging
import socket
import sys
from dataclasses import dataclass
from typing import Optional


# ═══════════════════════════════════════════════════════════════════════════
# WEEK 6 CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

WEEK = 6

# IP Plan
SUBNET = f"10.0.{WEEK}.0/24"
GATEWAY = f"10.0.{WEEK}.1"
H1_IP = f"10.0.{WEEK}.11"
H2_IP = f"10.0.{WEEK}.12"
H3_IP = f"10.0.{WEEK}.13"
SERVER_IP = f"10.0.{WEEK}.100"

# Port plan (avoids root privileges)
TCP_APP_PORT = 9090
UDP_APP_PORT = 9091
HTTP_PORT = 8080
PROXY_PORT = 8888
DNS_PORT = 5353
FTP_PORT = 2121
SSH_PORT = 2222
CONTROLLER_PORT = 6633

# Custom ports for Week 6
WEEK_PORT_BASE = 5100 + 100 * (WEEK - 1)  # 5600
WEEK_PORT_RANGE = range(WEEK_PORT_BASE, WEEK_PORT_BASE + 100)

# Default timeouts
DEFAULT_TIMEOUT = 5
DEFAULT_BUFFER_SIZE = 4096


# ═══════════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════════

def setup_logging(
    name: str = "network_app",
    level: int = logging.INFO,
    fmt: str = "[%(asctime)s] %(levelname)s: %(message)s"
) -> logging.Logger:
    """
    Configure consistent logging for applications.
    
    Args:
        name: Logger name
        level: Logging level (default: INFO)
        fmt: Message format
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt, datefmt="%H:%M:%S"))
        logger.addHandler(handler)
    
    return logger


# ═══════════════════════════════════════════════════════════════════════════
# SOCKET HELPERS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SocketConfig:
    """Socket configuration."""
    host: str = "0.0.0.0"
    port: int = TCP_APP_PORT
    timeout: float = DEFAULT_TIMEOUT
    buffer_size: int = DEFAULT_BUFFER_SIZE
    reuse_addr: bool = True


def create_tcp_socket(config: Optional[SocketConfig] = None) -> socket.socket:
    """
    Create a configured TCP socket.
    
    Args:
        config: Socket configuration (optional)
    
    Returns:
        Configured TCP socket
    """
    if config is None:
        config = SocketConfig()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    if config.reuse_addr:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    if config.timeout > 0:
        sock.settimeout(config.timeout)
    
    return sock


def create_udp_socket(config: Optional[SocketConfig] = None) -> socket.socket:
    """
    Create a configured UDP socket.
    
    Args:
        config: Socket configuration (optional)
    
    Returns:
        Configured UDP socket
    """
    if config is None:
        config = SocketConfig(port=UDP_APP_PORT)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    if config.reuse_addr:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    if config.timeout > 0:
        sock.settimeout(config.timeout)
    
    return sock


# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

def is_valid_ip(ip: str) -> bool:
    """Check if a string is a valid IPv4 address."""
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def is_valid_port(port: int) -> bool:
    """Check if a port is in the valid range."""
    return 1 <= port <= 65535


def is_week_port(port: int) -> bool:
    """Check if the port is in the week's custom range."""
    return port in WEEK_PORT_RANGE


# ═══════════════════════════════════════════════════════════════════════════
# ARGPARSE HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def add_common_args(parser, include_port: bool = True, include_host: bool = True):
    """
    Add common arguments to an argparse parser.
    
    Args:
        parser: ArgumentParser instance
        include_port: Include --port argument
        include_host: Include --host/--bind argument
    """
    if include_host:
        parser.add_argument(
            "--host", "--bind",
            default="0.0.0.0",
            help=f"Bind/connect address (default: 0.0.0.0)"
        )
    
    if include_port:
        parser.add_argument(
            "--port", "-p",
            type=int,
            default=TCP_APP_PORT,
            help=f"Port (default: {TCP_APP_PORT})"
        )
    
    parser.add_argument(
        "--timeout", "-t",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"Timeout in seconds (default: {DEFAULT_TIMEOUT})"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )


# ═══════════════════════════════════════════════════════════════════════════
# WEEK INFORMATION
# ═══════════════════════════════════════════════════════════════════════════

def print_week_info():
    """Display information about the week's configuration."""
    print(f"""
╔══════════════════════════════════════════════════════════╗
║  Week {WEEK}: SDN - Software-Defined Networking             ║
╠══════════════════════════════════════════════════════════╣
║  IP Plan:                                                ║
║    Subnet:  {SUBNET:<20}                       ║
║    Gateway: {GATEWAY:<20}                       ║
║    h1:      {H1_IP:<20}                       ║
║    h2:      {H2_IP:<20}                       ║
║    h3:      {H3_IP:<20}                       ║
║    Server:  {SERVER_IP:<20}                       ║
╠══════════════════════════════════════════════════════════╣
║  Port Plan:                                              ║
║    TCP App:     {TCP_APP_PORT:<10}                              ║
║    UDP App:     {UDP_APP_PORT:<10}                              ║
║    Controller:  {CONTROLLER_PORT:<10}                              ║
║    Week Base:   {WEEK_PORT_BASE:<10} (range: {WEEK_PORT_BASE}-{WEEK_PORT_BASE+99})    ║
╚══════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    print_week_info()
