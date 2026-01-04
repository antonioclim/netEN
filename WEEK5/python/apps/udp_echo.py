#!/usr/bin/env python3
"""
UDP Echo Server & Client — demonstration protocol Layer 3/4
===========================================================
Pereche client-server UDP for demonstrarea comunicarii in network.

usage Server:
    python udp_echo.py server --port 9999
    python udp_echo.py server --port 9999 --verbose

usage Client:
    python udp_echo.py client --host 127.0.0.1 --port 9999 --message "Hello"
    python udp_echo.py client --host 10.0.1.10 --port 9999 --count 5

Autor: Material didactic ASE-CSIE
"""

from __future__ import annotations

import argparse
import socket
import sys
import time
from datetime import datetime
from typing import Optional

# Culori ANSI
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

    @classmethod
    def disable(cls):
        for attr in dir(cls):
            if not attr.startswith('_') and attr.isupper():
                setattr(cls, attr, '')


def timestamp() -> str:
    """Returneaza timestamp curent."""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def run_server(port: int, verbose: bool = False, buffer_size: int = 1024):
    """
    start serverul UDP Echo.
    
    Serverul listen pe portul specificat and send inapoi fiecare
    message primit (echo).
    """
    c = Colors
    
    # Creare socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind(('0.0.0.0', port))
    except OSError as e:
        print(f"{c.RED}Eroare bind pe port {port}: {e}{c.END}")
        sys.exit(1)
    
    print(f"{c.BOLD}{c.CYAN}╔══════════════════════════════════════════════════════════╗{c.END}")
    print(f"{c.BOLD}{c.CYAN}║{c.END}           {c.BOLD}UDP ECHO SERVER{c.END} — Port {port}                    {c.BOLD}{c.CYAN}║{c.END}")
    print(f"{c.BOLD}{c.CYAN}╚══════════════════════════════════════════════════════════╝{c.END}")
    print()
    print(f"{c.YELLOW}[{timestamp()}]{c.END} Server pornit, await connections...")
    print(f"{c.YELLOW}[{timestamp()}]{c.END} Apasati Ctrl+C for stop")
    print()
    
    message_count = 0
    
    try:
        while True:
            # Primire message
            data, client_addr = sock.recvfrom(buffer_size)
            message_count += 1
            
            client_ip, client_port = client_addr
            message = data.decode('utf-8', errors='replace')
            
            if verbose:
                print(f"{c.GREEN}[{timestamp()}]{c.END} #{message_count} Primit de la {client_ip}:{client_port}")
                print(f"           Dimensiune: {len(data)} bytes")
                print(f"           message: {message[:50]}{'...' if len(message) > 50 else ''}")
            else:
                print(f"{c.GREEN}[{timestamp()}]{c.END} #{message_count} {client_ip}:{client_port} → {len(data)}B")
            
            # Trimitem echo (acelasi message inapoi)
            response = f"ECHO: {message}".encode('utf-8')
            sock.sendto(response, client_addr)
            
            if verbose:
                print(f"{c.BLUE}[{timestamp()}]{c.END} Raspuns trimis ({len(response)} bytes)")
                print()
    
    except KeyboardInterrupt:
        print(f"\n{c.YELLOW}[{timestamp()}]{c.END} Server oprit. Total messages: {message_count}")
    
    finally:
        sock.close()


