#!/usr/bin/env python3
"""
FTP Demo Server - using pyftpdlib

Example of a real FTP server for comparison with our pseudo-FTP.
Demonstrates standard FTP protocols and commands.

Usage:
    python3 ftp_demo_server.py --host 127.0.0.1 --port 2121 --root ./server-files
"""

import argparse
import sys
from pathlib import Path

try:
    from pyftpdlib.authorizers import DummyAuthorizer
    from pyftpdlib.handlers import FTPHandler
    from pyftpdlib.servers import FTPServer
except ImportError:
    print("Error: pyftpdlib is not installed.")
    print("Install with: pip install pyftpdlib --break-system-packages")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="FTP Demo Server")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address")
    parser.add_argument("--port", type=int, default=2121, help="Port (default: 2121)")
    parser.add_argument("--root", default="./server-files", help="Root directoryy")
    parser.add_argument("--user", default="test", help="Username")
    parser.add_argument("--password", default="12345", help="Password")
    parser.add_argument("--passive-ports", default="60000-60100", 
                        help="Passive port range")
    
    args = parser.parse_args()
    
    # Ensure root directoryy exists
    root_path = Path(args.root).resolve()
    root_path.mkdir(parents=True, exist_ok=True)
    
    # Configure authorisation
    authorizer = DummyAuthorizer()
    
    # Add user with all permissions
    # Permissions: e=cwd, l=list, r=retr, a=appe, d=delete, f=rename, m=mkdir, w=stor
    authorizer.add_user(args.user, args.password, str(root_path), perm="elradfmw")
    
    # Configure handler
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "Pseudo-FTP Demo Server (pyftpdlib)"
    
    # Configure passive ports
    start_port, end_port = map(int, args.passive_ports.split("-"))
    handler.passive_ports = range(start_port, end_port + 1)
    
    # Create and start server
    address = (args.host, args.port)
    server = FTPServer(address, handler)
    
    # Server configuration
    server.max_cons = 256
    server.max_cons_per_ip = 5
    
    print(f"[FTP SERVER] Started on {args.host}:{args.port}")
    print(f"[FTP SERVER] Root: {root_path}")
    print(f"[FTP SERVER] User: {args.user}")
    print(f"[FTP SERVER] Passive ports: {args.passive_ports}")
    print("[FTP SERVER] Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[FTP SERVER] Stopping...")
        server.close_all()


if __name__ == "__main__":
    main()
