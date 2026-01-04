#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Exercise 6: TCP Framing (Delimitare Mesaje)                               ║
║  Week 3 — Computer Networks                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

LEARNING OBJECTIVES:
    - Demonstrarea faptului ca TCP este STREAM, not MESSAGE-oriented
    - Un recv() poate returna: parte dintr-un mesaj, exact un mesaj, sau mai multe
    - Tehnici de framing: delimitator, length-prefix, TLV

PROBLEMA:
    TCP garanteaza livrarea in ordine, dar NOT garanteaza limitele mesajelor!
    
    Client Sends:            Server receives (posibile variante):
    send("HELLO")              recv() → "HELLOWORLD"  (concatenate)
    send("WORLD")              recv() → "HEL"         (fragment)
                               recv() → "LOWORLD"

SOLUTII DE FRAMING:

    1. DELIMITATOR (ex: newline \n, CRLF, NULL byte)
       - Simplu de implementat
       - Delimitatorul not poate aparea in date
       - Folosit de: HTTP headers, SMTP, FTP commands
       
    2. LENGTH-PREFIX (lungime + date)
       - Primele N bytes indica lungimea mesajului
       - Date binare pot contine orice
       - Folosit de: HTTP body (Content-Length), TLS records
       
    3. TLV (Type-Length-Value)
       - Tip (identifica mesajul) + Lungime + Date
       - for protocoale complexe with multiple tipuri de messages
       - Folosit de: ASN.1/BER, protocoale binare custom

USAGE:
    # Terminal 1: Server
    python3 ex06_tcp_framing.py server --port 4444

    # Terminal 2: Client
    python3 ex06_tcp_framing.py client --port 4444
"""
from __future__ import annotations

import argparse
import socket
import struct
import sys
import time
from datetime import datetime


def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def log(level: str, message: str) -> None:
    print(f"[{timestamp()}] [{level}] {message}")


# ════════════════════════════════════════════════════════════════════════════
#  PROBLEMA: NAIVE RECV
# ════════════════════════════════════════════════════════════════════════════

def demo_naive_recv(sock: socket.socket) -> None:
    """
    Demonstreaza problema: recv() not respecta limitele mesajelor.
    """
    log("INFO", "Metoda NAIVA: recv() poate returna orice cantitate de date!")
    
    # Citim ce vine - poate fi incomplet sau concatenat
    data = sock.recv(1024)
    log("RECV", f"Am primit: {data!r}")
    log("WARN", "↑ Acest output poate fi different de mesajele individuale trimise!")


# ════════════════════════════════════════════════════════════════════════════
#  SOLUTIA 1: DELIMITATOR (NEWLINE)
# ════════════════════════════════════════════════════════════════════════════

def recv_with_delimiter(sock: socket.socket, delimiter: bytes = b"\n") -> bytes:
    """
    Receives date pana gaseste delimitatorul.
    Returns mesajul FARA delimitator.
    
    Pattern-ul fundamental for protocoale text-based.
    """
    buffer = b""
    
    while delimiter not in buffer:
        chunk = sock.recv(1)  # Citim byte with byte for simplitate
        if not chunk:
            raise ConnectionError("Connection closed inainte de delimitator")
        buffer += chunk
    
    message, _ = buffer.split(delimiter, 1)
    return message


def recv_lines(sock: socket.socket, count: int, delimiter: bytes = b"\n") -> list[bytes]:
    """Receives `count` messages delimitate."""
    messages = []
    for _ in range(count):
        msg = recv_with_delimiter(sock, delimiter)
        messages.append(msg)
    return messages


def send_with_delimiter(sock: socket.socket, message: bytes, delimiter: bytes = b"\n") -> None:
    """Sends mesaj with delimitator to sfarandt."""
    sock.sendall(message + delimiter)


# ════════════════════════════════════════════════════════════════════════════
#  SOLUTIA 2: LENGTH-PREFIX (4 bytes big-endian)
# ════════════════════════════════════════════════════════════════════════════

def recv_exact(sock: socket.socket, n: int) -> bytes:
    """
    Receives EXACT n bytes.
    Pattern esential for protocoale binare.
    """
    buffer = b""
    while len(buffer) < n:
        remaining = n - len(buffer)
        chunk = sock.recv(remaining)
        if not chunk:
            raise ConnectionError(f"Connection closed. Received {len(buffer)}/{n} bytes.")
        buffer += chunk
    return buffer


def recv_length_prefixed(sock: socket.socket) -> bytes:
    """
    Receives un mesaj with lungime prefixata (4 bytes, big-endian).
    
    Format: [4 bytes lungime][date]
    """
    # Step 1: Citim lungimea (4 bytes)
    length_bytes = recv_exact(sock, 4)
    length = struct.unpack(">I", length_bytes)[0]  # >I = big-endian unsigned int
    
    # Step 2: Citim exact `length` bytes de date
    data = recv_exact(sock, length)
    return data


def send_length_prefixed(sock: socket.socket, message: bytes) -> None:
    """
    Sends mesaj with lungime prefixata.
    """
    length = len(message)
    header = struct.pack(">I", length)  # 4 bytes, big-endian
    sock.sendall(header + message)


# ════════════════════════════════════════════════════════════════════════════
#  SERVER DEMO
# ════════════════════════════════════════════════════════════════════════════

def run_server(port: int) -> int:
    """Server care demonstreaza cele doua tehnici de framing."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind(("0.0.0.0", port))
        server.listen(1)
        
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║  Demo TCP Framing - Server                                   ║")
        print(f"║  Port: {port:<53}║")
        print("╚══════════════════════════════════════════════════════════════╝")
        log("INFO", "Astept client...")
        
        client, addr = server.accept()
        log("CONN", f"Client connected: {addr}")
        
        with client:
            # ─────────────────────────────────────────────────────────────────
            # Demo 1: Reception with DELIMITATOR
            # ─────────────────────────────────────────────────────────────────
            log("INFO", "══ Demo 1: FRAMING CU DELIMITATOR (newline) ══")
            
            for i in range(3):
                msg = recv_with_delimiter(client, b"\n")
                log("RECV", f"Mesaj #{i+1}: {msg.decode()!r}")
            
            client.sendall(b"ACK:delimiter_ok\n")
            
            # ─────────────────────────────────────────────────────────────────
            # Demo 2: Reception with LENGTH-PREFIX
            # ─────────────────────────────────────────────────────────────────
            log("INFO", "══ Demo 2: FRAMING CU LENGTH-PREFIX (4 bytes) ══")
            
            for i in range(3):
                msg = recv_length_prefixed(client)
                log("RECV", f"Mesaj #{i+1}: {msg!r} ({len(msg)} bytes)")
            
            send_length_prefixed(client, b"ACK:length_prefix_ok")
            
        log("INFO", "Demo complete!")
        
    except KeyboardInterrupt:
        log("INFO", "Stopping")
    except OSError as e:
        log("ERROR", f"Error: {e}")
        return 1
    finally:
        server.close()
    
    return 0


