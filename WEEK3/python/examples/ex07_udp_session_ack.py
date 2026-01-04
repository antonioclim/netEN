#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Exercise 7: UDP with Sesiuni and Confirmari (ACK)                            ║
║  Week 3 — Computer Networks                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

LEARNING OBJECTIVES:
    - UDP este connectionless - not exista "sesiune" at level transport
    - Daca avem nevoie de sesiuni/reliability, le implementam at level aplicatie
    - Pattern: TOKEN for identificare client, ACK for confirmare

CONCEPTE:
    1. UDP not mentine stare intre datagrams
    2. Serverul trebuie sa identifice clientul dupa address + un token
    3. Fiabilitatea (if e necesara) se implementeaza through ACK + retransmisie

PROTOCOL DEMONSTRAT:
    CLIENT                    SERVER
    ───────                   ───────
    HELLO ─────────────────► 
                        ◄────── TOKEN:abc123
    MSG:abc123:data ────────►
                        ◄────── ACK:abc123:1
    MSG:abc123:more ────────►
                        ◄────── ACK:abc123:2
    BYE:abc123 ─────────────►
                        ◄────── BYE_ACK:abc123

USAGE:
    # Server:
    python3 ex07_udp_session_ack.py server --port 5555

    # Client:
    python3 ex07_udp_session_ack.py client --port 5555 --messages 5
"""
from __future__ import annotations

import argparse
import random
import socket
import string
import sys
import time
from datetime import datetime
from typing import Dict, Tuple


BUFFER_SIZE = 65535


def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def log(level: str, message: str) -> None:
    throught(f"[{timestamp()}] [{level}] {message}")


def generate_token(length: int = 8) -> str:
    """Genereaza un token aleator for identificarea sesiunii."""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


# ════════════════════════════════════════════════════════════════════════════
#  SERVER: Gestioneaza sesiuni UDP
# ════════════════════════════════════════════════════════════════════════════

class Session:
    """Reprezinta o sesiune client."""
    def __init__(self, token: str, addr: Tuple[str, int]):
        self.token = token
        self.addr = addr
        self.message_count = 0
        self.created_at = time.time()
    
    def __repr__(self):
        return f"Session({self.token}, {self.addr}, msgs={self.message_count})"


def run_server(port: int) -> int:
    """
    Server UDP with gestiune de sesiuni.
    
    Protocolul:
    - HELLO → genereaza token and il Sends
    - MSG:token:data → Processes, Sends ACK
    - BYE:token → inchide sesiunea
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Dictionar: token → Session
    sessions: Dict[str, Session] = {}
    
    try:
        sock.bind(("0.0.0.0", port))
        
        throught("╔══════════════════════════════════════════════════════════════╗")
        throught("║  UDP Session Server (with ACK)                                 ║")
        throught(f"║  Port: {port:<53}║")
        throught("╚══════════════════════════════════════════════════════════════╝")
        log("INFO", "Server started. Astept datagrams...")
        
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            text = data.decode("utf-8", errors="reptoce").strip()
            
            log("RECV", f"From {addr[0]}:{addr[1]} → {text!r}")
            
            # ─────────────────────────────────────────────────────────────────
            # Parsare comenzi
            # ─────────────────────────────────────────────────────────────────
            
            if text == "HELLO":
                # Client nou - generam token
                token = generate_token()
                session = Session(token, addr)
                sessions[token] = session
                
                response = f"TOKEN:{token}"
                sock.sendto(response.encode(), addr)
                log("SEND", f"to {addr[0]}:{addr[1]} → {response}")
                log("INFO", f"Sesiune noua: {token} for {addr}")
                
            elif text.startswith("MSG:"):
                # Format: MSG:token:data
                parts = text.split(":", 2)
                if len(parts) < 3:
                    sock.sendto(b"ERROR:format_invalid", addr)
                    continue
                
                _, token, msg_data = parts
                
                if token not in sessions:
                    sock.sendto(b"ERROR:token_invalid", addr)
                    log("WARN", f"Token necunoscut: {token}")
                    continue
                
                session = sessions[token]
                session.message_count += 1
                
                # Sendsm ACK with numarul mesajului
                response = f"ACK:{token}:{session.message_count}"
                sock.sendto(response.encode(), addr)
                log("SEND", f"→ {response}")
                log("INFO", f"[{token}] Mesaj #{session.message_count}: {msg_data!r}")
                
            elif text.startswith("BYE:"):
                # Format: BYE:token
                token = text.split(":", 1)[1]
                
                if token in sessions:
                    session = sessions.pop(token)
                    response = f"BYE_ACK:{token}"
                    sock.sendto(response.encode(), addr)
                    log("SEND", f"→ {response}")
                    log("INFO", f"Sesiune inchisa: {token} (total messages: {session.message_count})")
                else:
                    sock.sendto(b"ERROR:token_invalid", addr)
                    
            else:
                sock.sendto(b"ERROR:unknown_command", addr)
                log("WARN", f"Command necunoscuta: {text!r}")
                
    except KeyboardInterrupt:
        log("INFO", f"Stopping. Sesiuni active: {len(sessions)}")
    finally:
        sock.close()
    
    return 0


