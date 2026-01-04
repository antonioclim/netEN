#!/usr/bin/env python3
"""
Network Utilities for Week 5 – Network Layer: IP Addressing
============================================================
Reusable functions for CIDR calculations, VLSM, IPv6 and validations.

Author: ASE-CSIE Teaching Material
Version: 2.0 (December 2025)
"""

from __future__ import annotations

import ipaddress
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union


@dataclass
class IPv4NetworkInfo:
    """Complete information about an IPv4 network/interface."""
    address: ipaddress.IPv4Address
    network: ipaddress.IPv4Network
    netmask: ipaddress.IPv4Address
    wildcard: ipaddress.IPv4Address
    broadcast: ipaddress.IPv4Address
    total_addresses: int
    usable_hosts: int
    first_host: Optional[ipaddress.IPv4Address]
    last_host: Optional[ipaddress.IPv4Address]
    is_private: bool
    address_type: str  # 'network', 'broadcast', 'host'


@dataclass
class VLSMAllocation:
    """Result of a VLSM allocation."""
    required_hosts: int
    allocated_prefix: int
    network: ipaddress.IPv4Network
    gateway: ipaddress.IPv4Address
    broadcast: ipaddress.IPv4Address
    usable_hosts: int
    efficiency: float  # usage percentage


@dataclass
class IPv6Info:
    """Information about an IPv6 address."""
    full_form: str
    compressed: str
    exploded: str
    network: Optional[ipaddress.IPv6Network]
    address_type: str
    scope: str


def analyze_ipv4_interface(cidr: str) -> IPv4NetworkInfo:
    """
    Completely analyse an IPv4 address with CIDR prefix.
    
    Args:
        cidr: Address in format 'x.x.x.x/n' (e.g.: '192.168.10.14/26')
    
    Returns:
        IPv4NetworkInfo with all network details
    
    Raises:
        ValueError: for invalid addresses
    """
    interface = ipaddress.IPv4Interface(cidr)
    network = interface.network
    address = interface.ip
    
    # Calculate wildcard mask (inverse of mask)
    netmask_int = int(network.netmask)
    wildcard_int = netmask_int ^ 0xFFFFFFFF
    wildcard = ipaddress.IPv4Address(wildcard_int)
    
    # Determine address type
    if address == network.network_address:
        addr_type = "network"
    elif address == network.broadcast_address:
        addr_type = "broadcast"
    else:
        addr_type = "host"
    
    # Calculate usable hosts
    total = network.num_addresses
    if network.prefixlen == 32:
        usable = 1
        first_host = last_host = address
    elif network.prefixlen == 31:
        # RFC 3021: point-to-point links
        usable = 2
        first_host = network.network_address
        last_host = network.broadcast_address
    else:
        usable = total - 2
        first_host = network.network_address + 1
        last_host = network.broadcast_address - 1
    
    return IPv4NetworkInfo(
        address=address,
        network=network,
        netmask=network.netmask,
        wildcard=wildcard,
        broadcast=network.broadcast_address,
        total_addresses=total,
        usable_hosts=usable,
        first_host=first_host if usable > 0 else None,
        last_host=last_host if usable > 0 else None,
        is_private=network.is_private,
        address_type=addr_type
    )


def ipv4_host_range(network: ipaddress.IPv4Network) -> Tuple[Optional[ipaddress.IPv4Address], 
                                                              Optional[ipaddress.IPv4Address], 
                                                              int]:
    """
    Return (first_host, last_host, usable_count) for an IPv4 network.
    """
    total = network.num_addresses
    if network.prefixlen == 32:
        return network.network_address, network.network_address, 1
    elif network.prefixlen == 31:
        return network.network_address, network.broadcast_address, 2
    elif total <= 2:
        return None, None, 0
    else:
        return network.network_address + 1, network.broadcast_address - 1, total - 2


def prefix_for_hosts(hosts_needed: int) -> int:
    """
    Calculate the minimum prefix required for a number of hosts.
    
    Args:
        hosts_needed: number of hosts required
    
    Returns:
        Prefix length (e.g.: 26 for max 62 hosts)
    """
    if hosts_needed <= 0:
        raise ValueError("Number of hosts must be positive")
    
    # Add 2 for network address and broadcast
    total_needed = hosts_needed + 2
    
    # Find power of 2 >= total_needed
    host_bits = math.ceil(math.log2(total_needed))
    
    # Ensure minimum 2 host bits (for /30)
    host_bits = max(host_bits, 2)
    
    prefix = 32 - host_bits
    
    if prefix < 0:
        raise ValueError(f"No sufficient prefix for {hosts_needed} hosts")
    
    return prefix


