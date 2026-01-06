#!/usr/bin/env python3
"""
net_utils.py - Utilities for network programming (Week 8).

Helper functions for:
- HTTP request/response parsing
- Building HTTP responses
- Path validation and sanitisation (security)
- MIME types and formatting

Author: Computer Networks, ASE Bucharest
"""
from __future__ import annotations

import os
import re
import socket
import urllib.parse
from dataclasses import dataclass
from typing import Dict, Optional, Tuple


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP Constants
# ═══════════════════════════════════════════════════════════════════════════════

HTTP_STATUS_CODES = {
    200: "OK",
    201: "Created",
    204: "No Content",
    301: "Moved Permanently",
    302: "Found",
    304: "Not Modified",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    408: "Request Timeout",
    414: "URI Too Long",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
}

MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".htm": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
    ".xml": "application/xml; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".pdf": "application/pdf",
    ".zip": "application/zip",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
}

DEFAULT_CONTENT_TYPE = "application/octet-stream"


# ═══════════════════════════════════════════════════════════════════════════════
# Data Classes
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HttpRequest:
    """Structured representation of an HTTP request."""
    method: str
    target: str
    version: str
    headers: Dict[str, str]
    body: bytes = b""
    raw: bytes = b""


@dataclass
class HttpResponse:
    """Structured representation of an HTTP response."""
    status: int
    reason: str
    headers: Dict[str, str]
    body: bytes = b""


# ═══════════════════════════════════════════════════════════════════════════════
# Socket Reading Functions
# ═══════════════════════════════════════════════════════════════════════════════

def read_until(sock: socket.socket, 
               marker: bytes = b"\r\n\r\n", 
               timeout: float = 10.0,
               max_bytes: int = 64 * 1024) -> bytes:
    """
    Read from socket until the specified marker is encountered.
    
    Args:
        sock: The socket to read from
        marker: The sequence marking the end (default: CRLFCRLF for HTTP)
        timeout: Timeout in seconds
        max_bytes: Maximum number of bytes to read
    
    Returns:
        Bytes read (including the marker)
    
    Raises:
        TimeoutError: If the timeout expires
        ValueError: If max_bytes is exceeded
    """
    sock.settimeout(timeout)
    data = b""
    
    try:
        while marker not in data:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
            if len(data) > max_bytes:
                raise ValueError(f"Exceeded limit of {max_bytes} bytes")
        return data
    except socket.timeout:
        raise TimeoutError("Socket timeout on read")


def read_exact(sock: socket.socket, n: int, timeout: float = 10.0) -> bytes:
    """Read exactly n bytes from socket."""
    sock.settimeout(timeout)
    data = b""
    while len(data) < n:
        chunk = sock.recv(min(4096, n - len(data)))
        if not chunk:
            break
        data += chunk
    return data


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP Parsing
# ═══════════════════════════════════════════════════════════════════════════════

def parse_http_request(raw: bytes) -> HttpRequest:
    """
    Parse an HTTP request from bytes.
    
    Args:
        raw: Raw bytes of the request (minimum up to CRLFCRLF)
    
    Returns:
        HttpRequest with parsed fields
    
    Raises:
        ValueError: If the request is invalid
    """
    if not raw:
        raise ValueError("Empty request")
    
    # Separate headers from body
    if b"\r\n\r\n" in raw:
        head_bytes, body = raw.split(b"\r\n\r\n", 1)
    else:
        head_bytes = raw
        body = b""
    
    # Decode headers (HTTP/1.x uses ISO-8859-1)
    try:
        head = head_bytes.decode("iso-8859-1")
    except UnicodeDecodeError:
        raise ValueError("Invalid encoding in headers")
    
    lines = head.split("\r\n")
    if not lines:
        raise ValueError("Request without request line")
    
    # Parse request line: METHOD SP REQUEST-TARGET SP HTTP-VERSION
    request_line = lines[0]
    parts = request_line.split(" ")
    if len(parts) < 3:
        raise ValueError(f"Invalid request line: {request_line}")
    
    method = parts[0].upper()
    target = parts[1]
    version = parts[2]
    
    # Validate method
    valid_methods = {"GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"}
    if method not in valid_methods:
        raise ValueError(f"Unknown HTTP method: {method}")
    
    # Validate version
    if not version.startswith("HTTP/"):
        raise ValueError(f"Invalid HTTP version: {version}")
    
    # Parse headers
    headers: Dict[str, str] = {}
    for line in lines[1:]:
        if not line:
            continue
        if ":" not in line:
            continue  # Ignore malformed lines
        key, value = line.split(":", 1)
        # Normalise keys to lowercase
        headers[key.strip().lower()] = value.strip()
    
    return HttpRequest(
        method=method,
        target=target,
        version=version,
        headers=headers,
        body=body,
        raw=raw
    )


