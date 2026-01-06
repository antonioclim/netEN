#!/usr/bin/env python3
"""Week 10 - Minimal FTP server for the Docker laboratory.

This service uses *pyftpdlib* to expose a small FTP server that students can
interrogate with standard clients (ftp, lftp and Python ftplib).

Notes
-----
- This configuration is deliberately simple and suitable for local teaching
  environments only.
- The user credentials are hard-coded for reproducibility.

Default credentials
-------------------
- Username: labftp
- Password: labftp
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


def _prepare_filesystem(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "uploads").mkdir(parents=True, exist_ok=True)
    (root / "downloads").mkdir(parents=True, exist_ok=True)

    welcome = root / "welcome.txt"
    if not welcome.exists():
        welcome.write_text(
            "Welcome to the Week 10 FTP server!\n\n"
            "This container is used for demonstrating FTP control and data channels.\n",
            encoding="utf-8",
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Week 10 FTP server (pyftpdlib)")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address")
    parser.add_argument("--port", type=int, default=2121, help="Control port")
    parser.add_argument(
        "--root",
        default="/home/ftp",
        help="FTP root directory inside the container",
    )
    parser.add_argument(
        "--passive-ports",
        default="30000-30009",
        help="Passive port range, e.g. 30000-30009",
    )
    args = parser.parse_args()

    root = Path(args.root)
    _prepare_filesystem(root)

    user = "labftp"
    password = "labftp"

    authorizer = DummyAuthorizer()
    # Full permissions for teaching (list, read, write, delete, create, rename).
    authorizer.add_user(user, password, str(root), perm="elradfmwMT")

    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "Week 10 FTP server ready."

    # Passive mode configuration.
    try:
        start_s, end_s = args.passive_ports.split("-", 1)
        start, end = int(start_s), int(end_s)
        if start <= 0 or end <= 0 or end < start:
            raise ValueError
        handler.passive_ports = range(start, end + 1)
    except Exception:
        raise SystemExit("Invalid passive port range. Example: 30000-30009")

    # Avoid extremely verbose output unless explicitly requested.
    if os.environ.get("WEEK10_FTP_DEBUG") == "1":
        handler.log_prefix = "%(remote_ip)s:%(remote_port)s -"
    else:
        handler.log_prefix = "%(remote_ip)s -"

    address = (args.host, args.port)
    server = FTPServer(address, handler)

    print("[INFO] Week 10 FTP server starting")
    print(f"[INFO] Bind: {args.host}:{args.port}")
    print(f"[INFO] Root: {root}")
    print("[INFO] User: labftp / Password: labftp")
    print(f"[INFO] Passive ports: {args.passive_ports}")

    server.serve_forever()


if __name__ == "__main__":
    main()
