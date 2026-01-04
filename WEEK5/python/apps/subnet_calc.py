#!/usr/bin/env python3
"""
Subnet Calculator — Interactive calculator for subnets
===========================================================
CLI tool for analiza and planificarea subnets IPv4.

usage:
    python subnet_calc.py                     # Interactive mode
    python subnet_calc.py 192.168.1.0/24      # Direct analysis
    python subnet_calc.py --visual 10.0.0.0/8 # With visual view

Author: Teaching material (ASE-CSIE)
"""

from __future__ import annotations

import argparse
import ipaddress
import sys
from typing import Optional

# ANSI colours
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    @classmethod
    def disable(cls):
        """Disable colours for non-terminal output."""
        for attr in dir(cls):
            if not attr.startswith('_') and attr.isupper():
                setattr(cls, attr, '')


def analyze_network(cidr: str, visual: bool = False) -> dict:
    """
    analyse o network in notation CIDR and returneaza toti parametrii.
    """
    try:
        interface = ipaddress.ip_interface(cidr)
        network = interface.network
    except ValueError as e:
        raise ValueError(f"address invalid: {cidr}") from e
    
    # Calculam parametrii
    netmask = network.netmask
    wildcard = network.hostmask
    network_addr = network.network_address
    broadcast = network.broadcast_address
    prefix = network.prefixlen
    
    # Numar de hosts
    num_addresses = network.num_addresses
    num_hosts = max(0, num_addresses - 2)  # Excludem network and broadcast
    
    # Prima and ultima host
    hosts = list(network.hosts())
    first_host = hosts[0] if hosts else None
    last_host = hosts[-1] if hosts else None
    
    # Legacy class (for referinta hhistoric)
    first_octet = int(str(network_addr).split('.')[0])
    if first_octet < 128:
        ip_class = 'A'
    elif first_octet < 192:
        ip_class = 'B'
    elif first_octet < 224:
        ip_class = 'C'
    elif first_octet < 240:
        ip_class = 'D (Multicast)'
    else:
        ip_class = 'E (Rezervata)'
    
    # Tip address
    if network.is_private:
        addr_type = 'Privata (RFC 1918)'
    elif network.is_loopback:
        addr_type = 'Loopback'
    elif network.is_link_local:
        addr_type = 'Link-Local'
    elif network.is_multicast:
        addr_type = 'Multicast'
    elif network.is_reserved:
        addr_type = 'Rezervata'
    else:
        addr_type = 'Publica (Rutabila)'
    
    result = {
        'input': cidr,
        'ip': str(interface.ip),
        'network': str(network_addr),
        'netmask': str(netmask),
        'wildcard': str(wildcard),
        'broadcast': str(broadcast),
        'prefix': prefix,
        'first_host': str(first_host) if first_host else 'N/A',
        'last_host': str(last_host) if last_host else 'N/A',
        'num_addresses': num_addresses,
        'num_hosts': num_hosts,
        'ip_class': ip_class,
        'addr_type': addr_type,
    }
    
    # Reprezentare binara (optional)
    if visual:
        result['binary'] = {
            'ip': ip_to_binary(str(interface.ip)),
            'netmask': ip_to_binary(str(netmask)),
            'network': ip_to_binary(str(network_addr)),
            'broadcast': ip_to_binary(str(broadcast)),
        }
    
    return result


def ip_to_binary(ip: str) -> str:
    """Converteste IP in reprezentare binara with puncte."""
    octets = ip.split('.')
    return '.'.join(format(int(o), '08b') for o in octets)


def print_analysis(result: dict, visual: bool = False):
    """Prints rezultatul analizei in format frumos."""
    c = Colors
    
    print()
    print(f"{c.BOLD}{c.CYAN}╔══════════════════════════════════════════════════════════════════╗{c.END}")
    print(f"{c.BOLD}{c.CYAN}║{c.END}           {c.BOLD}SUBNET CALCULATOR — results Analiza{c.END}               {c.BOLD}{c.CYAN}║{c.END}")
    print(f"{c.BOLD}{c.CYAN}╠══════════════════════════════════════════════════════════════════╣{c.END}")
    
    fields = [
        ('Input', result['input']),
        ('address IP', result['ip']),
        ('Prefix', f"/{result['prefix']}"),
        ('mask network', result['netmask']),
        ('Wildcard', result['wildcard']),
        ('address network', result['network']),
        ('Broadcast', result['broadcast']),
        ('Prima host', result['first_host']),
        ('Ultima host', result['last_host']),
        ('addresses totale', f"{result['num_addresses']:,}"),
        ('hosts usable', f"{result['num_hosts']:,}"),
        ('Clasa IP', result['ip_class']),
        ('Tip address', result['addr_type']),
    ]
    
    for label, value in fields:
        print(f"{c.BOLD}{c.CYAN}║{c.END}  {c.YELLOW}{label:18}{c.END} {c.GREEN}{value}{c.END}")
    
    print(f"{c.BOLD}{c.CYAN}╚══════════════════════════════════════════════════════════════════╝{c.END}")
    
    # Reprezentare binara
    if visual and 'binary' in result:
        print()
        print(f"{c.BOLD}Reprezentare binara:{c.END}")
        print(f"  IP:        {result['binary']['ip']}")
        print(f"  mask:     {result['binary']['netmask']}")
        print(f"  network:     {result['binary']['network']}")
        print(f"  Broadcast: {result['binary']['broadcast']}")
        
        # Vizualizare grafica a bitilor
        prefix = result['prefix']
        print()
        print(f"{c.BOLD}Structura bitilor (prefix /{prefix}):{c.END}")
        print(f"  {'█' * prefix}{'░' * (32 - prefix)}")
        print(f"  {c.GREEN}← network ({prefix} biti){c.END}  {c.YELLOW}Host ({32 - prefix} biti) →{c.END}")
    
    print()


