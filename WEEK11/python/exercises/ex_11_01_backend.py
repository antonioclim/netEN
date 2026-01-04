#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
  Exercise 11.01 – Simple HTTP Backend Server
═══════════════════════════════════════════════════════════════════════════════

EDUCATIONAL PURPOSE:
  - Understanding the HTTP request-response model
  - Implementing a minimal HTTP server
  - Observing behaviour from the backend perspective

FEATURES:
  - Simple HTTP server on configurable port
  - Responds with backend ID (to observe load balancing)
  - Support for delay simulation (for least_conn tests)
  - Minimal logging for debugging

ARCHITECTURE:
  ┌─────────────────────────────────────────────────────────────┐
  │  Client  ──────►  Load Balancer  ──────►  Backend (this     │
  │                                          server)            │
  │          ◄──────                 ◄──────                    │
  └─────────────────────────────────────────────────────────────┘

USAGE:
  python3 ex_11_01_backend.py --id 1 --port 8001
  python3 ex_11_01_backend.py --id 2 --port 8002
  python3 ex_11_01_backend.py --id 3 --port 8003 --delay 0.5

TESTING:
  curl http://localhost:8001/
  # Response: Backend 1 | Host: hostname | Time: 2025-01-01T12:00:00

═══════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import argparse
import socket
import threading
import time
import os
from datetime import datetime


def get_hostname() -> str:
    """Get hostname or a fallback."""
    try:
        return socket.gethostname()
    except Exception:
        return "unknown"


def build_response(backend_id: int, request_count: int) -> bytes:
    """
    Build the HTTP response.
    
    The response format includes:
    - Backend ID (for load balancing verification)
    - Container/machine hostname
    - Current timestamp
    - Processed request number
    """
    hostname = get_hostname()
    timestamp = datetime.now().isoformat(timespec='seconds')
    
    body = f"Backend {backend_id} | Host: {hostname} | Time: {timestamp} | Request #{request_count}\n"
    body_bytes = body.encode("utf-8")
    
    response = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/plain; charset=utf-8\r\n"
        b"Connection: close\r\n"
        b"X-Backend-ID: " + str(backend_id).encode() + b"\r\n"
        b"Content-Length: " + str(len(body_bytes)).encode() + b"\r\n"
        b"\r\n"
    ) + body_bytes
    
    return response


def handle_client(client_sock: socket.socket, 
                  client_addr: tuple,
                  backend_id: int,
                  delay: float,
                  request_counter: list,
                  verbose: bool) -> None:
    """
    Process an HTTP request.
    
    Args:
        client_sock: Client socket
        client_addr: Client address (ip, port)
        backend_id: This backend's ID
        delay: Artificial delay in seconds (for tests)
        request_counter: List with counter (for thread-safety)
        verbose: Whether to show logging
    """
    try:
        # Read request (simplified - only headers)
        request = b""
        client_sock.settimeout(5.0)
        
        while True:
            chunk = client_sock.recv(4096)
            if not chunk:
                break
            request += chunk
            if b"\r\n\r\n" in request:
                break
        
        # Increment counter thread-safe
        with threading.Lock():
            request_counter[0] += 1
            count = request_counter[0]
        
        # Simulate delay if configured
        if delay > 0:
            time.sleep(delay)
        
        # Build and send response
        response = build_response(backend_id, count)
        client_sock.sendall(response)
        
        if verbose:
            method = request.split(b" ", 1)[0].decode("ascii", errors="replace")
            print(f"[Backend {backend_id}] {client_addr[0]}:{client_addr[1]} - {method} - #{count}")
    
    except Exception as e:
        if verbose:
            print(f"[Backend {backend_id}] Error: {e}")
    
    finally:
        try:
            client_sock.close()
        except Exception:
            pass


def run_server(backend_id: int, 
               host: str, 
               port: int, 
               delay: float,
               verbose: bool) -> None:
    """
    Start the HTTP server.
    
    Args:
        backend_id: Unique ID of this backend
        host: Bind address (0.0.0.0 for all interfaces)
        port: Listening port
        delay: Artificial delay per request (seconds)
        verbose: Detailed logging
    """
    request_counter = [0]  # List for thread-safety
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((host, port))
        server_sock.listen(128)
        
        print(f"[Backend {backend_id}] Listening on {host}:{port}")
        if delay > 0:
            print(f"[Backend {backend_id}] Delay per request: {delay}s")
        print(f"[Backend {backend_id}] Press Ctrl+C to stop")
        print("")
        
        try:
            while True:
                client_sock, client_addr = server_sock.accept()
                thread = threading.Thread(
                    target=handle_client,
                    args=(client_sock, client_addr, backend_id, delay, request_counter, verbose),
                    daemon=True
                )
                thread.start()
        
        except KeyboardInterrupt:
            print(f"\n[Backend {backend_id}] Shutting down...")
            print(f"[Backend {backend_id}] Total requests served: {request_counter[0]}")


def main():
    parser = argparse.ArgumentParser(
        description="Simple HTTP backend server for load balancing demonstrations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --id 1 --port 8001
  %(prog)s --id 2 --port 8002 --delay 0.2
  %(prog)s --id 3 --port 8003 -v
        """
    )
    
    parser.add_argument("--id", type=int, default=1,
                        help="Backend ID (default: 1)")
    parser.add_argument("--host", type=str, default="0.0.0.0",
                        help="Bind address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8001,
                        help="Listening port (default: 8001)")
    parser.add_argument("--delay", type=float, default=0.0,
                        help="Artificial delay per request in seconds (default: 0)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Detailed logging")
    
    args = parser.parse_args()
    
    run_server(
        backend_id=args.id,
        host=args.host,
        port=args.port,
        delay=args.delay,
        verbose=args.verbose
    )


if __name__ == "__main__":
    main()


# Revolvix&Hypotheticalandrei
