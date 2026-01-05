#!/usr/bin/env python3
"""
TCP Echo Server/Client for SDN connectivity testing

Simple application for generating TCP traffic and verifying
network policies in SDN topologies.

Week 6 Port Plan:
    TCP_APP_PORT = 9090
    UDP_APP_PORT = 9091
    WEEK_PORT_BASE = 5600 (for custom ports)

Usage:
    # Server
    python3 tcp_echo.py server --bind 10.0.6.12 --port 9090
    
    # Client
    python3 tcp_echo.py client --dst 10.0.6.12 --port 9090 --message "Hello TCP"

Rezolvix&Hypotheticalandrei
"""

from __future__ import annotations

import argparse
import socket
import sys


def run_server(bind_addr: str, port: int) -> None:
    """
    TCP echo server - returns received messages.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind((bind_addr, port))
        sock.listen(5)
        
        print(f"[TCP Echo Server]")
        print(f"Listening on {bind_addr}:{port}")
        print("Press Ctrl+C to stop.")
        print("-" * 40)
        
        while True:
            client_sock, client_addr = sock.accept()
            print(f"Connection from {client_addr[0]}:{client_addr[1]}")
            
            try:
                while True:
                    data = client_sock.recv(1024)
                    if not data:
                        break
                    
                    message = data.decode("utf-8", errors="replace")
                    print(f"  Received: {message.strip()}")
                    
                    # Echo back
                    client_sock.sendall(data)
                    print(f"  Echoed back: {message.strip()}")
                    
            finally:
                client_sock.close()
                print(f"Connection closed.\n")
                
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        sock.close()


def run_client(dst: str, port: int, message: str) -> None:
    """
    TCP client - sends message and displays response.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    
    try:
        print(f"[TCP Echo Client]")
        print(f"Connecting to {dst}:{port}...")
        
        sock.connect((dst, port))
        print(f"Connected!")
        
        # Send
        sock.sendall(message.encode())
        print(f"Sent: {message}")
        
        # Receive echo
        response = sock.recv(1024).decode("utf-8", errors="replace")
        print(f"Received: {response}")
        
        if response.strip() == message.strip():
            print("✓ Echo verified - connection successful!")
        
    except socket.timeout:
        print("✗ Connection timed out!")
        print("  Possible causes:")
        print("  - Server not running")
        print("  - SDN policy blocking traffic")
        print("  - Firewall rules")
        sys.exit(1)
    except ConnectionRefusedError:
        print("✗ Connection refused!")
        sys.exit(1)
    finally:
        sock.close()


def main():
    parser = argparse.ArgumentParser(description="TCP Echo Server/Client")
    subparsers = parser.add_subparsers(dest="mode")
    
    # Server
    srv = subparsers.add_parser("server")
    srv.add_argument("--bind", default="0.0.0.0")
    srv.add_argument("--port", type=int, default=9090)
    
    # Client
    cli = subparsers.add_parser("client")
    cli.add_argument("--dst", required=True)
    cli.add_argument("--port", type=int, default=9090)
    cli.add_argument("--message", default="Hello TCP")
    
    args = parser.parse_args()
    
    if args.mode == "server":
        run_server(args.bind, args.port)
    elif args.mode == "client":
        run_client(args.dst, args.port, args.message)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
