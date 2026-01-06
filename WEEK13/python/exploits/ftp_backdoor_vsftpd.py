#!/usr/bin/env python3
"""Week 13 - FTP backdoor check (educational).

This script is a SAFE, self-contained demonstration that:
  1) connects to an FTP service (control port) and sends a benign login attempt
  2) checks whether an additional, unexpected TCP port is exposed (default: 6200)

Important:
- This is not a real-world exploitation tool.
- The provided Week 13 Docker image exposes port 6200 via a *simulated* stub that
  prints a banner and closes. No command execution is implemented.

Exit codes:
  0  - check completed and backdoor port was reachable
  2  - check completed and backdoor port was NOT reachable
  1  - operational error (network or unexpected failure)
"""

from __future__ import annotations

import argparse
import socket
import sys
import time
from typing import Optional


def recv_line(sock: socket.socket, timeout: float = 2.0) -> str:
    sock.settimeout(timeout)
    data = b""
    try:
        while b"\n" not in data and len(data) < 4096:
            chunk = sock.recv(1024)
            if not chunk:
                break
            data += chunk
    except socket.timeout:
        pass
    return data.decode(errors="replace").strip()


def tcp_connect(host: str, port: int, timeout: float = 3.0) -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect((host, port))
    return s


def ftp_probe(host: str, ftp_port: int) -> str:
    with tcp_connect(host, ftp_port, timeout=3.0) as s:
        banner = recv_line(s, timeout=2.0)

        # Minimal, harmless dialogue. Some FTP servers will accept the commands
        # and respond with error codes, which is fine for this demonstration.
        for cmd in ("USER demo:)\r\n", "PASS demo\r\n", "QUIT\r\n"):
            try:
                s.sendall(cmd.encode())
                _ = recv_line(s, timeout=1.0)
            except Exception:
                break

        return banner


def backdoor_check(host: str, backdoor_port: int, command: Optional[str]) -> str:
    with tcp_connect(host, backdoor_port, timeout=3.0) as s:
        banner = recv_line(s, timeout=2.0)
        if command:
            # For the Week 13 lab this will not be executed, but we send it to
            # illustrate how client input could be observed.
            try:
                s.sendall((command + "\n").encode())
                time.sleep(0.2)
            except Exception:
                pass
        return banner


def main() -> int:
    parser = argparse.ArgumentParser(description="Week 13 - FTP backdoor check (educational)")
    parser.add_argument("--target", required=True, help="Target host (use 127.0.0.1 for the local Docker lab)")
    parser.add_argument("--ftp-port", type=int, default=21, help="FTP control port (default: 21)")
    parser.add_argument("--backdoor-port", type=int, default=6200, help="Backdoor check port (default: 6200)")
    parser.add_argument("--command", default=None, help="Optional string to send to the backdoor port (not executed)")
    args = parser.parse_args()

    print("=" * 72)
    print("Week 13 - FTP backdoor check (educational)")
    print("=" * 72)
    print(f"Target: {args.target}")
    print(f"FTP control port: {args.ftp_port}")
    print(f"Backdoor port: {args.backdoor_port}")
    if args.command:
        print(f"Command to send: {args.command!r} (educational, not executed)")
    print()

    try:
        ftp_banner = ftp_probe(args.target, args.ftp_port)
        if ftp_banner:
            print(f"[FTP] Banner: {ftp_banner}")
        else:
            print("[FTP] Connected, no banner received (this can happen with some servers)")
    except Exception as exc:
        print(f"[FTP] ERROR: could not connect to {args.target}:{args.ftp_port} ({exc})")
        return 1

    try:
        backdoor_banner = backdoor_check(args.target, args.backdoor_port, args.command)
        if backdoor_banner:
            print(f"[BACKDOOR] Banner: {backdoor_banner}")
        else:
            print("[BACKDOOR] Connected, no banner received")
        print("\nResult: backdoor port is reachable (for the Week 13 lab this is a simulated stub).")

        # Exit 0: reachable backdoor port
        return 0
    except Exception as exc:
        print(f"[BACKDOOR] Not reachable: {args.target}:{args.backdoor_port} ({exc})")
        print("\nResult: backdoor port is not reachable.")
        # Exit 2: check completed, not reachable
        return 2


if __name__ == "__main__":
    sys.exit(main())
