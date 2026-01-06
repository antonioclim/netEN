#!/usr/bin/env python3
"""
net_utils.py - Networking utilities
Week 14 - Review and Integration
Computer Networks

Helper functions for:
- IP address validation and conversion
- Subnet calculation
- Parsing networking command output
- Formatting and logging
"""

import re
import socket
import struct
import subprocess
import logging
from typing import Tuple, List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

def setup_logging(
    name: str = "netutils",
    level: int = logging.INFO,
    fmt: str = "%(asctime)s [%(levelname)s] %(message)s"
) -> logging.Logger:
    """Configures and returns a logger."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(fmt, datefmt="%H:%M:%S"))
        logger.addHandler(handler)
    
    return logger


# =============================================================================
# IP ADDRESS VALIDATION
# =============================================================================

def is_valid_ipv4(ip: str) -> bool:
    """
    Checks if a string is a valid IPv4 address.
    
    Args:
        ip: String to verify
        
    Returns:
        True if valid IPv4, False otherwise
        
    Examples:
        >>> is_valid_ipv4("192.168.1.1")
        True
        >>> is_valid_ipv4("256.1.1.1")
        False
    """
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def is_valid_mac(mac: str) -> bool:
    """
    Checks if a string is a valid MAC address.
    
    Accepts formats:
    - aa:bb:cc:dd:ee:ff
    - aa-bb-cc-dd-ee-ff
    - aabbccddeeff
    
    Args:
        mac: String to verify
        
    Returns:
        True if valid MAC, False otherwise
    """
    # Normalise: remove separators
    mac_clean = mac.replace(":", "").replace("-", "").lower()
    
    if len(mac_clean) != 12:
        return False
    
    try:
        int(mac_clean, 16)
        return True
    except ValueError:
        return False


def is_valid_port(port: int) -> bool:
    """Checks if a port is valid (1-65535)."""
    return isinstance(port, int) and 1 <= port <= 65535


# =============================================================================
# IP CONVERSIONS
# =============================================================================

def ip_to_int(ip: str) -> int:
    """
    Converts IPv4 address to integer.
    
    Args:
        ip: IPv4 address (e.g.: "192.168.1.1")
        
    Returns:
        Integer representation (e.g.: 3232235777)
    """
    return struct.unpack("!I", socket.inet_aton(ip))[0]


def int_to_ip(num: int) -> str:
    """
    Converts integer to IPv4 address.
    
    Args:
        num: Integer (e.g.: 3232235777)
        
    Returns:
        IPv4 address (e.g.: "192.168.1.1")
    """
    return socket.inet_ntoa(struct.pack("!I", num))


def ip_to_binary(ip: str) -> str:
    """
    Converts IPv4 address to binary representation.
    
    Args:
        ip: IPv4 address (e.g.: "192.168.1.1")
        
    Returns:
        Binary string with dots (e.g.: "11000000.10101000.00000001.00000001")
    """
    octets = ip.split(".")
    return ".".join(format(int(o), "08b") for o in octets)


# =============================================================================
# SUBNET CALCULATION
# =============================================================================

@dataclass
class SubnetInfo:
    """Information about a subnet."""
    network: str
    broadcast: str
    first_host: str
    last_host: str
    netmask: str
    wildcard: str
    prefix: int
    total_hosts: int
    usable_hosts: int


def parse_cidr(cidr: str) -> Tuple[str, int]:
    """
    Parses CIDR notation into address and prefix.
    
    Args:
        cidr: CIDR notation (e.g.: "192.168.1.0/24")
        
    Returns:
        Tuple (ip, prefix)
        
    Raises:
        ValueError: If format is invalid
    """
    if "/" not in cidr:
        raise ValueError(f"Invalid CIDR notation: {cidr}")
    
    parts = cidr.split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid CIDR notation: {cidr}")
    
    ip, prefix_str = parts
    
    if not is_valid_ipv4(ip):
        raise ValueError(f"Invalid IP address: {ip}")
    
    try:
        prefix = int(prefix_str)
    except ValueError:
        raise ValueError(f"Invalid prefix: {prefix_str}")
    
    if not 0 <= prefix <= 32:
        raise ValueError(f"Prefix must be 0-32, got: {prefix}")
    
    return ip, prefix


def calculate_subnet(cidr: str) -> SubnetInfo:
    """
    Calculates complete information about a subnet.
    
    Args:
        cidr: CIDR notation (e.g.: "192.168.1.0/24")
        
    Returns:
        SubnetInfo with all subnet details
    """
    ip, prefix = parse_cidr(cidr)
    
    # Calculate mask
    mask_int = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
    netmask = int_to_ip(mask_int)
    wildcard = int_to_ip(~mask_int & 0xFFFFFFFF)
    
    # Calculate network and broadcast
    ip_int = ip_to_int(ip)
    network_int = ip_int & mask_int
    broadcast_int = network_int | (~mask_int & 0xFFFFFFFF)
    
    network = int_to_ip(network_int)
    broadcast = int_to_ip(broadcast_int)
    
    # Calculate first and last host
    total_hosts = 2 ** (32 - prefix)
    
    if prefix == 32:
        first_host = last_host = network
        usable_hosts = 1
    elif prefix == 31:
        first_host = network
        last_host = broadcast
        usable_hosts = 2
    else:
        first_host = int_to_ip(network_int + 1)
        last_host = int_to_ip(broadcast_int - 1)
        usable_hosts = total_hosts - 2
    
    return SubnetInfo(
        network=network,
        broadcast=broadcast,
        first_host=first_host,
        last_host=last_host,
        netmask=netmask,
        wildcard=wildcard,
        prefix=prefix,
        total_hosts=total_hosts,
        usable_hosts=usable_hosts
    )


def is_ip_in_subnet(ip: str, cidr: str) -> bool:
    """
    Checks if an IP address belongs to a subnet.
    
    Args:
        ip: IP address to verify
        cidr: Subnet in CIDR notation
        
    Returns:
        True if IP is in subnet
    """
    subnet = calculate_subnet(cidr)
    ip_int = ip_to_int(ip)
    network_int = ip_to_int(subnet.network)
    broadcast_int = ip_to_int(subnet.broadcast)
    
    return network_int <= ip_int <= broadcast_int


# =============================================================================
# COMMAND OUTPUT PARSING
# =============================================================================

def parse_ping_output(output: str) -> Dict[str, Any]:
    """
    Parses ping command output.
    
    Args:
        output: Text output from ping
        
    Returns:
        Dict with: packets_sent, packets_received, loss_percent, 
                 rtt_min, rtt_avg, rtt_max (if available)
    """
    result: Dict[str, Any] = {
        "packets_sent": 0,
        "packets_received": 0,
        "loss_percent": 100.0,
        "rtt_min": None,
        "rtt_avg": None,
        "rtt_max": None
    }
    
    # Search for packet statistics
    # Format: "3 packets transmitted, 3 received, 0% packet loss"
    pkt_match = re.search(
        r"(\d+) packets transmitted, (\d+) (?:packets )?received, (\d+(?:\.\d+)?)% packet loss",
        output
    )
    if pkt_match:
        result["packets_sent"] = int(pkt_match.group(1))
        result["packets_received"] = int(pkt_match.group(2))
        result["loss_percent"] = float(pkt_match.group(3))
    
    # Search for RTT statistics
    # Format: "rtt min/avg/max/mdev = 0.123/0.456/0.789/0.111 ms"
    rtt_match = re.search(
        r"rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+) ms",
        output
    )
    if rtt_match:
        result["rtt_min"] = float(rtt_match.group(1))
        result["rtt_avg"] = float(rtt_match.group(2))
        result["rtt_max"] = float(rtt_match.group(3))
    
    return result


def parse_netstat_output(output: str) -> List[Dict[str, str]]:
    """
    Parses netstat -tlnp or ss -tlnp command output.
    
    Args:
        output: Text output
        
    Returns:
        List of dicts with: protocol, local_addr, local_port, state, process
    """
    connections = []
    lines = output.strip().split("\n")
    
    for line in lines[1:]:  # Skip header
        parts = line.split()
        if len(parts) < 4:
            continue
        
        # Parse local address
        local = parts[3] if len(parts) > 3 else ""
        if ":" in local:
            addr, port = local.rsplit(":", 1)
        else:
            addr, port = local, ""
        
        conn = {
            "protocol": parts[0] if parts else "",
            "local_addr": addr.strip("[]"),
            "local_port": port,
            "state": parts[5] if len(parts) > 5 else "",
            "process": parts[-1] if len(parts) > 6 else ""
        }
        connections.append(conn)
    
    return connections


# =============================================================================
# COMMAND EXECUTION
# =============================================================================

def run_command(
    cmd: List[str],
    timeout: int = 30,
    capture_stderr: bool = True
) -> Tuple[int, str, str]:
    """
    Executes a command and returns the result.
    
    Args:
        cmd: List of command arguments
        timeout: Timeout in seconds
        capture_stderr: Whether to capture stderr
        
    Returns:
        Tuple (return_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Command exceeded timeout after {timeout}s"
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"
    except Exception as e:
        return -1, "", str(e)


def check_port_open(host: str, port: int, timeout: float = 3.0) -> bool:
    """
    Checks if a port is open.
    
    Args:
        host: Hostname or IP
        port: Port number
        timeout: Timeout in seconds
        
    Returns:
        True if port is open
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except socket.error:
        return False


def resolve_hostname(hostname: str) -> Optional[str]:
    """
    Resolves a hostname to IP address.
    
    Args:
        hostname: Name to resolve
        
    Returns:
        IP address or None if resolution fails
    """
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None


# =============================================================================
# OUTPUT FORMATTING
# =============================================================================

def format_bytes(num_bytes: int) -> str:
    """
    Formats a number of bytes in human-readable format.
    
    Args:
        num_bytes: Number of bytes
        
    Returns:
        Formatted string (e.g.: "1.5 KB", "2.3 MB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    Formats a duration in seconds in human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g.: "1m 30s", "2h 15m")
    """
    if seconds < 1:
        return f"{seconds*1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"


def format_table(
    headers: List[str],
    rows: List[List[str]],
    separator: str = " | "
) -> str:
    """
    Formats data into an aligned text table.
    
    Args:
        headers: List of headers
        rows: List of rows (each row is a list of values)
        separator: Separator between columns
        
    Returns:
        Formatted table as string
    """
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(str(cell)))
    
    # Format header
    header_line = separator.join(h.ljust(widths[i]) for i, h in enumerate(headers))
    separator_line = "-" * len(header_line)
    
    # Format rows
    row_lines = []
    for row in rows:
        cells = [str(cell).ljust(widths[i]) for i, cell in enumerate(row)]
        row_lines.append(separator.join(cells))
    
    return "\n".join([header_line, separator_line] + row_lines)


# =============================================================================
# TIMESTAMPS
# =============================================================================

def get_timestamp() -> str:
    """Returns timestamp in ISO format."""
    return datetime.now().isoformat(timespec="seconds")


def get_timestamp_filename() -> str:
    """Returns timestamp for filename (no special characters)."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# =============================================================================
# MAIN - FOR TESTING
# =============================================================================

if __name__ == "__main__":
    # Quick tests
    print("=== Test IP Validation ===")
    print(f"192.168.1.1 valid: {is_valid_ipv4('192.168.1.1')}")
    print(f"256.1.1.1 valid: {is_valid_ipv4('256.1.1.1')}")
    
    print("\n=== Test MAC Validation ===")
    print(f"aa:bb:cc:dd:ee:ff valid: {is_valid_mac('aa:bb:cc:dd:ee:ff')}")
    print(f"aabbccddeeff valid: {is_valid_mac('aabbccddeeff')}")
    
    print("\n=== Test IP Conversion ===")
    ip = "192.168.1.1"
    num = ip_to_int(ip)
    print(f"{ip} -> {num} -> {int_to_ip(num)}")
    print(f"Binary: {ip_to_binary(ip)}")
    
    print("\n=== Test Subnet Calculation ===")
    subnet = calculate_subnet("192.168.1.0/24")
    print(f"Network: {subnet.network}")
    print(f"Broadcast: {subnet.broadcast}")
    print(f"First host: {subnet.first_host}")
    print(f"Last host: {subnet.last_host}")
    print(f"Usable hosts: {subnet.usable_hosts}")
    
    print("\n=== Test Port Check ===")
    print(f"localhost:22 open: {check_port_open('localhost', 22, 1)}")
    
    print("\n=== Test Formatting ===")
    print(f"1536 bytes: {format_bytes(1536)}")
    print(f"125.5 seconds: {format_duration(125.5)}")
    
    print("\n=== Test Table ===")
    headers = ["Host", "IP", "Status"]
    rows = [
        ["app1", "10.0.14.100", "UP"],
        ["app2", "10.0.14.101", "UP"],
        ["cli", "10.0.14.11", "UP"]
    ]
    print(format_table(headers, rows))
