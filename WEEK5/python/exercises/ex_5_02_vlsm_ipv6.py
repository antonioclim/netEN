#!/usr/bin/env python3
"""
Exercise 5.02 – VLSM and IPv6 Utilities
=======================================
CLI for VLSM allocation and IPv6 address operations.

Usage:
    python ex_5_02_vlsm_ipv6.py vlsm 172.16.0.0/24 60 20 10 2
    python ex_5_02_vlsm_ipv6.py ipv6 2001:0db8:0000:0000:0000:0000:0000:0001
    python ex_5_02_vlsm_ipv6.py ipv6-expand 2001:db8::1
    python ex_5_02_vlsm_ipv6.py ipv6-subnets 2001:db8:10::/48 64 5

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
    vlsm_allocate,
    ipv6_compress,
    ipv6_expand,
    ipv6_info,
    ipv6_subnets_from_prefix,
    prefix_for_hosts,
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
    END = '\033[0m'


def colorize(text: str, color: str) -> str:
    """Apply colour if stdout is a terminal."""
    if sys.stdout.isatty():
        return f"{color}{text}{Colors.END}"
    return text


def cmd_vlsm(base: str, requirements: List[int], as_json: bool = False) -> int:
    """Allocate subnets with VLSM."""
    try:
        allocations = vlsm_allocate(base, requirements)
    except ValueError as e:
        print(colorize(f"Error: {e}", Colors.RED), file=sys.stderr)
        return 1
    
    if as_json:
        result = []
        for alloc in allocations:
            result.append({
                "required_hosts": alloc.required_hosts,
                "prefix": alloc.allocated_prefix,
                "network": str(alloc.network),
                "gateway": str(alloc.gateway),
                "broadcast": str(alloc.broadcast),
                "usable_hosts": alloc.usable_hosts,
                "efficiency_percent": round(alloc.efficiency, 2),
            })
        output = {
            "base_network": base,
            "requirements": requirements,
            "allocations": result,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return 0
    
    # Formatted output
    import ipaddress
    base_net = ipaddress.ip_network(base, strict=True)
    
    print()
    print(colorize("═" * 70, Colors.BLUE))
    print(colorize("  VLSM Allocation (Variable Length Subnet Mask)", Colors.BOLD))
    print(colorize("═" * 70, Colors.BLUE))
    print()
    
    print(f"  {colorize('Available Network:', Colors.CYAN):30} {base}")
    print(f"  {colorize('Total Addresses:', Colors.CYAN):30} {base_net.num_addresses}")
    print(f"  {colorize('Host Requirements:', Colors.CYAN):30} {', '.join(map(str, requirements))}")
    print()
    
    # Algorithm explanation
    print(colorize("─" * 70, Colors.BLUE))
    print(colorize("  VLSM Algorithm:", Colors.BOLD))
    print(colorize("─" * 70, Colors.BLUE))
    print("  1. Sort requirements in descending order")
    print("  2. For each requirement, calculate minimum prefix needed")
    print("  3. Align start address to block boundary")
    print("  4. Allocate and advance cursor")
    print()
    
    # Allocation table
    print(colorize("─" * 70, Colors.BLUE))
    print(f"  {'#':>3}  {'Required':>8}  {'Prefix':>7}  {'Subnet':<20} {'Gateway':<16} {'Efficiency'}")
    print(colorize("─" * 70, Colors.BLUE))
    
    total_required = 0
    total_allocated = 0
    
    for i, alloc in enumerate(allocations, 1):
        efficiency_color = Colors.GREEN if alloc.efficiency > 75 else Colors.YELLOW if alloc.efficiency > 50 else Colors.RED
        eff_str = colorize(f"{alloc.efficiency:5.1f}%", efficiency_color)
        
        print(f"  {i:>3}  {alloc.required_hosts:>8}  /{alloc.allocated_prefix:<6}  "
              f"{str(alloc.network):<20} {str(alloc.gateway):<16} {eff_str}")
        
        total_required += alloc.required_hosts
        total_allocated += alloc.usable_hosts
    
    print(colorize("─" * 70, Colors.BLUE))
    
    # Efficiency summary
    print()
    total_used = sum(alloc.network.num_addresses for alloc in allocations)
    remaining = base_net.num_addresses - total_used
    overall_efficiency = (total_required / total_allocated * 100) if total_allocated > 0 else 0
    
    print(f"  {colorize('Summary:', Colors.BOLD)}")
    print(f"    Total hosts required:     {total_required}")
    print(f"    Total hosts allocated:    {total_allocated}")
    print(f"    Overall efficiency:       {colorize(f'{overall_efficiency:.1f}%', Colors.GREEN)}")
    print(f"    Remaining free addresses: {remaining}")
    
    if remaining > 0:
        import ipaddress
        # Find the last allocated address
        last_alloc = max(allocations, key=lambda a: int(a.network.broadcast_address))
        next_addr = int(last_alloc.network.broadcast_address) + 1
        if next_addr <= int(base_net.broadcast_address):
            print(f"    First free address:       {ipaddress.IPv4Address(next_addr)}")
    
    print()
    return 0


def cmd_ipv6_compress(address: str) -> int:
    """Compress an IPv6 address."""
    try:
        info = ipv6_info(address)
    except ValueError as e:
        print(colorize(f"Error: {e}", Colors.RED), file=sys.stderr)
        return 1
    
    print()
    print(colorize("═" * 60, Colors.BLUE))
    print(colorize("  IPv6 Address Analysis", Colors.BOLD))
    print(colorize("═" * 60, Colors.BLUE))
    print()
    
    print(f"  {colorize('Input:', Colors.CYAN):30} {address}")
    print(f"  {colorize('Full Form:', Colors.CYAN):30} {info.full_form}")
    print(f"  {colorize('Compressed Form:', Colors.CYAN):30} {colorize(info.compressed, Colors.GREEN)}")
    print()
    
    print(f"  {colorize('Address Type:', Colors.CYAN):30} {info.address_type}")
    print(f"  {colorize('Scope:', Colors.CYAN):30} {info.scope}")
    
    if info.network:
        print(f"  {colorize('Network:', Colors.CYAN):30} {info.network}")
    
    print()
    
    # Compression explanation
    print(colorize("─" * 60, Colors.BLUE))
    print(colorize("  IPv6 Compression Rules:", Colors.BOLD))
    print(colorize("─" * 60, Colors.BLUE))
    print("  1. Remove leading zeros from each group")
    print("  2. Use :: for the longest sequence of zeros")
    print("  3. :: can only be used once")
    print()
    
    return 0


def cmd_ipv6_expand(address: str) -> int:
    """Expand an IPv6 address."""
    try:
        expanded = ipv6_expand(address)
    except ValueError as e:
        print(colorize(f"Error: {e}", Colors.RED), file=sys.stderr)
        return 1
    
    print()
    print(colorize("═" * 60, Colors.BLUE))
    print(colorize("  IPv6 Address Expansion", Colors.BOLD))
    print(colorize("═" * 60, Colors.BLUE))
    print()
    
    print(f"  {colorize('Input (compressed):', Colors.CYAN):30} {address}")
    print(f"  {colorize('Output (expanded):', Colors.CYAN):30} {colorize(expanded, Colors.GREEN)}")
    print()
    
    # Decompose into groups
    groups = expanded.split(':')
    print(colorize("  Hexadecimal Groups:", Colors.CYAN))
    for i, group in enumerate(groups):
        decimal_val = int(group, 16)
        print(f"    Group {i+1}: {group} = {decimal_val} (decimal)")
    print()
    
    return 0


def cmd_ipv6_subnets(base: str, target_prefix: int, count: int) -> int:
    """Generate IPv6 subnets."""
    try:
        subnets = ipv6_subnets_from_prefix(base, target_prefix, count)
    except ValueError as e:
        print(colorize(f"Error: {e}", Colors.RED), file=sys.stderr)
        return 1
    
    import ipaddress
    base_net = ipaddress.ip_network(base, strict=True)
    total_possible = 2 ** (target_prefix - base_net.prefixlen)
    
    print()
    print(colorize("═" * 70, Colors.BLUE))
    print(colorize("  IPv6 Subnetting", Colors.BOLD))
    print(colorize("═" * 70, Colors.BLUE))
    print()
    
    print(f"  {colorize('Base Prefix:', Colors.CYAN):30} {base}")
    print(f"  {colorize('Target Prefix:', Colors.CYAN):30} /{target_prefix}")
    print(f"  {colorize('Requested Subnets:', Colors.CYAN):30} {count}")
    print(f"  {colorize('Total Possible Subnets:', Colors.CYAN):30} {total_possible:,}")
    print()
    
    print(colorize("─" * 70, Colors.BLUE))
    print(f"  {'#':>3}  {'Subnet Prefix':<45} {'Suggested Gateway'}")
    print(colorize("─" * 70, Colors.BLUE))
    
    for i, subnet in enumerate(subnets, 1):
        # Gateway = first address (::1)
        gateway = subnet.network_address + 1
        print(f"  {i:>3}  {str(subnet):<45} {gateway}")
    
    print(colorize("─" * 70, Colors.BLUE))
    print()
    
    # Notes about IPv6 subnetting
    if target_prefix == 64:
        print(colorize("  Note:", Colors.YELLOW))
        print("  • /64 is the standard length for LANs (SLAAC)")
        print("  • Interface ID occupies the last 64 bits")
        print("  • Each /64 subnet can have 2^64 addresses")
    
    print()
    return 0


def cmd_ipv6_types() -> int:
    """Display IPv6 address types."""
    print()
    print(colorize("═" * 65, Colors.BLUE))
    print(colorize("  IPv6 Address Types", Colors.BOLD))
    print(colorize("═" * 65, Colors.BLUE))
    print()
    
    types = [
        ("::", "Unspecified address", "Used when we have no address"),
        ("::1", "Loopback", "Equivalent to 127.0.0.1"),
        ("fe80::/10", "Link-local", "Local communication, auto-configured"),
        ("fc00::/7", "Unique local", "Equivalent to RFC 1918 (private addresses)"),
        ("2000::/3", "Global unicast", "Internet routable addresses"),
        ("ff00::/8", "Multicast", "Communication to groups"),
    ]
    
    print(f"  {'Prefix':<15} {'Type':<20} {'Description'}")
    print(colorize("─" * 65, Colors.BLUE))
    
    for prefix, typ, desc in types:
        print(f"  {colorize(prefix, Colors.GREEN):<24} {typ:<20} {desc}")
    
    print()
    print(colorize("  Practical Examples:", Colors.YELLOW))
    print("  • fe80::1             Link-local on interface")
    print("  • 2001:db8::1         Global unicast (documentation)")
    print("  • ff02::1             All-nodes multicast")
    print("  • ff02::2             All-routers multicast")
    print()
    
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        description="Exercise 5.02 – VLSM and IPv6 Utilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s vlsm 172.16.0.0/24 60 20 10 2       VLSM allocation
  %(prog)s vlsm 10.0.0.0/22 200 100 50 2 2    For large organisation
  
  %(prog)s ipv6 2001:0db8:0000:0000:0000:0000:0000:0001   IPv6 compression
  %(prog)s ipv6-expand 2001:db8::1                        IPv6 expansion
  %(prog)s ipv6-subnets 2001:db8:10::/48 64 10            Generate subnets
  %(prog)s ipv6-types                                      Type reference
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # VLSM subcommand
    p_vlsm = subparsers.add_parser(
        "vlsm",
        help="Allocate subnets with VLSM for a list of requirements"
    )
    p_vlsm.add_argument(
        "base",
        help="Available network in CIDR format (e.g.: 172.16.0.0/24)"
    )
    p_vlsm.add_argument(
        "requirements",
        type=int,
        nargs="+",
        help="List of host requirements (e.g.: 60 20 10 2)"
    )
    p_vlsm.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output in JSON format"
    )
    
    # IPv6 subcommand (compression)
    p_ipv6 = subparsers.add_parser(
        "ipv6",
        help="Analyse and compress an IPv6 address"
    )
    p_ipv6.add_argument(
        "address",
        help="IPv6 address in any format"
    )
    
    # ipv6-expand subcommand
    p_expand = subparsers.add_parser(
        "ipv6-expand",
        help="Expand an IPv6 address to full form"
    )
    p_expand.add_argument(
        "address",
        help="Compressed IPv6 address (e.g.: 2001:db8::1)"
    )
    
    # ipv6-subnets subcommand
    p_subnets = subparsers.add_parser(
        "ipv6-subnets",
        help="Generate IPv6 subnets from a prefix"
    )
    p_subnets.add_argument(
        "base",
        help="Base prefix (e.g.: 2001:db8:10::/48)"
    )
    p_subnets.add_argument(
        "target_prefix",
        type=int,
        help="Target prefix length (e.g.: 64)"
    )
    p_subnets.add_argument(
        "count",
        type=int,
        help="Number of subnets to generate"
    )
    
    # ipv6-types subcommand
    subparsers.add_parser(
        "ipv6-types",
        help="Display IPv6 address types"
    )
    
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main function."""
    parser = build_parser()
    args = parser.parse_args(argv)
    
    if args.command == "vlsm":
        return cmd_vlsm(args.base, args.requirements, args.json)
    elif args.command == "ipv6":
        return cmd_ipv6_compress(args.address)
    elif args.command == "ipv6-expand":
        return cmd_ipv6_expand(args.address)
    elif args.command == "ipv6-subnets":
        return cmd_ipv6_subnets(args.base, args.target_prefix, args.count)
    elif args.command == "ipv6-types":
        return cmd_ipv6_types()
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
