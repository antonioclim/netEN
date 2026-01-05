#!/usr/bin/env python3
"""
demo_reverse_proxy.py - Reverse Proxy with Round-Robin Load Balancing.

Week 8 – Demo: HTTP Reverse Proxy

═══════════════════════════════════════════════════════════════════════════════
WHAT WE WILL LEARN
═══════════════════════════════════════════════════════════════════════════════
- The concept of reverse proxy and its role in web architectures
- Implementing load balancing with round-robin algorithm
- Modifying HTTP headers (X-Forwarded-For, X-Forwarded-Host)
- Observing two distinct TCP connections (client→proxy, proxy→backend)
- Understanding the difference between proxy and direct connection

═══════════════════════════════════════════════════════════════════════════════
ARCHITECTURE
═══════════════════════════════════════════════════════════════════════════════

    ┌────────┐          ┌─────────────────┐          ┌───────────┐
    │ Client │ ───────→ │  Reverse Proxy  │ ───────→ │ Backend A │
    │        │          │   (port 8080)   │          │ (port 9001)│
    └────────┘          │                 │          └───────────┘
                        │  Round-Robin    │          ┌───────────┐
                        │                 │ ───────→ │ Backend B │
                        │                 │          │ (port 9002)│
                        └─────────────────┘          └───────────┘

═══════════════════════════════════════════════════════════════════════════════
USAGE
═══════════════════════════════════════════════════════════════════════════════
    # Start reverse proxy with 2 backends
    python3 demo_reverse_proxy.py --listen-port 8080 \\
        --backends 127.0.0.1:9001,127.0.0.1:9002
    
    # Test (observe backend alternation)
    for i in {1..6}; do curl -s http://localhost:8080/ -D - | grep X-Backend; done
    
    # tcpdump capture (see the 2 TCP connections)
    sudo tcpdump -i lo '(port 8080 or port 9001 or port 9002)' -nn

Author: Computer Networks, ASE Bucharest, 2025
Revolvix&Hypotheticalandrei
"""

from __future__ import annotations

