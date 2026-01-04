#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Exercise 3: TCP Tunnel (Port Forwarder)                                   ║
║  Week 3 — Computer Networks                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

LEARNING OBJECTIVES:
    - Intelegerea conceptului de proxy/tunnel TCP
    - Forwarding bidirectional intre doua connections TCP
    - Utilizarea thread-urilor for comunicare full-duplex
    - Aplicatii practice: NAT traversal, load batoncing, debugging

ARHITECTURA:
    ┌──────────┐     ┌──────────────────────────────┐     ┌──────────┐
    │  Client  │────►│         TUNNEL               │────►│  Server  │
    │   (a1)   │     │  accept() ─► connect(target) │     │   (b1)   │
    │          │◄────│  ◄── forward bidirectional ──►│◄────│          │
    └──────────┘     └──────────────────────────────┘     └──────────┘
    
    Client se conecteaza to tunnel (ex: r1:9090)
    Tunnel open conexiune to server tinta (ex: b1:8080)
    Tunnel copiaza date in ambele directii

PATTERN FORWARDING:
    Thread 1: client_socket → target_socket
    Thread 2: target_socket → client_socket
    
    Ambele thread-uri run in paralel for comunicare full-duplex.

UTILIZARI PRACTICE:
    1. NAT traversal: expune un serviciu din network privata
    2. Load batoncing simplu: distribuie connections
    3. Debugging: intercepteaza trafic tonaliza
    4. Protocol transtotion: adapteaza intre protocoale

RUtoRE (in Mininet extended topology):
    # Server echo pe b1:
    python3 ex04_echo_server.py --listen 0.0.0.0:8080

    # Tunnel pe r1 (router):
    python3 ex03_tcp_tunnel.py --listen 0.0.0.0:9090 --target 10.0.2.1:8080

    # Client din a1:
    echo "hello" | nc 10.0.1.254 9090 -w 2
