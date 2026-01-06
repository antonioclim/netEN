"""
═══════════════════════════════════════════════════════════════════════════════
  net_utils.py – Common utilities for network exercises
═══════════════════════════════════════════════════════════════════════════════

Module with helper functions for network operations:
- Socket read/write with buffering
- Simplified HTTP parsing  
- TCP connection functions with timeout
- Time utilities

═══════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import socket
import time
import re
from typing import Optional
from contextlib import contextmanager


def now_s() -> float:
    """Returns current timestamp in seconds (monotonic)."""
    return time.monotonic()


def set_timeouts(sock: socket.socket, timeout: float) -> None:
    """Set timeout for socket operations."""
    sock.settimeout(timeout)


@contextmanager
def connect_tcp(host: str, port: int, timeout: float = 5.0):
    """
    Context manager for TCP connection.
    
    Example:
        with connect_tcp("localhost", 8080) as sock:
            sock.sendall(b"GET / HTTP/1.1\\r\\n\\r\\n")
            response = sock.recv(4096)
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        yield sock
    finally:
        try:
            sock.close()
        except Exception:
            pass


def recv_until(sock: socket.socket, 
               delimiter: bytes = b"\r\n\r\n", 
               max_bytes: int = 65536) -> bytes:
    """
    Read from socket until delimiter or max_bytes.
    
    Used for reading HTTP headers.
    
    Args:
        sock: Socket to read from
        delimiter: Termination sequence (default: \\r\\n\\r\\n for HTTP)
        max_bytes: Maximum byte limit
    
    Returns:
        Data read (including delimiter if found)
    """
    data = b""
    while len(data) < max_bytes:
        try:
            chunk = sock.recv(1024)
            if not chunk:
                break
            data += chunk
            if delimiter in data:
                break
        except socket.timeout:
            break
        except Exception:
            break
    return data


def recv_exact(sock: socket.socket, n: int) -> bytes:
    """
    Read exactly n bytes from socket.
    
    Args:
        sock: Socket to read from
        n: Exact number of bytes to read
    
    Returns:
        Exactly n bytes (or fewer if connection closed)
    """
    data = b""
    while len(data) < n:
        try:
            chunk = sock.recv(n - len(data))
            if not chunk:
                break
            data += chunk
        except Exception:
            break
    return data


def parse_http_content_length(headers: bytes) -> int:
    """
    Extract Content-Length from HTTP headers.
    
    Args:
        headers: HTTP headers (bytes)
    
    Returns:
        Content-Length value or 0 if not present
    """
    try:
        headers_str = headers.decode("ascii", errors="replace")
        match = re.search(r"content-length:\s*(\d+)", headers_str, re.IGNORECASE)
        if match:
            return int(match.group(1))
    except Exception:
        pass
    return 0


def parse_http_status(response: bytes) -> int:
    """
    Extract HTTP status code from response.
    
    Args:
        response: HTTP response (bytes)
    
    Returns:
        Status code (e.g.: 200) or 0 if cannot be parsed
    """
    try:
        first_line = response.split(b"\r\n", 1)[0].decode("ascii", errors="replace")
        parts = first_line.split()
        if len(parts) >= 2:
            return int(parts[1])
    except Exception:
        pass
    return 0


def format_bytes(n: int) -> str:
    """Format number of bytes in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if abs(n) < 1024.0:
            return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} TB"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 0.001:
        return f"{seconds * 1000000:.1f} µs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    else:
        return f"{seconds:.3f} s"


# Revolvix&Hypotheticalandrei