def run_client(
    host: str,
    port: int,
    message: str = "Hello from UDP client!",
    count: int = 1,
    interval: float = 1.0,
    timeout: float = 5.0,
    verbose: bool = False
):
    """
    run clientul UDP Echo.
    
    send messages to server and await raspunsul.
    """
    c = Colors
    
    # Creare socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    
    print(f"{c.BOLD}{c.CYAN}╔══════════════════════════════════════════════════════════╗{c.END}")
    print(f"{c.BOLD}{c.CYAN}║{c.END}           {c.BOLD}UDP ECHO CLIENT{c.END}                               {c.BOLD}{c.CYAN}║{c.END}")
    print(f"{c.BOLD}{c.CYAN}╚══════════════════════════════════════════════════════════╝{c.END}")
    print()
    print(f"  Destinatie: {host}:{port}")
    print(f"  messages de trimis: {count}")
    print()
    
    successful = 0
    failed = 0
    total_rtt = 0.0
    
    server_addr = (host, port)
    
    try:
        for i in range(count):
            seq = i + 1
            msg_with_seq = f"[{seq}/{count}] {message}"
            
            try:
                # Masuram RTT
                start_time = time.perf_counter()
                
                # Trimitem message
                sock.sendto(msg_with_seq.encode('utf-8'), server_addr)
                
                if verbose:
                    print(f"{c.BLUE}[{timestamp()}]{c.END} Trimis #{seq}: {msg_with_seq[:40]}...")
                
                # Asteptam raspuns
                data, _ = sock.recvfrom(1024)
                
                end_time = time.perf_counter()
                rtt = (end_time - start_time) * 1000  # in ms
                total_rtt += rtt
                
                response = data.decode('utf-8', errors='replace')
                
                print(f"{c.GREEN}[{timestamp()}]{c.END} #{seq} Raspuns: {len(data)}B, RTT: {rtt:.2f}ms")
                
                if verbose:
                    print(f"           Continut: {response[:60]}{'...' if len(response) > 60 else ''}")
                
                successful += 1
                
            except socket.timeout:
                print(f"{c.RED}[{timestamp()}]{c.END} #{seq} Timeout (>{timeout}s)")
                failed += 1
            
            except Exception as e:
                print(f"{c.RED}[{timestamp()}]{c.END} #{seq} Eroare: {e}")
                failed += 1
            
            # Pauza intre messages (daca nu e ultimul)
            if i < count - 1:
                time.sleep(interval)
    
    except KeyboardInterrupt:
        print(f"\n{c.YELLOW}Intrerupt de utilizator{c.END}")
    
    finally:
        sock.close()
    
    # Statistici
    print()
    print(f"{c.BOLD}═══ Statistici ═══{c.END}")
    print(f"  messages trimise:  {count}")
    print(f"  Raspunsuri:      {successful}")
    print(f"  Pierdute:        {failed}")
    if successful > 0:
        print(f"  RTT mediu:       {total_rtt / successful:.2f}ms")
    print()


def main():
    """Functia main."""
    parser = argparse.ArgumentParser(
        description="UDP Echo Server & Client for demonstrations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  # Terminal 1 - Server:
  %(prog)s server --port 9999

  # Terminal 2 - Client:
  %(prog)s client --host 127.0.0.1 --port 9999 --message "Test"
  %(prog)s client --host 10.0.1.10 --port 9999 --count 10
"""
    )
    
    subparsers = parser.add_subparsers(dest='mode', help='Mod de operare')
    
    # Server
    server_parser = subparsers.add_parser('server', help='start server UDP Echo')
    server_parser.add_argument(
        '--port', '-p',
        type=int,
        default=9999,
        help='Port de ascultare (default: 9999)'
    )
    server_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Output detaliat'
    )
    server_parser.add_argument(
        '--buffer',
        type=int,
        default=1024,
        help='Dimensiune buffer (default: 1024)'
    )
    
    # Client
    client_parser = subparsers.add_parser('client', help='start client UDP Echo')
    client_parser.add_argument(
        '--host', '-H',
        default='127.0.0.1',
        help='Adresa serverului (default: 127.0.0.1)'
    )
    client_parser.add_argument(
        '--port', '-p',
        type=int,
        default=9999,
        help='Portul serverului (default: 9999)'
    )
    client_parser.add_argument(
        '--message', '-m',
        default='Hello from UDP client!',
        help='Mesajul de trimis'
    )
    client_parser.add_argument(
        '--count', '-c',
        type=int,
        default=1,
        help='Numar de messages (default: 1)'
    )
    client_parser.add_argument(
        '--interval', '-i',
        type=float,
        default=1.0,
        help='Interval intre messages in secunde (default: 1.0)'
    )
    client_parser.add_argument(
        '--timeout', '-t',
        type=float,
        default=5.0,
        help='Timeout for raspuns in secunde (default: 5.0)'
    )
    client_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Output detaliat'
    )
    
    # Global
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Dezactivare culori'
    )
    
    args = parser.parse_args()
    
    if args.no_color or not sys.stdout.isatty():
        Colors.disable()
    
    if args.mode == 'server':
        run_server(args.port, args.verbose, args.buffer)
    elif args.mode == 'client':
        run_client(
            host=args.host,
            port=args.port,
            message=args.message,
            count=args.count,
            interval=args.interval,
            timeout=args.timeout,
            verbose=args.verbose
        )
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
