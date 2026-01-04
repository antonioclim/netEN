#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Exercise 5: TCP Server Multiclient (Thread per Client)                    ║
║  Week 3 — Computer Networks                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

LEARNING OBJECTIVES:
    - Gestionarea mai multor clienti TCP simultaneously
    - Pattern "thread per client" with threading.Thread
    - Sincronizare access to resurse partajate (threading.Lock)
    - Observing the behaviour concurrent in Wireshark

PROBLEMA:
    Un server TCP simplu (accept → recv → send) poate servi doar un client.
    Ceitolti clienti asteapta in coada listen().
    
    Solutia: for fiecare accept(), pornim un thread separat.

ALTERNATIVE to THREADING:
    1. Process per client (multiprocessing) - overhead mare, izotore buna
    2. Event loop (select/epoll) - eficient, complex
    3. Async (asyncio) - modern, necesita async/await

USAGE:
    # Server:
    python3 ex05_tcp_multiclient.py

    # Clienti (in mai multe terminals):
    nc 127.0.0.1 3333
    # Scrieti text, primiti response uppercase

OBSERVATII WIRESHARK:
    - Fiecare client are propriul TCP stream
    - Mesajele sunt independente pe fiecare stream
    - Filter: tcp.port == 3333
"""
from __future__ import annotations

import argparse
import socket
import sys
import threading
from datetime import datetime
from typing import Set


# ════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 3333
BUFFER_SIZE = 1024


# ════════════════════════════════════════════════════════════════════════════
#  LOGGING
# ════════════════════════════════════════════════════════════════════════════

def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def log(level: str, thread_id: str, message: str) -> None:
    print(f"[{timestamp()}] [{level:5s}] [{thread_id:8s}] {message}")


# ════════════════════════════════════════════════════════════════════════════
#  MANAGEMENT CLIENTI
# ════════════════════════════════════════════════════════════════════════════

class ClientManager:
    """
    Gestioneaza lista de clienti connected.
    Thread-safe through utilizarea unui Lock.
    """
    
    def __init__(self):
        self.clients: Set[socket.socket] = set()
        self.lock = threading.Lock()
        self.client_counter = 0
    
    def add(self, client: socket.socket) -> int:
        """Add un client and returneaza ID-ul sau."""
        with self.lock:
            self.client_counter += 1
            self.clients.add(client)
            return self.client_counter
    
    def remove(self, client: socket.socket) -> None:
        """Elimina un client din lista."""
        with self.lock:
            self.clients.discard(client)
    
    def count(self) -> int:
        """Returns numarul de clienti connected."""
        with self.lock:
            return len(self.clients)
    
    def broadcast(self, message: bytes, exclude: socket.socket = None) -> None:
        """Sends mesaj to toti clientii (for exercitiul chat)."""
        with self.lock:
            for client in self.clients:
                if client != exclude:
                    try:
                        client.sendall(message)
                    except OSError:
                        pass


# Instanta globala for managementul clientilor
manager = ClientManager()


# ════════════════════════════════════════════════════════════════════════════
#  HANDLER CLIENT
# ════════════════════════════════════════════════════════════════════════════

def handle_client(client_socket: socket.socket, client_addr: tuple[str, int]) -> None:
    """
    Handler for un client individual.
    Ruleaza in thread separat.
    
    Comportament:
    - Receives messages from client
    - Raspunde with mesajul in uppercase
    - Se opreste cand clientul inchide conexiunea
    """
    ip, port = client_addr
    client_id = manager.add(client_socket)
    thread_id = f"C{client_id:05d}"
    
    log("CONN", thread_id, f"Client connected from {ip}:{port}")
    log("INFO", thread_id, f"Total clients connected: {manager.count()}")
    
    try:
        # Mesaj de bun venit
        welcome = f"Welcome! You are client #{client_id}. Type something:\n"
        client_socket.sendall(welcome.encode("utf-8"))
        
        while True:
            # ─────────────────────────────────────────────────────────────────
            # recv() blocks until receives date sau conexiunea se inchide
            # ─────────────────────────────────────────────────────────────────
            data = client_socket.recv(BUFFER_SIZE)
            
            if not data:
                # 0 bytes = peer-ul closed connection (FIN)
                log("INFO", thread_id, f"Client {ip}:{port} closed connection")
                break
            
            # Decodificare and procesare
            text = data.decode("utf-8", errors="replace").strip()
            log("RECV", thread_id, f"← {text!r}")
            
            # Response: uppercase
            response = data.upper()
            client_socket.sendall(response)
            log("SEND", thread_id, f"→ {response.decode('utf-8', errors='replace').strip()!r}")
            
    except ConnectionResetError:
        log("WARN", thread_id, f"Connection reset by {ip}:{port}")
    except BrokenPipeError:
        log("WARN", thread_id, f"Broken pipe for {ip}:{port}")
    except OSError as e:
        log("ERROR", thread_id, f"Error: {e}")
    finally:
        # Cleanup
        manager.remove(client_socket)
        try:
            client_socket.close()
        except OSError:
            pass
        log("DISC", thread_id, f"Client disconnected. Remaining: {manager.count()}")


# ════════════════════════════════════════════════════════════════════════════
#  SERVER MAIN
# ════════════════════════════════════════════════════════════════════════════

def run_server(host: str, port: int) -> int:
    """
    Porneste serverul TCP multiclient.
    
    Bucto throughcipala:
    1. accept() - asteapta conexiune
    2. Porneste thread for handle_client
    3. Revine to accept()
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # ─────────────────────────────────────────────────────────────────────
        # Optiuni socket
        # ─────────────────────────────────────────────────────────────────────
        # SO_REUSEADDR: permite restart rapid (not asteapta TIME_WAIT)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind and listen
        server_socket.bind((host, port))
        server_socket.listen(10)  # Backlog: max 10 connections in asteptare
        
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║  TCP Server Multiclient (Thread per Client)                  ║")
        print(f"║  Listening on: {host}:{port:<43}║")
        print("╚══════════════════════════════════════════════════════════════╝")
        log("INFO", "MAIN", f"Server started. Waiting for connections...")
        log("INFO", "MAIN", "Test: nc {host} {port}".format(host=host, port=port))
        
        while True:
            # ─────────────────────────────────────────────────────────────────
            # accept() blocks until When a client se conecteaza
            # Returns (socket_nou, (ip, port))
            # ─────────────────────────────────────────────────────────────────
            client_socket, client_addr = server_socket.accept()
            
            # Starting thread tocest client
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_addr),
                daemon=True  # Thread se opreste cand procesul throughcipal se opreste
            )
            client_thread.start()
            
    except KeyboardInterrupt:
        print()
        log("INFO", "MAIN", "Stopping server (Ctrl+C)")
    except OSError as e:
        log("ERROR", "MAIN", f"Nu pot asculta pe {host}:{port}: {e}")
        return 1
    finally:
        server_socket.close()
        log("INFO", "MAIN", "Server closed")
    
    return 0


# ════════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════════

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ex05_tcp_multiclient.py",
        description="Server TCP multiclient with thread per client."
    )
    parser.add_argument(
        "--host", default=DEFAULT_HOST,
        help=f"Address IP de ascultare (default: {DEFAULT_HOST})"
    )
    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT,
        help=f"Portul de ascultare (default: {DEFAULT_PORT})"
    )
    args = parser.parse_args(argv)
    
    return run_server(args.host, args.port)


if __name__ == "__main__":
    sys.exit(main())
