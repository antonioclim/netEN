#!/usr/bin/env python3
"""
FTP Demo Client - using ftplib (Python standard library)

FTP client for comparison with our pseudo-FTP.

Usage:
    python3 ftp_demo_client.py --host 127.0.0.1 --port 2121 --user test --password 12345 list
    python3 ftp_demo_client.py ... get hello.txt
    python3 ftp_demo_client.py ... put myfile.txt
"""

import argparse
import sys
from ftplib import FTP
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="FTP Demo Client")
    parser.add_argument("--host", default="127.0.0.1", help="Server address")
    parser.add_argument("--port", type=int, default=2121, help="Port")
    parser.add_argument("--user", default="test", help="Username")
    parser.add_argument("--password", default="12345", help="Password")
    parser.add_argument("--local-dir", default="./client-files", help="Local directoryy")
    parser.add_argument("--passive", action="store_true", default=True, 
                        help="Passive mode (default)")
    parser.add_argument("--active", action="store_true", help="Active mode")
    parser.add_argument("command", help="Command: list, get, put, pwd")
    parser.add_argument("argument", nargs="?", help="Argument for command")
    
    args = parser.parse_args()
    
    local_dir = Path(args.local_dir).resolve()
    local_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Connect
        ftp = FTP()
        ftp.connect(args.host, args.port)
        print(f"[CLIENT] Connected to {args.host}:{args.port}")
        
        # Set active/passive mode
        if args.active:
            ftp.set_pasv(False)
            print("[CLIENT] Active mode")
        else:
            ftp.set_pasv(True)
            print("[CLIENT] Passive mode")
        
        # Authentication
        response = ftp.login(args.user, args.password)
        print(f"[CLIENT] Login: {response}")
        
        # Execute command
        cmd = args.command.lower()
        
        if cmd == "list" or cmd == "ls":
            print("[CLIENT] === Directoryy listing ===")
            ftp.retrlines("LIST")
        
        elif cmd == "pwd":
            print(f"[CLIENT] Current directoryy: {ftp.pwd()}")
        
        elif cmd == "get":
            if not args.argument:
                print("Usage: get <filename>")
                return 1
            
            local_path = local_dir / args.argument
            print(f"[CLIENT] Downloading: {args.argument} -> {local_path}")
            
            with open(local_path, "wb") as f:
                ftp.retrbinary(f"RETR {args.argument}", f.write)
            
            print(f"[CLIENT] ✓ Saved: {local_path} ({local_path.stat().st_size} bytes)")
        
        elif cmd == "put":
            if not args.argument:
                print("Usage: put <filename>")
                return 1
            
            local_path = local_dir / args.argument
            if not local_path.is_file():
                print(f"File does not exist: {local_path}")
                return 1
            
            print(f"[CLIENT] Uploading: {local_path}")
            
            with open(local_path, "rb") as f:
                ftp.storbinary(f"STOR {args.argument}", f)
            
            print(f"[CLIENT] ✓ Uploaded: {args.argument}")
        
        else:
            print(f"Unknown command: {cmd}")
            return 1
        
        # Disconnect
        ftp.quit()
        print("[CLIENT] Disconnected")
        
    except Exception as e:
        print(f"[CLIENT] Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
