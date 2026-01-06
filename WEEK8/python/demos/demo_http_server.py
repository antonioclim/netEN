#!/usr/bin/env python3
"""
demo_http_server.py - Minimal HTTP server implemented with sockets.

Week 8 – Demo: HTTP Server (application layer over TCP)

═══════════════════════════════════════════════════════════════════════════════
WHAT WE WILL LEARN
═══════════════════════════════════════════════════════════════════════════════
- Understanding HTTP request/response structure at byte level
- Observing three-way handshake and TCP communication in tcpdump
- Implementing HTTP request line and headers parsing
- Serving static files with correct Content-Type and Content-Length
- Protection against directory traversal attacks

═══════════════════════════════════════════════════════════════════════════════
INTENTIONAL LIMITATIONS (for pedagogical clarity)
═══════════════════════════════════════════════════════════════════════════════
- Supports only GET and HEAD (no POST/PUT)
- Does not support chunked transfer encoding
- Connection: close (one request per TCP connection)
- Does not support HTTP/2 or HTTP/3

═══════════════════════════════════════════════════════════════════════════════
USAGE
═══════════════════════════════════════════════════════════════════════════════
    # Start server
    python3 demo_http_server.py --host 127.0.0.1 --port 8080 --www ./www
    
    # Test with curl
    curl -v http://127.0.0.1:8080/
    curl -v http://127.0.0.1:8080/index.html
    
    # Observe in tcpdump (three-way handshake + request/response)
    sudo tcpdump -i lo port 8080 -nn -A

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
from typing import Optional

# Add utils directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.net_utils import (
    read_until,
    parse_http_request,
    safe_map_target_to_path,
    build_response,
    guess_content_type,
    format_bytes,
    get_ephemeral_port,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Logging configuration with colours
# ═══════════════════════════════════════════════════════════════════════════════

COLORS = {
    "INFO": "\033[0;32m",     # green
    "WARN": "\033[0;33m",     # yellow  
    "ERROR": "\033[0;31m",    # red
    "DEBUG": "\033[0;36m",    # cyan
    "RESET": "\033[0m",
}


def log(msg: str, level: str = "INFO") -> None:
    """Simple logging with timestamp and colours."""
    ts = time.strftime("%H:%M:%S")
    color = COLORS.get(level, "")
    reset = COLORS["RESET"] if color else ""
    print(f"[{ts}] {color}[{level}]{reset} {msg}")


# ═══════════════════════════════════════════════════════════════════════════════
# Handler for client connections
# ═══════════════════════════════════════════════════════════════════════════════

def handle_client(conn: socket.socket, 
                  addr: tuple, 
                  www_root: str, 
                  backend_id: str) -> None:
    """
    Process an HTTP client.
    
    ALGORITHM (step by step):
    1. Read the request (until CRLFCRLF - HTTP delimiter)
    2. Parse request line (METHOD TARGET VERSION)
    3. Validate method (only GET/HEAD)
    4. Map target to file (with directory traversal protection!)
    5. Read file or generate 404
    6. Send complete HTTP response
    7. Close connection
    
    Args:
        conn: The accepted connection socket
        addr: Client address (ip, port)
        www_root: Root directory for files
        backend_id: Identifier for X-Backend header
    """
    client_ip, client_port = addr
    log(f"[+] New connection: {client_ip}:{client_port}", "INFO")
    
    try:
        # ─────────────────────────────────────────────────────────────────────
        # STEP 1: Read HTTP request
        # ─────────────────────────────────────────────────────────────────────
        # HTTP/1.x uses CRLF (\r\n) as delimiter
        # An HTTP request ends headers with an empty line (CRLFCRLF)
        raw = read_until(conn, marker=b"\r\n\r\n", timeout=5.0)
        
        # ─────────────────────────────────────────────────────────────────────
        # STEP 2: Parse request
        # ─────────────────────────────────────────────────────────────────────
        req = parse_http_request(raw)
        log(f"    {req.method} {req.target} {req.version}", "DEBUG")
        
        # ─────────────────────────────────────────────────────────────────────
        # STEP 3: Validate HTTP method
        # ─────────────────────────────────────────────────────────────────────
        # In this demo we only accept GET and HEAD
        # GET: returns headers + body
        # HEAD: returns only headers (useful for existence check)
        if req.method not in ("GET", "HEAD"):
            body = b"405 Method Not Allowed\n\nThis server only supports GET and HEAD.\n"
            resp = build_response(405, body, extra_headers={"X-Backend": backend_id, "X-Served-By": backend_id})
            conn.sendall(resp)
            log(f"    → 405 Method Not Allowed ({req.method})", "WARN")
            return
        
        # ─────────────────────────────────────────────────────────────────────
        # STEP 4: Map path → file (WITH SECURITY!)
        # ─────────────────────────────────────────────────────────────────────
        filepath, error = safe_map_target_to_path(req.target, www_root)
        
        # Check for security errors
        if error == "URI_TOO_LONG":
            resp = build_response(414, b"URI Too Long\n", 
                                  extra_headers={"X-Backend": backend_id, "X-Served-By": backend_id})
            conn.sendall(resp)
            log(f"    → 414 URI Too Long", "WARN")
            return
        
        if error == "TRAVERSAL":
            # WARNING: Directory traversal detected!
            # An attacker is trying to access files outside www_root
            # E.g.: GET /../../../etc/passwd
            resp = build_response(400, b"Bad Request\n", 
                                  extra_headers={"X-Backend": backend_id, "X-Served-By": backend_id})
            conn.sendall(resp)
            log(f"    → 400 Bad Request (directory traversal detected!)", "WARN")
            return
        
        # ─────────────────────────────────────────────────────────────────────
        # STEP 5: Check file existence
        # ─────────────────────────────────────────────────────────────────────
        if not filepath or not os.path.isfile(filepath):
            body = b"<!DOCTYPE html>\n<html><body><h1>404 - Not Found</h1><p>Resource does not exist.</p></body></html>\n"
            resp = build_response(404, body, 
                                  content_type="text/html; charset=utf-8",
                                  extra_headers={"X-Backend": backend_id, "X-Served-By": backend_id})
            conn.sendall(resp)
            log(f"    → 404 Not Found: {req.target}", "WARN")
            return
        
        # ─────────────────────────────────────────────────────────────────────
        # STEP 6: Read and send file
        # ─────────────────────────────────────────────────────────────────────
        with open(filepath, "rb") as f:
            content = f.read()
        
        content_type = guess_content_type(filepath)
        extra_headers = {"X-Backend": backend_id, "X-Served-By": backend_id}
        
        if req.method == "HEAD":
            # HEAD: send headers but no body
            # important: Content-Length must reflect the actual size!
            resp = build_response(200, b"", 
                                  content_type=content_type,
                                  extra_headers=extra_headers)
            # Correct Content-Length for HEAD
            resp = resp.replace(
                b"Content-Length: 0\r\n", 
                f"Content-Length: {len(content)}\r\n".encode("ascii")
            )
            conn.sendall(resp)
            log(f"    → 200 OK (HEAD) {format_bytes(len(content))}", "INFO")
        else:
            # GET: send headers + body
            resp = build_response(200, content, 
                                  content_type=content_type,
                                  extra_headers=extra_headers)
            conn.sendall(resp)
            log(f"    → 200 OK {format_bytes(len(content))}", "INFO")
    
    except TimeoutError:
        log(f"    → Timeout reading request", "WARN")
    except ValueError as e:
        log(f"    → Invalid request: {e}", "WARN")
        try:
            resp = build_response(400, b"Bad Request\n", 
                                  extra_headers={"X-Backend": backend_id, "X-Served-By": backend_id})
            conn.sendall(resp)
        except Exception:
            pass
    except Exception as e:
        log(f"    → Error: {e}", "ERROR")
        try:
            resp = build_response(500, b"Internal Server Error\n",
                                  extra_headers={"X-Backend": backend_id, "X-Served-By": backend_id})
            conn.sendall(resp)
        except Exception:
            pass
    finally:
        conn.close()
        log(f"[-] Connection closed: {client_ip}:{client_port}", "DEBUG")


# ═══════════════════════════════════════════════════════════════════════════════
# Main server function
# ═══════════════════════════════════════════════════════════════════════════════

def serve(host: str, port: int, www_root: str, backend_id: str, threaded: bool) -> None:
    """
    Start the HTTP server.
    
    SOCKET STEPS:
    1. socket()     - Create TCP socket
    2. setsockopt() - Options (SO_REUSEADDR for quick restart)
    3. bind()       - Associate with address and port
    4. listen()     - Activate server mode (listen for connections)
    5. accept()     - Accept connections (blocks until client arrives)
    
    Args:
        host: Address to bind to (0.0.0.0 for all interfaces)
        port: TCP port
        www_root: Directory with static files
        backend_id: Identifier for X-Backend header
        threaded: True for multi-threaded mode
    """
    www_root = os.path.abspath(www_root)
    
    # Verify www directory
    if not os.path.isdir(www_root):
        log(f"ERROR: Directory '{www_root}' does not exist!", "ERROR")
        sys.exit(1)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Create and configure server socket
    # ─────────────────────────────────────────────────────────────────────────
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        # SO_REUSEADDR: allows port reuse immediately after close
        # Without this option, the port remains in TIME_WAIT ~2 minutes
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind: associate socket with (host, port)
        server.bind((host, port))
        
        # Listen: activate server mode, backlog=50 (max waiting connections)
        server.listen(50)
        
        mode = "multi-threaded" if threaded else "single-threaded"
        log(f"HTTP server started on http://{host}:{port}/", "INFO")
        log(f"  www_root: {www_root}", "INFO")
        log(f"  backend_id: {backend_id}", "INFO")
        log(f"  mode: {mode}", "INFO")
        log(f"Press Ctrl+C to stop.", "INFO")
        print()
        
        try:
            while True:
                # Accept: blocks until a connection arrives
                # Returns (new socket for client, client address)
                conn, addr = server.accept()
                
                if threaded:
                    # Multi-threaded mode: each client in separate thread
                    # daemon=True: thread stops when main thread stops
                    t = threading.Thread(
                        target=handle_client, 
                        args=(conn, addr, www_root, backend_id),
                        daemon=True
                    )
                    t.start()
                else:
                    # Single-threaded mode: process sequentially
                    # Only for debugging (one client at a time)
                    handle_client(conn, addr, www_root, backend_id)
        
        except KeyboardInterrupt:
            print()
            log("Server stopped (Ctrl+C)", "INFO")


# ═══════════════════════════════════════════════════════════════════════════════
# Self-test
# ═══════════════════════════════════════════════════════════════════════════════

def selftest() -> int:
    """
    Minimal local test to verify functionality.
    
    Returns:
        0 if test passes, 1 otherwise
    """
    log("Running selftest...", "INFO")
    
    # Preparation - find www directory
    www_root = os.path.join(os.path.dirname(__file__), "..", "..", "www")
    if not os.path.isdir(www_root):
        www_root = os.path.join(os.path.dirname(__file__), "www")
    if not os.path.isdir(www_root):
        log("www directory not found for selftest", "ERROR")
        return 1
    
    host = "127.0.0.1"
    port = get_ephemeral_port()
    
    # Start server in thread
    thread = threading.Thread(
        target=serve, 
        args=(host, port, www_root, "selftest", True),
        daemon=True
    )
    thread.start()
    time.sleep(0.5)
    
    # Test 1: GET /
    try:
        with socket.create_connection((host, port), timeout=2.0) as c:
            c.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
            data = c.recv(4096)
        
        if b"HTTP/1.1 200" in data:
            log("✓ Test GET / → 200 OK", "INFO")
        else:
            log(f"✗ Test GET / → unexpected response", "ERROR")
            return 1
    except Exception as e:
        log(f"✗ Test GET / failed: {e}", "ERROR")
        return 1
    
    # Test 2: GET /not-found → 404
    try:
        with socket.create_connection((host, port), timeout=2.0) as c:
            c.sendall(b"GET /not-found HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
            data = c.recv(4096)
        
        if b"HTTP/1.1 404" in data:
            log("✓ Test GET /not-found → 404 Not Found", "INFO")
        else:
            log(f"✗ Test 404 → unexpected response", "ERROR")
            return 1
    except Exception as e:
        log(f"✗ Test 404 failed: {e}", "ERROR")
        return 1
    
    # Test 3: Directory traversal → 400
    try:
        with socket.create_connection((host, port), timeout=2.0) as c:
            c.sendall(b"GET /../../../etc/passwd HTTP/1.1\r\nHost: localhost\r\n\r\n")
            data = c.recv(4096)
        
        if b"HTTP/1.1 400" in data:
            log("✓ Test directory traversal → 400 Bad Request", "INFO")
        else:
            log(f"✗ Directory traversal was not blocked!", "ERROR")
            return 1
    except Exception as e:
        log(f"✗ Test traversal failed: {e}", "ERROR")
        return 1
    
    log("All tests passed!", "INFO")
    return 0


# ═══════════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Minimal HTTP server with sockets (educational demo) - Week 8",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 demo_http_server.py --port 8080 --www ./www
  python3 demo_http_server.py --host 0.0.0.0 --port 80 --id backend-A
  python3 demo_http_server.py --selftest
        """
    )
    parser.add_argument("--host", default="0.0.0.0",
                        help="Address the server listens on (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080,
                        help="TCP port (default: 8080)")
    parser.add_argument("--www", default=os.path.join(os.path.dirname(__file__), 
                                                       "..", "..", "www"),
                        help="Directory with static files")
    parser.add_argument("--id", dest="backend_id", default="http-server",
                        help="Identifier for X-Backend header")
    parser.add_argument("--mode", choices=["single", "threaded"], default="threaded",
                        help="Execution mode (default: threaded)")
    parser.add_argument("--selftest", action="store_true",
                        help="Run automatic test")
    
    args = parser.parse_args()
    
    if args.selftest:
        return selftest()
    
    serve(args.host, args.port, args.www, args.backend_id, 
          threaded=(args.mode == "threaded"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
