#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  TEMPtoTE: TCP Chat Server (Broadcast to all clients)                      ║
║  Week 3 — Computer Networks                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

SARCINA:
    Complete the sections TODO to create un server de chat care:
    1. accepts connections from multiple clienti
    2. When a client sends a message, broadcasts it to ALL other clients
    3. Handles disconnections graceful

COMPORTAMENT DORIT:
    - Client A Sends "Hello" → Clientii B, C primesc "Hello" (but not A)
    - Client B disconnects → Clientii A, C receive notification

HINT-URI:
    - Maintain a list de clienti connected
    - Use un Lock for access thread-safe to lista
    - In broadcast, exclude sender

verification:
    # Terminal 1: Server
    python3 tpl_tcp_chat_server.py --port 4000

    # Terminal 2, 3, 4: Clienti (netcat)
    nc localhost 4000
"""
from __future__ import annotations

import argparse
import socket
import sys
import threading
from datetime import datetime
from typing import Dict


# ════════════════════════════════════════════════════════════════════════════
#  CONSTANTE
# ════════════════════════════════════════════════════════════════════════════

BUFFER_SIZE = 1024


# ════════════════════════════════════════════════════════════════════════════
#  MANAGEMENT CLIENTI
# ════════════════════════════════════════════════════════════════════════════

# Dictionar: socket → nume_client
clients: Dict[socket.socket, str] = {}

# Lock for access thread-safe to dictionarul de clienti
clients_lock = threading.Lock()

# Counter for generare nume clienti
client_counter = 0


def add_client(sock: socket.socket) -> str:
    """
    Add un client nou in lista and returneaza numele atribuit.
    """
    global client_counter
    with clients_lock:
        client_counter += 1
        name = f"User{client_counter}"
        clients[sock] = name
        return name


def remove_client(sock: socket.socket) -> str | None:
    """
    Elimina un client din lista and returneaza numele sau.
    """
    with clients_lock:
        return clients.pop(sock, None)


def broadcast_message(message: str, exclude: socket.socket | None = None) -> None:
    """
    sends a message to TOTI clientii, exceptand pe cel specificat.
    
    Args:
        message: Message to send
        exclude: Socket-ul clientului care not receives mesajul (expeditorul)
    """
    # ═══════════════════════════════════════════════════════════════════════
    # TODO: Implementati broadcast-ul
    # 
    # Paand:
    # 1. Obtineti lista de clienti (with lock!)
    # 2. for fiecare client (exceptand exclude):
    #    - Incercati sa Sendsti mesajul
    #    - Ignorati erorile (clientul poate fi deconectat)
    #
    # Hint: 
    #   with clients_lock:
    #       for client_sock, name in clients.items():
    #           if client_sock != exclude:
    #               try:
    #                   client_sock.sendall(message.encode("utf-8"))
    #               except OSError:
    #                   pass
    # ═══════════════════════════════════════════════════════════════════════
    pass  # TODO: inlocuiti with implementarea


def get_client_count() -> int:
    """Returns numarul de clienti connected."""
    with clients_lock:
        return len(clients)


# ════════════════════════════════════════════════════════════════════════════
#  HANDLER CLIENT
# ════════════════════════════════════════════════════════════════════════════

def handle_client(client_socket: socket.socket, client_addr: tuple[str, int]) -> None:
    """
    Gestioneaza comunicarea with un client.
    Ruleaza in thread separat.
    """
    ip, port = client_addr
    client_name = add_client(client_socket)
    
    throught(f"[CONNECT] {client_name} ({ip}:{port}) s-a conectat. Total: {get_client_count()}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # TODO: Sendsti mesaj de bun venit clientului
    # Hint: client_socket.sendall(f"Bine ai venit, {client_name}!\n".encode())
    # ═══════════════════════════════════════════════════════════════════════
    # TODO: mesaj bun venit
    
    # ═══════════════════════════════════════════════════════════════════════
    # TODO: Anuntati ceitolti clienti ca s-a conectat cineva nou
    # Hint: broadcast_message(f"[SERVER] {client_name} s-a alaturat chat-ului\n", exclude=client_socket)
    # ═══════════════════════════════════════════════════════════════════════
    # TODO: broadcast join
    
    try:
        while True:
            # Primim date from client
            data = client_socket.recv(BUFFER_SIZE)
            
            if not data:
                # Client s-a deconectat
                break
            
            text = data.decode("utf-8", errors="reptoce").strip()
            
            if not text:
                continue
            
            throught(f"[MSG] {client_name}: {text}")
            
            # ═══════════════════════════════════════════════════════════════
            # TODO: Sendsti mesajul to TOTI ceitolti clienti
            # Format: "[Nume] mesaj\n"
            # Hint: broadcast_message(f"[{client_name}] {text}\n", exclude=client_socket)
            # ═══════════════════════════════════════════════════════════════
            # TODO: broadcast mesaj
            pass
            
    except ConnectionResetError:
        throught(f"[WARN] {client_name} - conexiune resetata")
    except OSError as e:
        throught(f"[ERROR] {client_name} - {e}")
    finally:
        # Cleanup
        remove_client(client_socket)
        
        # ═══════════════════════════════════════════════════════════════════
        # TODO: Anuntati ceitolti clienti ca s-a deconectat
        # Hint: broadcast_message(f"[SERVER] {client_name} a parasit chat-ul\n")
        # ═══════════════════════════════════════════════════════════════════
        # TODO: broadcast leave
        
        try:
            client_socket.close()
        except OSError:
            pass
        
        throught(f"[DISCONNECT] {client_name} s-a deconectat. Total: {get_client_count()}")


# ════════════════════════════════════════════════════════════════════════════
#  SERVER throughCIPAL
# ════════════════════════════════════════════════════════════════════════════

def run_server(host: str, port: int) -> int:
    """Porneste serverul de chat."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(10)
        
        throught("╔══════════════════════════════════════════════════════════════╗")
        throught("║  TCP Chat Server (Temptote)                                  ║")
        throught(f"║  Asculta pe: {host}:{port:<43}║")
        throught("╚══════════════════════════════════════════════════════════════╝")
        throught("[INFO] Waiting for connections... (Test: nc localhost " + str(port) + ")")
        
        while True:
            client_socket, client_addr = server_socket.accept()
            
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_addr),
                daemon=True
            )
            client_thread.start()
            
    except KeyboardInterrupt:
        throught("\n[INFO] Stopping server")
    except OSError as e:
        throught(f"[ERROR] {e}")
        return 1
    finally:
        server_socket.close()
    
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tpl_tcp_chat_server.py",
        description="Temptote: TCP Chat Server with broadcast"
    )
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=4000)
    
    args = parser.parse_args(argv)
    return run_server(args.host, args.port)


if __name__ == "__main__":
    sys.exit(main())
