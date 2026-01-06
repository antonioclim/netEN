#!/usr/bin/env python3
"""Week 13 - Network utilities (helper functions).

This module contains small helpers used across the kit. It is written to be:
- dependency-light (standard library only)
- predictable and easy to test

Functions
---------
- resolve_host(hostname) -> ip string
- tcp_connectable(host, port, timeout) -> bool
- parse_ports(spec) -> list[int]
- guess_service(port) -> str
"""

from __future__ import annotations

import socket
from typing import List


def resolve_host(hostname: str) -> str:
    """Resolve a hostname to an IPv4 address (best effort)."""
    try:
        return socket.gethostbyname(hostname)
    except Exception:
        return hostname


def tcp_connectable(host: str, port: int, timeout: float = 1.0) -> bool:
    """Return True if a TCP connection can be established."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def parse_ports(spec: str) -> List[int]:
    """Parse a comma-separated list of ports and ranges into a sorted list.

    Example:
      "22,80,8000-8003" -> [22, 80, 8000, 8001, 8002, 8003]
    """
    ports: List[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            ports.extend(range(int(a), int(b) + 1))
        else:
            ports.append(int(part))
    # unique and sorted
    return sorted(set(ports))


def guess_service(port: int) -> str:
    """Return a short service label for common ports."""
    mapping = {
        21: "ftp",
        22: "ssh",
        23: "telnet",
        80: "http",
        443: "https",
        1883: "mqtt",
        8883: "mqtt-tls",
        2121: "ftp-alt",
        6200: "backdoor-stub",
        8080: "http-alt",
    }
    return mapping.get(port, "unknown")


if __name__ == "__main__":
    # Minimal self-test (no network traffic)
    assert parse_ports("22,80,8000-8002") == [22, 80, 8000, 8001, 8002]
    print("net_utils: basic self-test passed")
