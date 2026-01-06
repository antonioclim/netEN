#!/usr/bin/env python3
"""
python/utils/ — Common utilities for the S14 starter kit
Computer Networks — CSIE/ASE

Available modules:
  - net_utils: helper functions for networking
"""

from .net_utils import (
    # Validare
    is_valid_ipv4,
    is_valid_mac,
    is_valid_port,
    # Conversii IP
    ip_to_int,
    int_to_ip,
    ip_to_binary,
    # Subnet
    SubnetInfo,
    parse_cidr,
    calculate_subnet,
    is_ip_in_subnet,
    # Parsare
    parse_ping_output,
    parse_netstat_output,
    # Comenzi
    run_command,
    check_port_open,
    resolve_hostname,
    # Formatare
    format_bytes,
    format_duration,
    format_table,
    # Timestamp
    get_timestamp,
    get_timestamp_filename,
    # Logging
    setup_logging,
)

__version__ = "1.0.0"
__all__ = [
    "is_valid_ipv4",
    "is_valid_mac",
    "is_valid_port",
    "ip_to_int",
    "int_to_ip",
    "ip_to_binary",
    "SubnetInfo",
    "parse_cidr",
    "calculate_subnet",
    "is_ip_in_subnet",
    "parse_ping_output",
    "parse_netstat_output",
    "run_command",
    "check_port_open",
    "resolve_hostname",
    "format_bytes",
    "format_duration",
    "format_table",
    "get_timestamp",
    "get_timestamp_filename",
    "setup_logging",
]
