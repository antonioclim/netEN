#!/usr/bin/env python3
"""Week 10 - Paramiko SSH client demo.

This script is executed inside the *ssh-client* container. It connects to the
*ssh-server* container and runs a small set of commands.

The goal is to demonstrate:
- TCP connection to port 22
- SSH handshake and authentication
- Remote command execution

Credentials
-----------
- Username: labuser
- Password: labpass
"""

from __future__ import annotations

import sys
import time

import paramiko


def main() -> int:
    host = "ssh-server"
    port = 22
    username = "labuser"
    password = "labpass"

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("[INFO] Connecting to SSH server...")
    for attempt in range(1, 6):
        try:
            client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                look_for_keys=False,
                allow_agent=False,
                timeout=5,
            )
            break
        except Exception as exc:
            if attempt == 5:
                print(f"[ERROR] Failed to connect after {attempt} attempts: {exc}")
                return 1
            print(f"[WARN] Attempt {attempt}/5 failed: {exc}")
            time.sleep(1)

    print("[OK] SSH connection established")

    commands = [
        "whoami",
        "uname -a",
        "pwd",
        "ls -la /home/labuser/storage",
        "echo 'hello from ssh-client' > /home/labuser/storage/hello_from_paramiko.txt",
        "ls -la /home/labuser/storage",
    ]

    for cmd in commands:
        print(f"\n[CMD] {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd)
        _ = stdin  # unused
        out = stdout.read().decode("utf-8", errors="replace").strip()
        err = stderr.read().decode("utf-8", errors="replace").strip()

        if out:
            print(out)
        if err:
            print("[STDERR]")
            print(err)

    client.close()
    print("\n[OK] SSH demo finished")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
