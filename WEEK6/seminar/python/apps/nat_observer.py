#!/usr/bin/env python3
"""
NAT Observer – Application for observing NAT/PAT translation

This application demonstrates how a "public" server sees connections
from behind a NAT. All connections from private hosts appear
as coming from the NAT router's public IP, differentiated by ports.

Usage:
    # On server (h3 - in the public network)
    python3 nat_observer.py server --bind 203.0.113.2 --port 5000
    
    # On clients (h1, h2 - in the private network)
    python3 nat_observer.py client --host 203.0.113.2 --port 5000 --msg "Hello from h1"

What we observe:
- The server sees all connections as coming from 203.0.113.1 (the NAT IP)
- Each connection has a different source port (the essence of PAT)
- Private addresses (192.168.1.x) are not visible from outside

Revolvix&Hypotheticalandrei
"""

from __future__ import annotations

import argparse
import socket
import sys
from datetime import datetime


def run_server(bind_addr: str, port: int) -> None:
    """
    Starts a TCP server that displays source IP:port for each connection.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind((bind_addr, port))
        sock.listen(5)
        
        print(f"[NAT Observer Server]")
        print(f"Listening on {bind_addr}:{port}")
        print(f"Waiting for connections...")
        print("-" * 60)
        
        while True:
            client_sock, client_addr = sock.accept()
            client_ip, client_port = client_addr
            
            try:
                # Receive the message
                data = client_sock.recv(1024)
                message = data.decode("utf-8", errors="replace").strip()
                
                # Display information
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] Connection from {client_ip}:{client_port}")
                print(f"            Message: {message}")
                print()
                
                # Send confirmation
                response = f"Received from {client_ip}:{client_port}\n"
                client_sock.sendall(response.encode())
                
            finally:
                client_sock.close()
                
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        sock.close()


def run_client(host: str, port: int, message: str) -> None:
    """
    Connect to server and send a message.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    try:
        print(f"[NAT Observer Client]")
        print(f"Connecting to {host}:{port}...")
        
        sock.connect((host, port))
        
        # Display local address (will be the private IP)
        local_addr = sock.getsockname()
        print(f"Local address: {local_addr[0]}:{local_addr[1]}")
        
        # Send the message
        sock.sendall(message.encode())
        print(f"Sent: {message}")
        
        # Receive response
        response = sock.recv(1024).decode("utf-8", errors="replace")
        print(f"Server response: {response}")
        
    except socket.timeout:
        print("Connection timed out!")
        sys.exit(1)
    except ConnectionRefusedError:
        print("Connection refused! Is the server running?")
        sys.exit(1)
    finally:
        sock.close()


def main():
    parser = argparse.ArgumentParser(
        description="NAT Observer - PAT translation demonstration"
    )
    
    subparsers = parser.add_subparsers(dest="mode", help="Operating mode")
    
    # Server mode
    server_parser = subparsers.add_parser("server", help="Start the server")
    server_parser.add_argument(
        "--bind", default="0.0.0.0",
        help="Bind address (default: 0.0.0.0)"
    )
    server_parser.add_argument(
        "--port", type=int, default=5000,
        help="Listening port (default: 5000)"
    )
    
    # Client mode
    client_parser = subparsers.add_parser("client", help="Start the client")
    client_parser.add_argument(
        "--host", required=True,
        help="Server address"
    )
    client_parser.add_argument(
        "--port", type=int, default=5000,
        help="Server port (default: 5000)"
    )
    client_parser.add_argument(
        "--msg", "--message", default="Hello from NAT client",
        help="Message to send"
    )
    
    args = parser.parse_args()
    
    if args.mode == "server":
        run_server(args.bind, args.port)
    elif args.mode == "client":
        run_client(args.host, args.port, args.msg)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
