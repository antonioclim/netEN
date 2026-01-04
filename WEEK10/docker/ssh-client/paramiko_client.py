#!/usr/bin/env python3
"""
SSH client helper for Week 10.

Uses Paramiko to connect to the demo SSH service and run a command.

Author: Computer Networks teaching team, ASE Bucharest.
"""

from __future__ import annotations

import os
import sys
import time
from io import StringIO

import paramiko


def main() -> int:
    # Configuration conexiune
    HOST = os.environ.get("SSH_HOST", "ssh-server")
    PORT = int(os.environ.get("SSH_PORT", "22"))
    USER = os.environ.get("SSH_USER", "labuser")
    PASSWORD = os.environ.get("SSH_PASSWORD", "labpass")
    
    print("=" * 60)
    print("CLIENT SSH CU PARAMIKO")
    print("=" * 60)
    print(f"Host: {HOST}:{PORT}")
    print(f"User: {USER}")
    print()
    
    # Creation client SSH
    client = paramiko.SSHClient()
    
    # Accepta chei newithnoswithte (doar for laborator!)
    # In productie: folositi known_hosts or verification manuala
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Conectare
        print("[1] Conectare SSH...")
        start = time.perf_counter()
        client.connect(
            hostname=HOST,
            port=PORT,
            username=USER,
            password=PASSWORD,
            timeout=10,
            look_for_keys=False,
            allow_agent=False
        )
        elapsed = (time.perf_counter() - start) * 1000
        print(f"    ✓ Conectat in {elapsed:.1f} ms")
        print()
        
        # Exewithtion comenzi
        print("[2] Executie comenzi...")
        commands = [
            ("hostname", "Numele hostului"),
            ("uname -a", "Informatii sistem"),
            ("whoami", "Utilizator curent"),
            ("pwd", "Director curent"),
            ("ls -la /home/labuser", "Continut home"),
        ]
        
        for cmd, description in commands:
            stfrom, stdout, stderr = client.exec_command(cmd)
            output = stdout.read().decode("utf-8").strip()
            error = stderr.read().decode("utf-8").strip()
            
            print(f"    [{description}]")
            print(f"    $ {cmd}")
            if output:
                for line in output.split("\n")[:5]:  # max 5 linii
                    print(f"      {line}")
            if error:
                print(f"      (stderr) {error}")
            print()
        
        # Transfer filee with SFTP
        print("[3] Transfer filee (SFTP)...")
        sftp = client.open_sftp()
        
        # Creation file local de test
        test_content = f"Test SFTP - {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        test_content += "Generat de Paramiko client\n"
        test_content += "Revolvix&Hypotheticalandrei\n"
        
        # Upload
        remote_path = "/home/labuser/storage/test_upload.txt"
        with sftp.file(remote_path, "w") as f:
            f.write(test_content)
        print(f"    ✓ Upload: {remote_path}")
        
        # Verification
        stat = sftp.stat(remote_path)
        print(f"    ✓ Verificat: {stat.st_size} bytes")
        
        # Download and verification continut
        with sftp.file(remote_path, "r") as f:
            downloaded = f.read().decode("utf-8")
        
        if downloaded == test_content:
            print("    ✓ Continut verificat (match)")
        else:
            print("    ✗ Continut diferit!")
        
        # Listare directoryy
        print()
        print("[4] Listare directory storage...")
        files = sftp.listdir("/home/labuser/storage")
        for f in files:
            print(f"    - {f}")
        
        sftp.close()
        
        print()
        print("=" * 60)
        print("TEST COMPLET ✓")
        print("=" * 60)
        
        return 0
        
    except paramiko.AuthenticationException:
        print("✗ Error autentificare (user/parola incorecte)")
        return 1
    except paramiko.SSHException as e:
        print(f"✗ Error SSH: {e}")
        return 2
    except Exception as e:
        print(f"✗ Error: {e}")
        return 3
    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(main())
