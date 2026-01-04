#!/usr/bin/env python3
"""lb_proxy.py — Simple HTTP Load Balancer / Reverse Proxy.

Features:
  - Round-robin distribution between backends
  - Passive health check (marks backend unavailable on error)
  - Adds forwarding headers (X-Forwarded-For, X-Real-IP)
  - Detailed logging for debugging

Usage:
  python3 lb_proxy.py --listen-host 0.0.0.0 --listen-port 8080 \
                      --backends 10.0.0.2:8000,10.0.0.3:8000
"""

from __future__ import annotations

import argparse
import socket
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import List, Tuple, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


class Backend:
    """Represents a backend with health state."""
    
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.healthy = True
        self.consecutive_failures = 0
        self.total_requests = 0
        self.total_errors = 0
        self.lock = threading.Lock()
    
    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"
    
    def mark_success(self) -> None:
        with self.lock:
            self.healthy = True
            self.consecutive_failures = 0
            self.total_requests += 1
    
    def mark_failure(self) -> None:
        with self.lock:
            self.consecutive_failures += 1
            self.total_requests += 1
            self.total_errors += 1
            if self.consecutive_failures >= 3:
                self.healthy = False


class LoadBalancer:
    """Round-robin load balancer with health tracking."""
    
    def __init__(self, backends_str: str):
        self.backends: List[Backend] = []
        self._current_index = 0
        self._lock = threading.Lock()
        
        for addr in backends_str.split(","):
            addr = addr.strip()
            if not addr:
                continue
            parts = addr.split(":")
            host = parts[0]
            port = int(parts[1]) if len(parts) > 1 else 80
            self.backends.append(Backend(host, port))
        
        if not self.backends:
            raise ValueError("No backends configured")
    
    def get_next_backend(self) -> Optional[Backend]:
        """Returns next healthy backend (round-robin)."""
        with self._lock:
            healthy_backends = [b for b in self.backends if b.healthy]
            if not healthy_backends:
                # Fallback: try any backend
                healthy_backends = self.backends
            
            if not healthy_backends:
                return None
            
            backend = healthy_backends[self._current_index % len(healthy_backends)]
            self._current_index = (self._current_index + 1) % len(healthy_backends)
            return backend
    
    def get_stats(self) -> dict:
        """Returns statistics for all backends."""
        return {
            "backends": [
                {
                    "address": b.address,
                    "healthy": b.healthy,
                    "total_requests": b.total_requests,
                    "total_errors": b.total_errors,
                }
                for b in self.backends
            ]
        }


class ProxyHandler(BaseHTTPRequestHandler):
    """Handler for proxy/load balancer."""
    
    lb: LoadBalancer
    timeout: float = 5.0

    def log_message(self, format: str, *args) -> None:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"[{ts}] [proxy] {format % args}")

    def _proxy_request(self) -> None:
        """Proxies the request to a backend."""
        backend = self.lb.get_next_backend()
        if backend is None:
            self._send_error(503, "No healthy backends available")
            return
        
        # Build URL to backend
        backend_url = f"http://{backend.host}:{backend.port}{self.path}"
        
        # Copy relevant headers
        headers = {}
        for key, value in self.headers.items():
            if key.lower() not in ("host", "connection"):
                headers[key] = value
        
        # Add forwarding headers
        client_ip = self.client_address[0]
        headers["X-Forwarded-For"] = client_ip
        headers["X-Real-IP"] = client_ip
        headers["X-Forwarded-Host"] = self.headers.get("Host", "")
        
        try:
            req = Request(backend_url, headers=headers, method=self.command)
            
            # Read body if exists
            content_length = self.headers.get("Content-Length")
            if content_length:
                req.data = self.rfile.read(int(content_length))
            
            with urlopen(req, timeout=self.timeout) as response:
                # Forward response
                self.send_response(response.status)
                
                for key, value in response.getheaders():
                    if key.lower() not in ("transfer-encoding", "connection"):
                        self.send_header(key, value)
                
                self.send_header("X-Backend", backend.address)
                self.end_headers()
                
                body = response.read()
                self.wfile.write(body)
                
                backend.mark_success()
                self.log_message(
                    "PROXY %s -> %s [%d] %d bytes",
                    self.path, backend.address, response.status, len(body)
                )
        
        except HTTPError as e:
            # Backend responded with HTTP error
            self.send_response(e.code)
            self.send_header("X-Backend", backend.address)
            self.send_header("X-Proxy-Error", "backend-http-error")
            self.end_headers()
            self.wfile.write(e.read())
            backend.mark_success()  # Backend works, just returned error
            
        except (URLError, socket.timeout, ConnectionRefusedError, OSError) as e:
            backend.mark_failure()
            error_msg = str(e)
            self.log_message("ERROR backend %s: %s", backend.address, error_msg)
            self._send_error(502, f"Backend unavailable: {backend.address}")

    def _send_error(self, code: int, message: str) -> None:
        """Sends error response."""
        body = f"{code} {message}\n".encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/lb-status":
            # Special endpoint: LB statistics
            import json
            stats = self.lb.get_stats()
            body = json.dumps(stats, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self._proxy_request()

    def do_POST(self) -> None:
        self._proxy_request()

    def do_PUT(self) -> None:
        self._proxy_request()

    def do_DELETE(self) -> None:
        self._proxy_request()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="HTTP Load Balancer / Reverse Proxy"
    )
    parser.add_argument(
        "--listen-host",
        default="0.0.0.0",
        help="Bind address (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--listen-port",
        type=int,
        default=8080,
        help="Listening port (default: 8080)"
    )
    parser.add_argument(
        "--backends",
        required=True,
        help="List of backends (format: host1:port1,host2:port2)"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Timeout for backend connections (default: 5.0s)"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    
    lb = LoadBalancer(args.backends)
    ProxyHandler.lb = lb
    ProxyHandler.timeout = args.timeout
    
    server_address = (args.listen_host, args.listen_port)
    httpd = HTTPServer(server_address, ProxyHandler)
    
    print(f"[proxy] Starting load balancer on {args.listen_host}:{args.listen_port}")
    print(f"[proxy] Backends: {[b.address for b in lb.backends]}")
    print(f"[proxy] Special endpoint: /lb-status")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[proxy] Shutting down...")
    finally:
        httpd.server_close()
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