def parse_http_response(raw: bytes) -> HttpResponse:
    """Parse an HTTP response from bytes."""
    if b"\r\n\r\n" in raw:
        head_bytes, body = raw.split(b"\r\n\r\n", 1)
    else:
        head_bytes = raw
        body = b""
    
    head = head_bytes.decode("iso-8859-1", errors="replace")
    lines = head.split("\r\n")
    
    # Status line: HTTP/1.1 200 OK
    status_line = lines[0] if lines else ""
    match = re.match(r"HTTP/\d\.\d\s+(\d+)\s+(.*)", status_line)
    if not match:
        raise ValueError(f"Invalid status line: {status_line}")
    
    status = int(match.group(1))
    reason = match.group(2)
    
    headers: Dict[str, str] = {}
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    
    return HttpResponse(status=status, reason=reason, headers=headers, body=body)


# ═══════════════════════════════════════════════════════════════════════════════
# Building HTTP Responses
# ═══════════════════════════════════════════════════════════════════════════════

def build_response(status: int, 
                   body: bytes = b"",
                   content_type: str = "text/plain; charset=utf-8",
                   extra_headers: Optional[Dict[str, str]] = None) -> bytes:
    """
    Build a complete HTTP response.
    
    Args:
        status: HTTP status code (e.g. 200, 404, 500)
        body: Response content
        content_type: Content-Type header
        extra_headers: Additional headers
    
    Returns:
        Complete HTTP response as bytes
    """
    reason = HTTP_STATUS_CODES.get(status, "Unknown")
    
    headers = [
        f"HTTP/1.1 {status} {reason}",
        f"Content-Type: {content_type}",
        f"Content-Length: {len(body)}",
        "Connection: close",
        "Server: ASE-S8-Server/1.0",
    ]
    
    if extra_headers:
        for key, value in extra_headers.items():
            headers.append(f"{key}: {value}")
    
    head = "\r\n".join(headers) + "\r\n\r\n"
    return head.encode("iso-8859-1") + body


def build_redirect(location: str, permanent: bool = False) -> bytes:
    """Build a redirect response."""
    status = 301 if permanent else 302
    body = f"Redirecting to {location}".encode("utf-8")
    return build_response(
        status, body, 
        extra_headers={"Location": location}
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Security: Path Validation
# ═══════════════════════════════════════════════════════════════════════════════

def safe_map_target_to_path(target: str, 
                            www_root: str,
                            max_uri_length: int = 2048) -> Tuple[Optional[str], Optional[str]]:
    """
    Map a URI target to a file path, with directory traversal protection.
    
    Args:
        target: URI from request (e.g. "/index.html", "/../etc/passwd")
        www_root: Root directory for files
        max_uri_length: Maximum URI length
    
    Returns:
        Tuple (filepath, error) where:
        - filepath: Complete path or None if error
        - error: None if OK, or one of: "URI_TOO_LONG", "TRAVERSAL"
    """
    # Check length
    if len(target) > max_uri_length:
        return None, "URI_TOO_LONG"
    
    # Extract only the path (without query string and fragment)
    parsed = urllib.parse.urlparse(target)
    path = parsed.path
    
    # Decode percent-encoding (%20 -> space, etc.)
    path = urllib.parse.unquote(path)
    
    # Remove leading / for os.path.join
    path = path.lstrip("/")
    
    # If empty or "/", map to index.html
    if not path:
        path = "index.html"
    
    # Build the complete path
    www_root = os.path.abspath(www_root)
    full_path = os.path.normpath(os.path.join(www_root, path))
    
    # CRITICAL CHECK: resulting path must be within www_root
    if not full_path.startswith(www_root + os.sep) and full_path != www_root:
        # Directory traversal attempt!
        return None, "TRAVERSAL"
    
    return full_path, None


# ═══════════════════════════════════════════════════════════════════════════════
# Various Utilities
# ═══════════════════════════════════════════════════════════════════════════════

def guess_content_type(filepath: str) -> str:
    """Guess Content-Type based on file extension."""
    _, ext = os.path.splitext(filepath.lower())
    return MIME_TYPES.get(ext, DEFAULT_CONTENT_TYPE)


def format_bytes(n: int) -> str:
    """Format number of bytes human-readable."""
    for unit in ["B", "KB", "MB", "GB"]:
        if abs(n) < 1024:
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def get_ephemeral_port() -> int:
    """Find a free ephemeral port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def format_headers(headers: Dict[str, str], indent: str = "  ") -> str:
    """Format headers for display."""
    return "\n".join(f"{indent}{k}: {v}" for k, v in sorted(headers.items()))


# ═══════════════════════════════════════════════════════════════════════════════
# Self-test
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Quick parsing test
    sample_request = b"GET /index.html HTTP/1.1\r\nHost: localhost\r\nUser-Agent: test\r\n\r\n"
    req = parse_http_request(sample_request)
    print(f"✓ Parsed: {req.method} {req.target} {req.version}")
    
    # Test response building
    resp = build_response(200, b"Hello, World!", extra_headers={"X-Test": "ok"})
    print(f"✓ Built response: {len(resp)} bytes")
    
    # Test path validation
    path, err = safe_map_target_to_path("/../etc/passwd", "/var/www")
    assert err == "TRAVERSAL", "Directory traversal was not detected!"
    print("✓ Directory traversal detection OK")
    
    print("\n[OK] All tests passed!")
