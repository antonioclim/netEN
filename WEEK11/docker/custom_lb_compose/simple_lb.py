#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
  simple_lb.py – Minimal Load Balancer in Python
═══════════════════════════════════════════════════════════════════════════════

EDUCATIONAL PURPOSE:
  - Demonstrating load balancer implementation from scratch
  - Understanding the round-robin algorithm
  - Comparison with industrial solutions (Nginx)

WARNING:
  - This code is educational, NOT for production!
  - Missing: health checks, retries, keep-alive, buffering, etc.

ARCHITECTURE:
  Client ─► LB (this script) ─► Backend 1/2/3

CONFIGURATION (environment variables):
  - BACKENDS: backend list (e.g.: "web1:80,web2:80,web3:80")
  - ALGO: algorithm (rr, random)
  - PORT: listening port (default: 8080)

═══════════════════════════════════════════════════════════════════════════════
"""
import os
import socket
import threading
import random

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
BACKENDS_STR = os.environ.get("BACKENDS", "web1:80,web2:80,web3:80")
ALGO = os.environ.get("ALGO", "rr")
PORT = int(os.environ.get("PORT", "8080"))

# Parse backends
BACKENDS = []
for item in BACKENDS_STR.split(","):
    item = item.strip()
    if item:
        host, port = item.split(":")
        BACKENDS.append((host, int(port)))

# Index for round-robin
rr_index = 0
rr_lock = threading.Lock()

# ─────────────────────────────────────────────────────────────────────────────
# Selection algorithms
# ─────────────────────────────────────────────────────────────────────────────
def pick_backend_rr():
    """Round-robin: select backends in turn."""
    global rr_index
    with rr_lock:
        backend = BACKENDS[rr_index]
        rr_index = (rr_index + 1) % len(BACKENDS)
    return backend


def pick_backend_random():
    """Random: select randomly."""
    return random.choice(BACKENDS)


def pick_backend():
    """Select backend according to configured algorithm."""
    if ALGO == "random":
        return pick_backend_random()
    return pick_backend_rr()

# ─────────────────────────────────────────────────────────────────────────────
# Proxy logic
# ─────────────────────────────────────────────────────────────────────────────
def forward_request(client_sock):
    """
    Forward request from client to backend and response back.
    
    Simplified implementation:
    1. Read request from client
    2. Select backend
    3. Send request to backend
    4. Read response and send it back to client
    """
    try:
        # 1. Read request from client
        request = b""
        client_sock.settimeout(5.0)
        while True:
            chunk = client_sock.recv(4096)
            if not chunk:
                return
            request += chunk
            if b"\r\n\r\n" in request:
                break
        
        # 2. Select backend
        backend_host, backend_port = pick_backend()
        
        # 3. Connect to backend and send request
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as backend_sock:
            backend_sock.settimeout(5.0)
            backend_sock.connect((backend_host, backend_port))
            backend_sock.sendall(request)
            
            # 4. Read response and send it back
            while True:
                response_chunk = backend_sock.recv(4096)
                if not response_chunk:
                    break
                client_sock.sendall(response_chunk)
    
    except Exception as e:
        # On error, send 502 Bad Gateway
        try:
            error_response = b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 11\r\n\r\nBad Gateway"
            client_sock.sendall(error_response)
        except:
            pass
    
    finally:
        try:
            client_sock.close()
        except:
            pass


def handle_client(client_sock):
    """Handler for threads."""
    forward_request(client_sock)

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print(f"[LB] Starting load balancer on port {PORT}")
    print(f"[LB] Algorithm: {ALGO}")
    print(f"[LB] Backends: {BACKENDS}")
    print("")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", PORT))
        server.listen(128)
        
        print(f"[LB] Listening on 0.0.0.0:{PORT}")
        
        while True:
            client_sock, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(client_sock,), daemon=True)
            thread.start()


if __name__ == "__main__":
    main()


# Revolvix&Hypotheticalandrei