# ════════════════════════════════════════════════════════════════════════════
#  CLIENT DEMO
# ════════════════════════════════════════════════════════════════════════════

def run_client(host: str, port: int) -> int:
    """Client care Sends messages with diferite tehnici de framing."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        sock.connect((host, port))
        log("CONN", f"Conectat to {host}:{port}")
        
        # ─────────────────────────────────────────────────────────────────────
        # Demo 1: Transmission with DELIMITATOR
        # ─────────────────────────────────────────────────────────────────────
        log("INFO", "══ Transmission with DELIMITATOR ══")
        
        messages = [b"Hello", b"World", b"From_Client"]
        for i, msg in enumerate(messages, 1):
            send_with_delimiter(sock, msg, b"\n")
            log("SEND", f"Mesaj #{i}: {msg.decode()!r}")
            time.sleep(0.1)  # Mica pauza for demonstratie
        
        # Asteptam ACK
        ack = recv_with_delimiter(sock, b"\n")
        log("RECV", f"Server ACK: {ack.decode()!r}")
        
        # ─────────────────────────────────────────────────────────────────────
        # Demo 2: Transmission with LENGTH-PREFIX
        # ─────────────────────────────────────────────────────────────────────
        log("INFO", "══ Transmission with LENGTH-PREFIX ══")
        
        binary_messages = [
            b"Date binare \x00\x01\x02",
            b"Mesaj with newline\nin interior",
            "Unicode: café ☕ 日本語".encode("utf-8")
        ]
        
        for i, msg in enumerate(binary_messages, 1):
            send_length_prefixed(sock, msg)
            log("SEND", f"Mesaj #{i}: {msg!r} ({len(msg)} bytes)")
            time.sleep(0.1)
        
        # Asteptam ACK
        ack = recv_length_prefixed(sock)
        log("RECV", f"Server ACK: {ack!r}")
        
        log("INFO", "Demo complete!")
        
    except ConnectionRefusedError:
        log("ERROR", f"Nu pot conecta to {host}:{port}")
        return 1
    except OSError as e:
        log("ERROR", f"Error: {e}")
        return 1
    finally:
        sock.close()
    
    return 0


# ════════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════════

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ex06_tcp_framing.py",
        description="Demonstratie tehnici de framing TCP."
    )
    
    subparsers = parser.add_subparsers(dest="mode", required=True)
    
    # Server
    ps = subparsers.add_parser("server", help="Starting server demo")
    ps.add_argument("--port", type=int, default=4444)
    
    # Client
    pc = subparsers.add_parser("client", help="Starting client demo")
    pc.add_argument("--host", default="127.0.0.1")
    pc.add_argument("--port", type=int, default=4444)
    
    args = parser.parse_args(argv)
    
    if args.mode == "server":
        return run_server(args.port)
    else:
        return run_client(args.host, args.port)


if __name__ == "__main__":
    sys.exit(main())
