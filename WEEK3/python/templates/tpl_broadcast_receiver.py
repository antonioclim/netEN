#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  TEMPtoTE: UDP Broadcast Receiver with Timestamp                               ║
║  Week 3 — Computer Networks                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

SARCINA:
    Complete the sections marcate with TODO to create un receiver UDP broadcast
    care afiseaza fiecare mesaj primit with:
    - Number de ordine (counter)
    - Timestamp
    - Address sursei
    - Continutul mesajului

OUTPUT DORIT:
    [#1 @ 2025-03-10 14:32:01.123] From 10.0.0.1:54321 → "HELLO_BCAST #0"
    [#2 @ 2025-03-10 14:32:02.125] From 10.0.0.1:54321 → "HELLO_BCAST #1"
    ...

HINT-URI:
    - Use datetime.now() for timestamp
    - socket.recvfrom() returneaza (data, (ip, port))
    - data.decode("utf-8") converteste bytes in string

verification:
    # Terminal 1: Porniti acest receiver
    python3 tpl_broadcast_receiver.py --port 5007 --count 5

    # Terminal 2: Sendsti messages broadcast
    python3 ../examples/ex01_udp_broadcast.py send --port 5007 --count 5
"""
from __future__ import annotations

import argparse
import socket
import sys
from datetime import datetime


def run_receiver(port: int, count: int) -> int:
    """
    Receiver UDP broadcast with timestamp and counter.
    
    Args:
        port: Portul pe care asculta
        count: Numarul de messages de primit (0 = infinite)
    
    Returns:
        0 for success
    """
    # ═══════════════════════════════════════════════════════════════════════
    # TODO 1: Creati un socket UDP
    # Hint: socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # ═══════════════════════════════════════════════════════════════════════
    sock = None  # TODO: inlocuiti with crearea socket-ului
    
    # ═══════════════════════════════════════════════════════════════════════
    # TODO 2: Activati SO_REUSEADDR for quick restart
    # Hint: sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # ═══════════════════════════════════════════════════════════════════════
    # TODO: adaugati setsockopt aici
    
    # ═══════════════════════════════════════════════════════════════════════
    # TODO 3: Faceti bind pe port (ascultati pe all interfaces)
    # Hint: sock.bind(("", port))
    # ═══════════════════════════════════════════════════════════════════════
    # TODO: adaugati bind aici
    
    print(f"[INFO] Receiver started on port {port}. Waiting for messages broadcast...")
    
    counter = 0
    
    try:
        while count == 0 or counter < count:
            # ═══════════════════════════════════════════════════════════════
            # TODO 4: Primiti o datagrama with recvfrom()
            # recvfrom() returneaza (data, (ip, port))
            # Hint: data, (sender_ip, sender_port) = sock.recvfrom(65535)
            # ═══════════════════════════════════════════════════════════════
            data = b""  # TODO: inlocuiti with recvfrom
            sender_ip = "???"  # TODO: extrageti din rezultatul recvfrom
            sender_port = 0    # TODO: extrageti din rezultatul recvfrom
            
            # ═══════════════════════════════════════════════════════════════
            # TODO 5: Incrementati counter-ul
            # ═══════════════════════════════════════════════════════════════
            # TODO: counter += 1
            
            # ═══════════════════════════════════════════════════════════════
            # TODO 6: Obtineti timestamp-ul curent
            # Hint: datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            # ═══════════════════════════════════════════════════════════════
            ts = "???"  # TODO: inlocuiti with timestamp real
            
            # ═══════════════════════════════════════════════════════════════
            # TODO 7: Decodificati datele din bytes in string
            # Hint: data.decode("utf-8", errors="replace")
            # ═══════════════════════════════════════════════════════════════
            text = "???"  # TODO: decodificati data
            
            # ═══════════════════════════════════════════════════════════════
            # TODO 8: Afisati in formatul cerut
            # Format: [#N @ TIMESTAMP] From IP:PORT → "mesaj"
            # ═══════════════════════════════════════════════════════════════
            print(f"[#{counter} @ {ts}] From {sender_ip}:{sender_port} → {text!r}")
            
    except KeyboardInterrupt:
        print(f"\n[INFO] Stopped by user. Total messages: {counter}")
    finally:
        if sock:
            sock.close()
    
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tpl_broadcast_receiver.py",
        description="Template: UDP Broadcast receiver with timestamp"
    )
    parser.add_argument("--port", type=int, default=5007, help="Port de ascultare")
    parser.add_argument("--count", type=int, default=0, help="Mesaje de primit (0=infinite)")
    
    args = parser.parse_args(argv)
    return run_receiver(args.port, args.count)


if __name__ == "__main__":
    sys.exit(main())