def interactive_mode():
    """Interactive mode with meniu."""
    c = Colors
    
    print()
    print(f"{c.BOLD}{c.CYAN}═══════════════════════════════════════════════════════════════════{c.END}")
    print(f"{c.BOLD}        SUBNET CALCULATOR — Mod Interactiv{c.END}")
    print(f"{c.BOLD}{c.CYAN}═══════════════════════════════════════════════════════════════════{c.END}")
    print()
    print("Comenzi available:")
    print("  • Enter o address CIDR (ex: 192.168.1.100/24)")
    print("  • 'prefix N' — Informatii despre prefixul /N")
    print("  • 'hosts N' — Ce prefix for N hosts")
    print("  • 'help' — Afisare ajutor")
    print("  • 'quit' sau 'exit' — Iesire")
    print()
    
    while True:
        try:
            user_input = input(f"{c.BOLD}subnet>{c.END} ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nLa revedere!")
            break
        
        if not user_input:
            continue
        
        cmd = user_input.lower()
        
        if cmd in ('quit', 'exit', 'q'):
            print("La revedere!")
            break
        
        elif cmd == 'help':
            print("\nExamples:")
            print("  192.168.1.0/24    — Analiza network")
            print("  10.0.0.1/8        — Analiza with IP specific")
            print("  prefix 24         — Info despre /24")
            print("  hosts 500         — Prefix for 500 hosts")
            print()
        
        elif cmd.startswith('prefix '):
            try:
                n = int(cmd.split()[1])
                if 0 <= n <= 32:
                    hosts = max(0, 2 ** (32 - n) - 2)
                    print(f"\n  Prefix /{n}:")
                    print(f"    mask: {ipaddress.IPv4Address(2**32 - 2**(32-n))}")
                    print(f"    addresses totale: {2 ** (32 - n):,}")
                    print(f"    hosts usable: {hosts:,}")
                    print()
                else:
                    print("  Prefix invalid (0-32)")
            except (ValueError, IndexError):
                print("  usage: prefix N (ex: prefix 24)")
        
        elif cmd.startswith('hosts '):
            try:
                n = int(cmd.split()[1])
                if n < 1:
                    print("  Numarul de hosts trebuie sa fie >= 1")
                else:
                    # Gasim cel mai mic prefix
                    for prefix in range(32, 0, -1):
                        available = 2 ** (32 - prefix) - 2
                        if available >= n:
                            print(f"\n  Pentru {n} hosts:")
                            print(f"    Prefix recomandat: /{prefix}")
                            print(f"    hosts available: {available:,}")
                            print(f"    Eficienta: {n / available * 100:.1f}%")
                            break
                    else:
                        print("  Prea multe hosts (max ~4 miliarde)")
                    print()
            except (ValueError, IndexError):
                print("  usage: hosts N (ex: hosts 500)")
        
        else:
            # Presupunem ca e o address CIDR
            try:
                result = analyze_network(user_input, visual=True)
                print_analysis(result, visual=True)
            except ValueError as e:
                print(f"  {c.RED}Eroare: {e}{c.END}")
                print("  Tip: Enter in format CIDR (ex: 192.168.1.0/24)")


def main():
    """Functia main."""
    parser = argparse.ArgumentParser(
        description="Subnet Calculator — Interactive calculator for subnets IPv4",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Interactive mode
  %(prog)s 192.168.1.0/24           # Direct analysis
  %(prog)s 10.0.0.0/8 --visual      # Cu reprezentare binara
  %(prog)s 172.16.50.12/21 --json   # Output JSON
"""
    )
    
    parser.add_argument(
        'cidr',
        nargs='?',
        help="Adresa in format CIDR (ex: 192.168.1.0/24)"
    )
    
    parser.add_argument(
        '--visual', '-v',
        action='store_true',
        help="Afisare reprezentare binara and vizualizare"
    )
    
    parser.add_argument(
        '--json', '-j',
        action='store_true',
        help="Output in format JSON"
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help="Dezactivare culori"
    )
    
    args = parser.parse_args()
    
    # Dezactivam culorile daca nu e terminal or daca e cerut explicit
    if args.no_color or not sys.stdout.isatty():
        Colors.disable()
    
    if args.cidr:
        # Mod direct
        try:
            result = analyze_network(args.cidr, visual=args.visual)
            
            if args.json:
                import json
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print_analysis(result, visual=args.visual)
                
        except ValueError as e:
            print(f"Eroare: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