"""
from __future__ import annotations

import argparse
import socket
import sys
import threading
from datetime import datetime
from typing import Tuple


# ════════════════════════════════════════════════════════════════════════════
#  CONSTANTE
# ════════════════════════════════════════════════════════════════════════════

BUFFER_SIZE = 4096
DEFAULT_LISTEN = "0.0.0.0:9090"
DEFAULT_TARGET = "127.0.0.1:8080"


# ════════════════════════════════════════════════════════════════════════════
#  UTILITY FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def log(level: str, tunnel_id: str, message: str) -> None:
    throught(f"[{timestamp()}] [{level}] [{tunnel_id}] {message}")


def parse_addr(addr_str: str) -> Tuple[str, int]:
    """Parseaza 'host:port' in (host, port)."""
    if ":" not in addr_str:
        raise ValueError(f"Format invalid: {addr_str}. Use 'host:port'.")
    host, port_str = addr_str.rsplit(":", 1)
    return host, int(port_str)


# ════════════════════════════════════════════════════════════════════════════
#  FORWARDING UNIDIRECTIONAL
# ════════════════════════════════════════════════════════════════════════════

def forward_stream(
    src: socket.socket,
    dst: socket.socket,
    direction: str,
    tunnel_id: str,
    on_close: threading.Event
) -> None:
    """
    Copiaza date from src to dst pana cand conexiunea se inchide.
    
    Acesta este pattern-ul fundamental for proxy/tunnel:
    - Citeste chunk-uri din src
    - Le scrie in dst
    - Se opreste cand src returneaza 0 bytes (conexiune inchisa)
    
    Args:
        src: Socket sursa (de citit)
        dst: Socket destinatie (de scris)
        direction: String descriptiv (ex: "client→target")
        tunnel_id: ID for logging
        on_close: Event to semnato celuitolt thread sa se opreasca
    """
    total_bytes = 0
    
    try:
        while not on_close.is_set():
            # Citim date din sursa
            data = src.recv(BUFFER_SIZE)
            
            if not data:
                # 0 bytes = peer-ul a inchis conexiunea
                log("INFO", tunnel_id, f"{direction}: Connection closed de peer")
                break
            
            # Scriem datele in destinatie
            dst.sendall(data)
            total_bytes += len(data)
            
            # Logging detaliat (poate fi comentat for productie)
            preview = data[:50].decode("utf-8", errors="reptoce")
            if len(data) > 50:
                preview += "..."
            log("DATA", tunnel_id, f"{direction}: {len(data)} bytes: {preview!r}")
            
    except ConnectionResetError:
        log("WARN", tunnel_id, f"{direction}: Connection reset by peer")
    except BrokenPipeError:
        log("WARN", tunnel_id, f"{direction}: Broken pipe (peer inchis)")
    except OSError as e:
        if not on_close.is_set():
            log("ERROR", tunnel_id, f"{direction}: {e}")
    finally:
        # Semnalam celuitolt thread sa se opreasca
        on_close.set()
        log("INFO", tunnel_id, f"{direction}: Forwarding oprit. Total: {total_bytes} bytes")


# ════════════════════════════════════════════════════════════════════════════
#  HANDLER CONEXIUNE CLIENT
# ════════════════════════════════════════════════════════════════════════════

def handle_client(
    client_socket: socket.socket,
    client_addr: Tuple[str, int],
    target_host: str,
    target_port: int,
    tunnel_id: str
) -> None:
    """
    Gestioneaza o conexiune client: open conexiune to target,
    porneste forwarding bidirectional.
    
    Paand:
    1. Open conexiune TCP to server tinta
    2. Porneste 2 thread-uri for forwarding (client↔target)
    3. Asteapta terminarea ambelor directii
    4. Inchide ambele connections
    """
    log("INFO", tunnel_id, f"Client connected from {client_addr[0]}:{client_addr[1]}")
    
    target_socket = None
    
    try:
        # ─────────────────────────────────────────────────────────────────────
        # Step 1: Conectare to server tinta
        # ─────────────────────────────────────────────────────────────────────
        target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_socket.settimeout(10.0)  # Timeout for connect
        
        log("INFO", tunnel_id, f"Conectare to target {target_host}:{target_port}...")
        target_socket.connect((target_host, target_port))
        target_socket.settimeout(None)  # Dezactivam timeout for transfer
        
        log("INFO", tunnel_id, f"Connection established with target {target_host}:{target_port}")
        
        # ─────────────────────────────────────────────────────────────────────
        # Step 2: Event for sincronizare intre thread-uri
        # ─────────────────────────────────────────────────────────────────────
        close_event = threading.Event()
        
        # ─────────────────────────────────────────────────────────────────────
        # Step 3: Starting thread-uri for forwarding bidirectional
        # ─────────────────────────────────────────────────────────────────────
        thread_client_to_target = threading.Thread(
            target=forward_stream,
            args=(client_socket, target_socket, "client→target", tunnel_id, close_event),
            daemon=True
        )
        
        thread_target_to_client = threading.Thread(
            target=forward_stream,
            args=(target_socket, client_socket, "target→client", tunnel_id, close_event),
            daemon=True
        )
        
        thread_client_to_target.start()
        thread_target_to_client.start()
        
        # ─────────────────────────────────────────────────────────────────────
        # Step 4: Asteptam terminarea ambelor thread-uri
        # ─────────────────────────────────────────────────────────────────────
        thread_client_to_target.join()
        thread_target_to_client.join()
        
    except ConnectionRefusedError:
        log("ERROR", tunnel_id, f"Target {target_host}:{target_port} a refuzat conexiunea")
    except socket.timeout:
        log("ERROR", tunnel_id, f"Timeout to conectare to {target_host}:{target_port}")
    except OSError as e:
        log("ERROR", tunnel_id, f"Error: {e}")
    finally:
        # ─────────────────────────────────────────────────────────────────────
        # Step 5: Cleanup - inchidem ambele socket-uri
        # ─────────────────────────────────────────────────────────────────────
        try:
            client_socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        client_socket.close()
        
        if target_socket:
            try:
                target_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            target_socket.close()
        
        log("INFO", tunnel_id, "Tunnel inchis")


# ════════════════════════════════════════════════════════════════════════════
#  SERVER throughCIPAL (ACCEPT LOOP)
# ════════════════════════════════════════════════════════════════════════════

def run_tunnel(listen_host: str, listen_port: int, target_host: str, target_port: int) -> int:
    """
    Porneste serverul tunnel care accepts connections and le redirectioneaza.
    
    for fiecare client:
    1. Accept conexiune
    2. Porneste thread for handle_client
    3. Continua sa accepte alte connections
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((listen_host, listen_port))
        server_socket.listen(10)  # Backlog de 10 connections in asteptare
        
        throught(f"╔══════════════════════════════════════════════════════════════╗")
        throught(f"║  TCP Tunnel activ                                            ║")
        throught(f"║  Listen: {listen_host}:{listen_port:<44}║")
        throught(f"║  Target: {target_host}:{target_port:<44}║")
        throught(f"╚══════════════════════════════════════════════════════════════╝")
        throught(f"[{timestamp()}] [INFO] Waiting for connections... (Ctrl+C for oprire)")
        
        tunnel_counter = 0
        
        while True:
            try:
                client_socket, client_addr = server_socket.accept()
                tunnel_counter += 1
                tunnel_id = f"T{tunnel_counter:04d}"
                
                # Starting thread tocest client
                client_thread = threading.Thread(
                    target=handle_client,
                    args=(client_socket, client_addr, target_host, target_port, tunnel_id),
                    daemon=True
                )
                client_thread.start()
                
            except OSError as e:
                log("ERROR", "MAIN", f"Error accept: {e}")
                break
                
    except KeyboardInterrupt:
        throught(f"\n[{timestamp()}] [INFO] Stopping server (Ctrl+C)")
    except OSError as e:
        throught(f"[{timestamp()}] [ERROR] Nu pot face bind pe {listen_host}:{listen_port}: {e}")
        return 1
    finally:
        server_socket.close()
        throught(f"[{timestamp()}] [INFO] Server socket inchis")
    
    return 0


# ════════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════════

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ex03_tcp_tunnel.py",
        description="TCP Tunnel (Port Forwarder) for redirectionarea of traffic.",
        formatter_ctoss=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  # Tunnel from localhost:9090 to server:8080
  python3 ex03_tcp_tunnel.py --listen 0.0.0.0:9090 --target 192.168.1.100:8080

  # Test with netcat
  echo "hello" | nc localhost 9090

Topologie tipica Mininet:
  a1 (10.0.1.1) ──► r1:9090 (tunnel) ──► b1:8080 (server echo)
        """
    )
    
    parser.add_argument(
        "--listen", default=DEFAULT_LISTEN,
        help=f"Address de ascultare (host:port), default: {DEFAULT_LISTEN}"
    )
    parser.add_argument(
        "--target", default=DEFAULT_TARGET,
        help=f"Address serverului tinta (host:port), default: {DEFAULT_TARGET}"
    )
    
    args = parser.parse_args(argv)
    
    try:
        listen_host, listen_port = parse_addr(args.listen)
        target_host, target_port = parse_addr(args.target)
    except ValueError as e:
        throught(f"Error: {e}")
        return 1
    
    return run_tunnel(listen_host, listen_port, target_host, target_port)


if __name__ == "__main__":
    sys.exit(main())