import argparse
import os
import socket
import sys
import threading
import time
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Add utils directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.net_utils import (
    read_until,
    parse_http_request,
    build_response,
    get_ephemeral_port,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Logging
# ═══════════════════════════════════════════════════════════════════════════════

COLORS = {
    "INFO": "\033[0;32m",
    "WARN": "\033[0;33m",
    "ERROR": "\033[0;31m",
    "DEBUG": "\033[0;36m",
    "PROXY": "\033[0;35m",  # magenta for proxy
    "RESET": "\033[0m",
}

def log(msg: str, level: str = "INFO") -> None:
    ts = time.strftime("%H:%M:%S")
    color = COLORS.get(level, "")
    reset = COLORS["RESET"]
    print(f"[{ts}] {color}[{level}]{reset} {msg}")


# ═══════════════════════════════════════════════════════════════════════════════
# Backend and Load Balancer
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Backend:
    """Representation of a backend server."""
    host: str
    port: int
    name: str = ""
    
    def __post_init__(self):
        if not self.name:
            self.name = f"{self.host}:{self.port}"
    
    @classmethod
    def from_string(cls, s: str, name: str = "") -> "Backend":
        """Parse 'host:port' into Backend."""
        if ":" in s:
            host, port_str = s.rsplit(":", 1)
            return cls(host=host, port=int(port_str), name=name)
        else:
            return cls(host=s, port=80, name=name)


class RoundRobinBalancer:
    """
    Load balancer with Round-Robin algorithm.
    
    Round-Robin: Balanced cyclic distribution
    - Request 1 → Backend A
    - Request 2 → Backend B  
    - Request 3 → Backend A
    - ...
    
    Thread-safe through lock.
    """
    
    def __init__(self, backends: List[Backend]):
        self.backends = backends
        self._index = 0
        self._lock = threading.Lock()
        log(f"RoundRobin initialised with {len(backends)} backends", "INFO")
    
    def next(self) -> Backend:
        """Return the next backend in rotation."""
        with self._lock:
            backend = self.backends[self._index]
            self._index = (self._index + 1) % len(self.backends)
            return backend
    
    def get_all(self) -> List[Backend]:
        """Return the list of all backends."""
        return self.backends.copy()


# ═══════════════════════════════════════════════════════════════════════════════
# Reverse Proxy
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ProxyConfig:
    """Reverse proxy configuration."""
    listen_host: str
    listen_port: int
    backends: List[Backend]
    timeout: float = 10.0


class ReverseProxy:
    """
    HTTP Reverse Proxy with load balancing.
    
    FEATURES:
    - Accepts connections from clients
    - Selects backend with round-robin
    - Forwards request to backend (with header modification)
    - Forwards response to client
    - Adds informative headers (X-Forwarded-*, Via)
    """
    
    def __init__(self, config: ProxyConfig):
        self.config = config
        self.balancer = RoundRobinBalancer(config.backends)
    
    def serve_forever(self) -> None:
        """Start the proxy and accept connections."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.config.listen_host, self.config.listen_port))
            server.listen(100)
            
            backends_str = ", ".join(b.name for b in self.config.backends)
            log(f"Reverse Proxy started on {self.config.listen_host}:{self.config.listen_port}", "PROXY")
            log(f"  Backends: {backends_str}", "PROXY")
            log(f"  Algorithm: Round-Robin", "PROXY")
            log("Press Ctrl+C to stop.", "INFO")
            print()
            
            try:
                while True:
                    conn, addr = server.accept()
                    # Each connection in separate thread
                    t = threading.Thread(
                        target=self._handle_client,
                        args=(conn, addr),
                        daemon=True
                    )
                    t.start()
            except KeyboardInterrupt:
                print()
                log("Proxy stopped (Ctrl+C)", "INFO")
    
    def _handle_client(self, client_conn: socket.socket, client_addr: Tuple[str, int]) -> None:
        """
        Process a connection from a client.
        
        FLOW:
        1. Read request from client
        2. Select backend (round-robin)
        3. Modify headers (X-Forwarded-For, etc.)
        4. Open connection to backend
        5. Send modified request
        6. Read response from backend
        7. Send response to client
        """
        client_ip, client_port = client_addr
        request_id = str(uuid.uuid4())[:8]  # Short ID for logging
        
        log(f"[{request_id}] Connection from {client_ip}:{client_port}", "PROXY")
        
        with client_conn:
            try:
                # ─────────────────────────────────────────────────────────────
                # Step 1: Read request from client
                # ─────────────────────────────────────────────────────────────
                raw_request = read_until(client_conn, b"\r\n\r\n", timeout=self.config.timeout)
                if not raw_request:
                    return
                
                req = parse_http_request(raw_request)
                log(f"[{request_id}] → {req.method} {req.target}", "DEBUG")
                
                # ─────────────────────────────────────────────────────────────
                # Step 2: Select backend (round-robin)
                # ─────────────────────────────────────────────────────────────
                backend = self.balancer.next()
                log(f"[{request_id}] Backend selected: {backend.name}", "PROXY")
                
                # ─────────────────────────────────────────────────────────────
                # Step 3: Modify headers for forwarding
                # ─────────────────────────────────────────────────────────────
                # These headers inform the backend about the original client
                forward_headers = req.headers.copy()
                
                # X-Forwarded-For: Original client IP
                # (can be a chain if there are multiple proxies)
                existing_xff = forward_headers.get("x-forwarded-for", "")
                if existing_xff:
                    forward_headers["x-forwarded-for"] = f"{existing_xff}, {client_ip}"
                else:
                    forward_headers["x-forwarded-for"] = client_ip
                
                # X-Forwarded-Host: Original host requested by client
                if "host" in forward_headers:
                    forward_headers["x-forwarded-host"] = forward_headers["host"]
                
                # X-Forwarded-Proto: Original protocol (http in our case)
                forward_headers["x-forwarded-proto"] = "http"
                
                # Via: Proxy identification (for debugging)
                forward_headers["via"] = "1.1 ASE-S8-Proxy"
                
                # X-Request-ID: For log correlation
                forward_headers["x-request-id"] = request_id
                
                # Host: Update to backend
                forward_headers["host"] = f"{backend.host}:{backend.port}"
                
                # Connection: close (simplification, we do not maintain connections)
                forward_headers["connection"] = "close"
                
                # Remove proxy-specific headers
                forward_headers.pop("proxy-connection", None)
                forward_headers.pop("keep-alive", None)
                
                # ─────────────────────────────────────────────────────────────
                # Step 4: Build request for backend
                # ─────────────────────────────────────────────────────────────
                request_lines = [f"{req.method} {req.target} {req.version}"]
                for key, value in forward_headers.items():
                    request_lines.append(f"{key}: {value}")
                forward_request = "\r\n".join(request_lines).encode("iso-8859-1") + b"\r\n\r\n"
                
                # ─────────────────────────────────────────────────────────────
                # Step 5: Forward to backend
                # ─────────────────────────────────────────────────────────────
                try:
                    with socket.create_connection(
                        (backend.host, backend.port), 
                        timeout=self.config.timeout
                    ) as backend_conn:
                        backend_conn.sendall(forward_request)
                        
                        # Step 6: Read response from backend
                        response_data = b""
                        while True:
                            chunk = backend_conn.recv(8192)
                            if not chunk:
                                break
                            response_data += chunk
                
                except (socket.timeout, ConnectionRefusedError, OSError) as e:
                    # Backend unavailable
                    log(f"[{request_id}] Backend {backend.name} unavailable: {e}", "ERROR")
                    error_body = b"502 Bad Gateway\n\nBackend server unavailable.\n"
                    error_resp = build_response(502, error_body, 
                                                extra_headers={"X-Proxy-Error": str(e)})
                    client_conn.sendall(error_resp)
                    return
                
                # ─────────────────────────────────────────────────────────────
                # Step 7: Add X-Served-By header to response
                # ─────────────────────────────────────────────────────────────
                # We inject a header to see which backend served the request
                response_data = self._inject_response_header(
                    response_data, "X-Served-By", backend.name
                )
                response_data = self._inject_response_header(
                    response_data, "X-Request-ID", request_id
                )
                
                # ─────────────────────────────────────────────────────────────
                # Step 8: Send response to client
                # ─────────────────────────────────────────────────────────────
                client_conn.sendall(response_data)
                
                log(f"[{request_id}] ← Response {len(response_data)} bytes via {backend.name}", "PROXY")
            
            except TimeoutError:
                log(f"[{request_id}] Timeout reading request", "WARN")
            except ValueError as e:
                log(f"[{request_id}] Invalid request: {e}", "WARN")
            except Exception as e:
                log(f"[{request_id}] Proxy error: {e}", "ERROR")
    
    @staticmethod
    def _inject_response_header(response: bytes, header: str, value: str) -> bytes:
        """Inject a header into the HTTP response."""
        try:
            # Separate headers from body
            if b"\r\n\r\n" not in response:
                return response
            
            head, sep, body = response.partition(b"\r\n\r\n")
            
            # Check that it is HTTP
            if not head.startswith(b"HTTP/"):
                return response
            
            # Check that the header does not already exist
            header_lower = header.lower().encode("ascii")
            for line in head.split(b"\r\n")[1:]:
                if line.lower().startswith(header_lower + b":"):
                    return response  # Already exists
            
            # Add the header
            new_header = f"{header}: {value}".encode("ascii")
            new_head = head + b"\r\n" + new_header
            
            return new_head + b"\r\n\r\n" + body
        
        except Exception:
            return response


# ═══════════════════════════════════════════════════════════════════════════════
# Self-test
# ═══════════════════════════════════════════════════════════════════════════════

def selftest() -> int:
    """Automatic test for reverse proxy."""
    log("Running selftest for reverse proxy...", "INFO")
    
    # For a complete test, we would need backends
    # Here we only do an initialisation test
    
    backends = [
        Backend.from_string("127.0.0.1:9001", "backend-A"),
        Backend.from_string("127.0.0.1:9002", "backend-B"),
    ]
    
    balancer = RoundRobinBalancer(backends)
    
    # Test round-robin
    selected = [balancer.next().name for _ in range(6)]
    expected = ["backend-A", "backend-B", "backend-A", "backend-B", "backend-A", "backend-B"]
    
    if selected == expected:
        log("✓ Round-robin works correctly", "INFO")
        log(f"  Selections: {' → '.join(selected)}", "DEBUG")
        return 0
    else:
        log("✗ Round-robin incorrect", "ERROR")
        log(f"  Expected: {expected}", "ERROR")
        log(f"  Got: {selected}", "ERROR")
        return 1


# ═══════════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser(
        description="HTTP Reverse Proxy with Load Balancing - Week 8",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Proxy to a single backend
  python3 demo_reverse_proxy.py --backends 127.0.0.1:9001
  
  # Proxy with round-robin between 2 backends
  python3 demo_reverse_proxy.py --backends 127.0.0.1:9001,127.0.0.1:9002
  
  # Test round-robin
  for i in {1..6}; do curl -s localhost:8080/ -D - | grep X-Served-By; done
        """
    )
    parser.add_argument("--listen-host", default="0.0.0.0",
                        help="Listen address (default: 0.0.0.0)")
    parser.add_argument("--listen-port", type=int, default=8080,
                        help="Listen port (default: 8080)")
    parser.add_argument("--backends", required=False,
                        default="127.0.0.1:9001,127.0.0.1:9002",
                        help="Backend list (host:port,host:port,...)")
    parser.add_argument("--timeout", type=float, default=10.0,
                        help="Connection timeout (default: 10s)")
    parser.add_argument("--selftest", action="store_true",
                        help="Run automatic test")
    
    args = parser.parse_args()
    
    if args.selftest:
        return selftest()
    
    # Parse backends
    backend_strs = args.backends.split(",")
    backends = []
    for i, bs in enumerate(backend_strs):
        bs = bs.strip()
        if bs:
            name = f"backend-{chr(65 + i)}"  # A, B, C, ...
            backends.append(Backend.from_string(bs, name))
    
    if not backends:
        log("ERROR: At least one backend must be specified", "ERROR")
        return 1
    
    config = ProxyConfig(
        listen_host=args.listen_host,
        listen_port=args.listen_port,
        backends=backends,
        timeout=args.timeout,
    )
    
    proxy = ReverseProxy(config)
    proxy.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
