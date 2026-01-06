"""Utility helpers used across Week 10 examples.

The Week 10 kit intentionally stays close to the standard library. These
functions are small wrappers that keep the examples readable.
"""

from __future__ import annotations

import json
import random
import socket
from typing import Any, Dict, Tuple


def find_free_port(host: str = "127.0.0.1") -> int:
    """Return an available TCP port by asking the OS to allocate one."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, 0))
        _, port = s.getsockname()
        return int(port)


def random_port(min_port: int = 20000, max_port: int = 40000) -> int:
    """Return a pseudo-random port in a safe range."""
    if min_port <= 0 or max_port <= 0 or max_port < min_port:
        raise ValueError("Invalid port range")
    return random.randint(min_port, max_port)


def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """Check if a TCP port is open."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def parse_http_headers(raw_headers: str) -> Dict[str, str]:
    """Parse HTTP headers from a raw header block."""
    headers: Dict[str, str] = {}
    for line in raw_headers.splitlines():
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        headers[key.strip()] = value.strip()
    return headers


def pretty_json(obj: Any) -> str:
    """Return pretty-printed JSON."""
    return json.dumps(obj, indent=2, sort_keys=True)


def split_host_port(value: str, default_port: int) -> Tuple[str, int]:
    """Split a string host:port into (host, port)."""
    if ":" not in value:
        return value, default_port
    host, port_s = value.rsplit(":", 1)
    return host, int(port_s)