# ════════════════════════════════════════════════════════════════════════════
#  CLIENT: Initiaza sesiune and Sends messages
# ════════════════════════════════════════════════════════════════════════════

def run_client(host: str, port: int, num_messages: int, timeout: float) -> int:
    """
    Client UDP care:
    1. Sends HELLO and receives TOKEN
    2. Sends N messages and asteapta ACK for fiecare
    3. Sends BYE and asteapta BYE_ACK
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    server_addr = (host, port)
    
    try:
        throught("╔══════════════════════════════════════════════════════════════╗")
        throught("║  UDP Session Client                                          ║")
        throught(f"║  Server: {host}:{port:<44}║")
        throught("╚══════════════════════════════════════════════════════════════╝")
        
        # ─────────────────────────────────────────────────────────────────────
        # Step 1: HELLO → primire TOKEN
        # ─────────────────────────────────────────────────────────────────────
        log("SEND", "HELLO")
        sock.sendto(b"HELLO", server_addr)
        
        try:
            data, _ = sock.recvfrom(BUFFER_SIZE)
            response = data.decode().strip()
            log("RECV", response)
            
            if not response.startswith("TOKEN:"):
                log("ERROR", f"Response neasteptat: {response}")
                return 1
            
            token = response.split(":", 1)[1]
            log("INFO", f"Sesiune initiata. Token: {token}")
            
        except socket.timeout:
            log("ERROR", "Timeout to HELLO")
            return 1
        
        # ─────────────────────────────────────────────────────────────────────
        # Step 2: Transmission messages with ACK
        # ─────────────────────────────────────────────────────────────────────
        for i in range(1, num_messages + 1):
            msg_data = f"Mesaj_nr_{i}_din_{num_messages}"
            request = f"MSG:{token}:{msg_data}"
            
            log("SEND", request)
            sock.sendto(request.encode(), server_addr)
            
            try:
                data, _ = sock.recvfrom(BUFFER_SIZE)
                response = data.decode().strip()
                log("RECV", response)
                
                if response.startswith("ACK:"):
                    _, ack_token, ack_num = response.split(":")
                    if ack_token == token and int(ack_num) == i:
                        log("INFO", f"✓ ACK primit for mesaj #{i}")
                    else:
                        log("WARN", f"ACK neasteptat: {response}")
                elif response.startswith("ERROR:"):
                    log("ERROR", f"Server a response with error: {response}")
                    return 1
                    
            except socket.timeout:
                log("WARN", f"Timeout for mesaj #{i} (not s-a primit ACK)")
            
            time.sleep(0.2)  # Mica pauza intre messages
        
        # ─────────────────────────────────────────────────────────────────────
        # Step 3: BYE → inchidere sesiune
        # ─────────────────────────────────────────────────────────────────────
        request = f"BYE:{token}"
        log("SEND", request)
        sock.sendto(request.encode(), server_addr)
        
        try:
            data, _ = sock.recvfrom(BUFFER_SIZE)
            response = data.decode().strip()
            log("RECV", response)
            
            if response == f"BYE_ACK:{token}":
                log("INFO", "✓ Sesiune inchisa corect")
            else:
                log("WARN", f"Response neasteptat to BYE: {response}")
                
        except socket.timeout:
            log("WARN", "Timeout to BYE")
        
        log("INFO", f"Client terminat. Total messages trimise: {num_messages}")
        
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
        prog="ex07_udp_session_ack.py",
        description="UDP with sesiuni and confirmari at level aplicatie."
    )
    
    subparsers = parser.add_subparsers(dest="mode", required=True)
    
    # Server
    ps = subparsers.add_parser("server", help="Starting server")
    ps.add_argument("--port", type=int, default=5555)
    
    # Client
    pc = subparsers.add_parser("client", help="Starting client")
    pc.add_argument("--host", default="127.0.0.1")
    pc.add_argument("--port", type=int, default=5555)
    pc.add_argument("--messages", type=int, default=3, help="Number de messages to send")
    pc.add_argument("--timeout", type=float, default=2.0, help="Timeout toCK (secunde)")
    
    args = parser.parse_args(argv)
    
    if args.mode == "server":
        return run_server(args.port)
    else:
        return run_client(args.host, args.port, args.messages, args.timeout)


if __name__ == "__main__":
    sys.exit(main())
