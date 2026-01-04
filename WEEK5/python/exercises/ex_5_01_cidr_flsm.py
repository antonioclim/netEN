#!/usr/bin/env python3
"""
Exercise 5.01 – CIDR Analysis and FLSM Subnetting
=================================================
CLI for calculating network parameters and splitting into equal subnets.

Usage:
    python ex_5_01_cidr_flsm.py analyze 192.168.10.14/26 [--verbose] [--json]
    python ex_5_01_cidr_flsm.py flsm 192.168.100.0/24 4
    python ex_5_01_cidr_flsm.py binary 192.168.10.14

Author: ASE-CSIE Teaching Material
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

# Local utility import
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from python.utils.net_utils import (
    analyze_ipv4_interface,
    flsm_split,
    ipv4_host_range,
    ip_to_binary,
    ip_to_dotted_binary,
    prefix_to_netmask,
    netmask_to_prefix,
)


# ANSI colour codes
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


def colorize(text: str, color: str) -> str:
    """Apply colour if stdout is a terminal."""
    if sys.stdout.isatty():
        return f"{color}{text}{Colors.END}"
    return text


def cmd_analyze(target: str, verbose: bool = False, as_json: bool = False) -> int:
    """Analyse an IPv4 address with CIDR prefix."""
    try:
        info = analyze_ipv4_interface(target)
    except ValueError as e:
        print(colorize(f"Error: {e}", Colors.RED), file=sys.stderr)
        return 1
    
    payload = {
        "input": target,
        "address": str(info.address),
        "address_type": info.address_type,
        "network": str(info.network.network_address),
        "prefix": info.network.prefixlen,
        "netmask": str(info.netmask),
        "wildcard": str(info.wildcard),
        "broadcast": str(info.broadcast),
        "total_addresses": info.total_addresses,
        "usable_hosts": info.usable_hosts,
        "first_host": str(info.first_host) if info.first_host else None,
        "last_host": str(info.last_host) if info.last_host else None,
        "is_private": info.is_private,
    }
    
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0
    
    # Formatted output
    print()
    print(colorize("═" * 50, Colors.BLUE))
    print(colorize("  IPv4 CIDR Analysis", Colors.BOLD))
    print(colorize("═" * 50, Colors.BLUE))
    print()
    
    print(f"  {colorize('Input:', Colors.CYAN):30} {target}")
    print(f"  {colorize('IP Address:', Colors.CYAN):30} {info.address}")
    print(f"  {colorize('Address Type:', Colors.CYAN):30} {colorize(info.address_type.upper(), Colors.YELLOW)}")
    print()
    
    print(f"  {colorize('Network Address:', Colors.CYAN):30} {info.network.network_address}/{info.network.prefixlen}")
    print(f"  {colorize('Subnet Mask:', Colors.CYAN):30} {info.netmask}")
    print(f"  {colorize('Wildcard Mask:', Colors.CYAN):30} {info.wildcard}")
    print(f"  {colorize('Broadcast Address:', Colors.CYAN):30} {info.broadcast}")
    print()
    
    print(f"  {colorize('Total Addresses:', Colors.CYAN):30} {info.total_addresses}")
    print(f"  {colorize('Usable Hosts:', Colors.CYAN):30} {colorize(str(info.usable_hosts), Colors.GREEN)}")
    print(f"  {colorize('First Host:', Colors.CYAN):30} {info.first_host or 'N/A'}")
    print(f"  {colorize('Last Host:', Colors.CYAN):30} {info.last_host or 'N/A'}")
    print()
    
    print(f"  {colorize('Private Address:', Colors.CYAN):30} {'Yes' if info.is_private else 'No'}")
    
    if verbose:
        print()
        print(colorize("─" * 50, Colors.BLUE))
        print(colorize("  Binary Representation", Colors.BOLD))
        print(colorize("─" * 50, Colors.BLUE))
        print()
        
        addr_bin = ip_to_dotted_binary(str(info.address))
        mask_bin = ip_to_dotted_binary(str(info.netmask))
        net_bin = ip_to_dotted_binary(str(info.network.network_address))
        bcast_bin = ip_to_dotted_binary(str(info.broadcast))
        
        prefix = info.network.prefixlen
        
        print(f"  {colorize('IP (binary):', Colors.CYAN):30}")
        print(f"    {colorize(addr_bin[:prefix], Colors.GREEN)}{addr_bin[prefix:]}")
        print(f"    {'─' * prefix}{'^' * (35 - prefix)} host portion")
        print()
        
        print(f"  {colorize('Mask (binary):', Colors.CYAN):30}")
        print(f"    {mask_bin}")
        print()
        
        print(f"  {colorize('Network (binary):', Colors.CYAN):30}")
        print(f"    {net_bin}")
        print()
        
        print(f"  {colorize('Broadcast (binary):', Colors.CYAN):30}")
        print(f"    {bcast_bin}")
        print()
        
        # Calculation explanation
        print(colorize("─" * 50, Colors.BLUE))
        print(colorize("  Calculation Explanation", Colors.BOLD))
        print(colorize("─" * 50, Colors.BLUE))
        print()
        
        host_bits = 32 - prefix
        print(f"  • Prefix /{prefix} = {prefix} bits for network, {host_bits} bits for host")
        print(f"  • Total addresses = 2^{host_bits} = {2**host_bits}")
        print(f"  • Usable hosts = 2^{host_bits} - 2 = {2**host_bits - 2}")
        print(f"  • Network address: all host bits = 0")
        print(f"  • Broadcast address: all host bits = 1")
    
    print()
    return 0


def cmd_flsm(base: str, n_subnets: int, as_json: bool = False) -> int:
    """Split a network into N equal subnets."""
    try:
        subnets = flsm_split(base, n_subnets)
    except ValueError as e:
        print(colorize(f"Error: {e}", Colors.RED), file=sys.stderr)
        return 1
    
    if as_json:
        result = []
        for subnet in subnets:
            first, last, usable = ipv4_host_range(subnet)
            result.append({
                "network": str(subnet.network_address),
                "prefix": subnet.prefixlen,
                "cidr": str(subnet),
                "broadcast": str(subnet.broadcast_address),
                "usable_hosts": usable,
                "first_host": str(first) if first else None,
                "last_host": str(last) if last else None,
            })
        print(json.dumps({"base": base, "num_subnets": n_subnets, "subnets": result}, indent=2))
        return 0
    
    # Formatted output
    import ipaddress
    base_net = ipaddress.ip_network(base, strict=True)
    bits_added = n_subnets.bit_length() - 1
    new_prefix = base_net.prefixlen + bits_added
    
    print()
    print(colorize("═" * 60, Colors.BLUE))
    print(colorize("  FLSM Subnetting (Fixed Length Subnet Mask)", Colors.BOLD))
    print(colorize("═" * 60, Colors.BLUE))
    print()
    
    print(f"  {colorize('Base Network:', Colors.CYAN):30} {base}")
    print(f"  {colorize('Number of Subnets:', Colors.CYAN):30} {n_subnets}")
    print(f"  {colorize('Borrowed Bits:', Colors.CYAN):30} {bits_added}")
    print(f"  {colorize('New Prefix:', Colors.CYAN):30} /{new_prefix}")
    print(f"  {colorize('Increment:', Colors.CYAN):30} {2**(32-new_prefix)} addresses")
    print()
    
    print(colorize("─" * 60, Colors.BLUE))
    print(f"  {'No.':>4}  {'Subnet':<20} {'Broadcast':<18} {'Hosts':<10} {'Range'}")
    print(colorize("─" * 60, Colors.BLUE))
    
    for i, subnet in enumerate(subnets, 1):
        first, last, usable = ipv4_host_range(subnet)
        interval = f"{first}..{last}" if first and last else "N/A"
        print(f"  {i:>4}. {str(subnet):<20} {str(subnet.broadcast_address):<18} {usable:<10} {interval}")
    
    print(colorize("─" * 60, Colors.BLUE))
    print()
    
    # Total verification
    total_usable = sum(ipv4_host_range(s)[2] for s in subnets)
    print(f"  {colorize('Total Usable Hosts:', Colors.GREEN)} {total_usable}")
    print()
    
    return 0


def cmd_binary(ip: str) -> int:
    """Display the binary representation of an IP address."""
    try:
        import ipaddress
        addr = ipaddress.IPv4Address(ip)
    except ValueError as e:
        print(colorize(f"Error: {e}", Colors.RED), file=sys.stderr)
        return 1
    
    binary = ip_to_binary(ip)
    dotted = ip_to_dotted_binary(ip)
    
    print()
    print(colorize("═" * 50, Colors.BLUE))
    print(colorize("  IP → Binary Conversion", Colors.BOLD))
    print(colorize("═" * 50, Colors.BLUE))
    print()
    
    print(f"  {colorize('Decimal IP:', Colors.CYAN):25} {ip}")
    print(f"  {colorize('Full Binary:', Colors.CYAN):25} {binary}")
    print(f"  {colorize('Dotted Binary:', Colors.CYAN):25} {dotted}")
    print()
    
    # Display by octets
    octets = ip.split('.')
    print(colorize("  Conversion by Octets:", Colors.CYAN))
    for i, octet in enumerate(octets):
        oct_bin = bin(int(octet))[2:].zfill(8)
        print(f"    Octet {i+1}: {octet:>3} → {oct_bin}")
    print()
    
    return 0


def cmd_quiz() -> int:
    """Generate a quick quiz question."""
    import random
    
    # Generate a random address
    octets = [random.randint(1, 254) for _ in range(4)]
    prefix = random.choice([24, 25, 26, 27, 28, 29, 30])
    
    ip = '.'.join(map(str, octets))
    cidr = f"{ip}/{prefix}"
    
    print()
    print(colorize("═" * 50, Colors.YELLOW))
    print(colorize("  Quick Quiz: CIDR Analysis", Colors.BOLD))
    print(colorize("═" * 50, Colors.YELLOW))
    print()
    print(f"  Address: {colorize(cidr, Colors.GREEN)}")
    print()
    print("  Calculate:")
    print("  1. Network address")
    print("  2. Broadcast address")
    print("  3. Number of usable hosts")
    print("  4. First and last usable host")
    print()
    
    input(colorize("  Press Enter to see the answer...", Colors.CYAN))
    
    return cmd_analyze(cidr, verbose=False, as_json=False)


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        description="Exercise 5.01 – CIDR Analysis and FLSM Subnetting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze 192.168.10.14/26           Analyse the address
  %(prog)s analyze 192.168.10.14/26 --verbose With detailed explanations
  %(prog)s analyze 192.168.10.14/26 --json    JSON output
  %(prog)s flsm 192.168.100.0/24 4            Split into 4 subnets
  %(prog)s flsm 10.0.0.0/24 8                 Split into 8 subnets
  %(prog)s binary 192.168.1.1                 Binary conversion
  %(prog)s quiz                               Random quick quiz
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Analyze subcommand
    p_analyze = subparsers.add_parser(
        "analyze",
        help="Analyse an IPv4 address with CIDR prefix"
    )
    p_analyze.add_argument(
        "target",
        help="IPv4 address with prefix (e.g.: 192.168.10.14/26)"
    )
    p_analyze.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Display detailed explanations and binary representation"
    )
    p_analyze.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output in JSON format"
    )
    
    # FLSM subcommand
    p_flsm = subparsers.add_parser(
        "flsm",
        help="Split a network into N equal subnets (FLSM)"
    )
    p_flsm.add_argument(
        "base",
        help="Base network in CIDR format (e.g.: 192.168.100.0/24)"
    )
    p_flsm.add_argument(
        "n",
        type=int,
        help="Number of subnets (power of 2)"
    )
    p_flsm.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output in JSON format"
    )
    
    # Binary subcommand
    p_binary = subparsers.add_parser(
        "binary",
        help="Display the binary representation of an IP address"
    )
    p_binary.add_argument(
        "ip",
        help="IPv4 address (e.g.: 192.168.1.1)"
    )
    
    # Quiz subcommand
    subparsers.add_parser(
        "quiz",
        help="Generate a quick quiz question"
    )
    
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main function."""
    parser = build_parser()
    args = parser.parse_args(argv)
    
    if args.command == "analyze":
        return cmd_analyze(args.target, args.verbose, args.json)
    elif args.command == "flsm":
        return cmd_flsm(args.base, args.n, args.json)
    elif args.command == "binary":
        return cmd_binary(args.ip)
    elif args.command == "quiz":
        return cmd_quiz()
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