def flsm_split(base_network: str, num_subnets: int) -> List[ipaddress.IPv4Network]:
    """
    Split a network into N equal subnets (FLSM).
    
    Args:
        base_network: base network in strict CIDR format (e.g.: '192.168.100.0/24')
        num_subnets: number of subnets (must be power of 2)
    
    Returns:
        List of resulting subnets
    
    Raises:
        ValueError: if num_subnets is not power of 2 or resulting prefix is invalid
    """
    net = ipaddress.ip_network(base_network, strict=True)
    
    if not isinstance(net, ipaddress.IPv4Network):
        raise ValueError("FLSM implemented only for IPv4")
    
    if num_subnets <= 0 or (num_subnets & (num_subnets - 1)) != 0:
        raise ValueError("Number of subnets must be power of 2 (2, 4, 8, 16...)")
    
    bits_needed = num_subnets.bit_length() - 1
    new_prefix = net.prefixlen + bits_needed
    
    if new_prefix > 30:
        raise ValueError(f"Resulting prefix /{new_prefix} leaves no usable hosts")
    
    return list(net.subnets(prefixlen_diff=bits_needed))


def vlsm_allocate(base_network: str, host_requirements: List[int]) -> List[VLSMAllocation]:
    """
    Allocate subnets with VLSM for a list of host requirements.
    
    Args:
        base_network: available network in CIDR format (e.g.: '10.0.0.0/24')
        host_requirements: list of requirements (e.g.: [60, 30, 10, 2])
    
    Returns:
        List of VLSM allocations in descending order of requirements
    
    Raises:
        ValueError: if address space is insufficient
    """
    net = ipaddress.ip_network(base_network, strict=True)
    
    if not isinstance(net, ipaddress.IPv4Network):
        raise ValueError("VLSM implemented only for IPv4")
    
    # Sort requirements in descending order
    sorted_reqs = sorted(enumerate(host_requirements), key=lambda x: -x[1])
    
    allocations: List[VLSMAllocation] = []
    current_addr = int(net.network_address)
    end_addr = int(net.broadcast_address)
    
    for orig_idx, hosts in sorted_reqs:
        prefix = prefix_for_hosts(hosts)
        block_size = 2 ** (32 - prefix)
        
        # Align to block boundary
        if current_addr % block_size != 0:
            current_addr = ((current_addr // block_size) + 1) * block_size
        
        if current_addr + block_size - 1 > end_addr:
            raise ValueError(
                f"Insufficient space for {hosts} hosts. "
                f"Current address: {ipaddress.IPv4Address(current_addr)}, "
                f"Required: /{prefix} ({block_size} addresses)"
            )
        
        subnet = ipaddress.IPv4Network(f"{ipaddress.IPv4Address(current_addr)}/{prefix}")
        first_host, last_host, usable = ipv4_host_range(subnet)
        
        efficiency = (hosts / usable * 100) if usable > 0 else 0
        
        allocations.append(VLSMAllocation(
            required_hosts=hosts,
            allocated_prefix=prefix,
            network=subnet,
            gateway=first_host if first_host else subnet.network_address,
            broadcast=subnet.broadcast_address,
            usable_hosts=usable,
            efficiency=efficiency
        ))
        
        current_addr += block_size
    
    # Reorder according to original index
    result = [None] * len(host_requirements)
    for i, (orig_idx, _) in enumerate(sorted_reqs):
        result[orig_idx] = allocations[i]
    
    return result


def ipv6_compress(address: str) -> str:
    """
    Compress an IPv6 address to minimal form.
    
    Args:
        address: IPv6 address in any valid format
    
    Returns:
        Compressed form (e.g.: '2001:db8::1')
    """
    addr = ipaddress.IPv6Address(address)
    return str(addr)


def ipv6_expand(address: str) -> str:
    """
    Expand an IPv6 address to full form.
    
    Args:
        address: IPv6 address in any format
    
    Returns:
        Full form with all zeros (e.g.: '2001:0db8:0000:...')
    """
    addr = ipaddress.IPv6Address(address)
    return addr.exploded


def ipv6_info(address_or_network: str) -> IPv6Info:
    """
    Analyse an IPv6 address or network.
    
    Args:
        address_or_network: IPv6 address or prefix
    
    Returns:
        IPv6Info with complete details
    """
    # Try first as network
    network = None
    try:
        if '/' in address_or_network:
            iface = ipaddress.IPv6Interface(address_or_network)
            addr = iface.ip
            network = iface.network
        else:
            addr = ipaddress.IPv6Address(address_or_network)
    except ValueError as e:
        raise ValueError(f"Invalid IPv6 address: {address_or_network}") from e
    
    # Determine type and scope
    if addr.is_loopback:
        addr_type = "loopback"
        scope = "node-local"
    elif addr.is_link_local:
        addr_type = "link-local"
        scope = "link-local"
    elif addr.is_site_local:
        addr_type = "site-local (deprecated)"
        scope = "site-local"
    elif addr.is_multicast:
        addr_type = "multicast"
        # Scope from second nibble
        scope_nibble = (int(addr) >> 112) & 0xF
        scope_map = {
            1: "interface-local",
            2: "link-local", 
            5: "site-local",
            8: "organisation-local",
            14: "global"
        }
        scope = scope_map.get(scope_nibble, f"scope-{scope_nibble}")
    elif addr.is_private:
        # Unique Local Address (fc00::/7)
        addr_type = "unique-local"
        scope = "global (private)"
    elif addr.is_global:
        addr_type = "global-unicast"
        scope = "global"
    else:
        addr_type = "other"
        scope = "unknown"
    
    return IPv6Info(
        full_form=addr.exploded,
        compressed=str(addr),
        exploded=addr.exploded,
        network=network,
        address_type=addr_type,
        scope=scope
    )


def ipv6_subnets_from_prefix(base_prefix: str, target_prefix: int, count: int) -> List[ipaddress.IPv6Network]:
    """
    Generate IPv6 subnets from a base prefix.
    
    Args:
        base_prefix: base prefix (e.g.: '2001:db8:10::/48')
        target_prefix: target prefix length (e.g.: 64)
        count: number of subnets to generate
    
    Returns:
        List of first N subnets with specified prefix
    """
    net = ipaddress.IPv6Network(base_prefix, strict=True)
    
    if target_prefix <= net.prefixlen:
        raise ValueError(f"Target prefix /{target_prefix} must be longer than /{net.prefixlen}")
    
    if target_prefix > 128:
        raise ValueError("Maximum IPv6 prefix is /128")
    
    all_subnets = net.subnets(new_prefix=target_prefix)
    result = []
    
    for i, subnet in enumerate(all_subnets):
        if i >= count:
            break
        result.append(subnet)
    
    return result


def validate_ip_in_network(ip: str, network: str) -> bool:
    """
    Check if an IP address belongs to a network.
    
    Args:
        ip: IP address to check
        network: network in CIDR format
    
    Returns:
        True if address belongs to network
    """
    try:
        addr = ipaddress.ip_address(ip)
        net = ipaddress.ip_network(network, strict=False)
        return addr in net
    except ValueError:
        return False


def is_valid_host_address(cidr: str) -> Tuple[bool, str]:
    """
    Check if a CIDR address can be used as host address.
    
    Args:
        cidr: address in format 'x.x.x.x/n'
    
    Returns:
        Tuple (is_valid, reason)
    """
    try:
        info = analyze_ipv4_interface(cidr)
        
        if info.address_type == "network":
            return False, f"Address {info.address} is the network address for {info.network}"
        elif info.address_type == "broadcast":
            return False, f"Address {info.address} is the broadcast address for {info.network}"
        else:
            return True, f"Valid host address in network {info.network}"
    
    except ValueError as e:
        return False, str(e)


def summarize_networks(networks: List[str]) -> List[ipaddress.IPv4Network]:
    """
    Summarise a list of IPv4 networks (supernetting/aggregation).
    
    Args:
        networks: list of networks in CIDR format
    
    Returns:
        List of summarised networks
    """
    nets = [ipaddress.ip_network(n, strict=False) for n in networks]
    return list(ipaddress.collapse_addresses(nets))


# Conversion and formatting functions
def netmask_to_prefix(netmask: str) -> int:
    """Convert a network mask to prefix length."""
    mask = ipaddress.IPv4Address(netmask)
    binary = bin(int(mask))[2:].zfill(32)
    return binary.count('1')


def prefix_to_netmask(prefix: int) -> str:
    """Convert a prefix length to network mask."""
    if not 0 <= prefix <= 32:
        raise ValueError("Prefix must be between 0 and 32")
    bits = '1' * prefix + '0' * (32 - prefix)
    octets = [int(bits[i:i+8], 2) for i in range(0, 32, 8)]
    return '.'.join(map(str, octets))


def ip_to_binary(ip: str) -> str:
    """Convert an IP address to binary representation."""
    addr = ipaddress.IPv4Address(ip)
    return bin(int(addr))[2:].zfill(32)


def ip_to_dotted_binary(ip: str) -> str:
    """Convert IP to binary with dots between octets."""
    binary = ip_to_binary(ip)
    return '.'.join([binary[i:i+8] for i in range(0, 32, 8)])


if __name__ == "__main__":
    # Quick demonstration
    print("=== Network Utilities Demonstration ===\n")
    
    # Test analyse
    info = analyze_ipv4_interface("192.168.10.14/26")
    print(f"Analysis 192.168.10.14/26:")
    print(f"  Network: {info.network}")
    print(f"  Mask: {info.netmask}")
    print(f"  Broadcast: {info.broadcast}")
    print(f"  Usable hosts: {info.usable_hosts}")
    print(f"  Range: {info.first_host} - {info.last_host}")
    print()
    
    # Test VLSM
    print("VLSM for 172.16.0.0/24 with requirements [60, 20, 10, 2]:")
    allocs = vlsm_allocate("172.16.0.0/24", [60, 20, 10, 2])
    for i, a in enumerate(allocs, 1):
        print(f"  {i}. {a.network} (required: {a.required_hosts}, usable: {a.usable_hosts}, eff: {a.efficiency:.1f}%)")
    print()
    
    # Test IPv6
    print("IPv6 2001:0db8:0000:0000:0000:0000:0000:0001:")
    v6 = ipv6_info("2001:0db8:0000:0000:0000:0000:0000:0001")
    print(f"  Compressed: {v6.compressed}")
    print(f"  Type: {v6.address_type}")
    print(f"  Scope: {v6.scope}")
