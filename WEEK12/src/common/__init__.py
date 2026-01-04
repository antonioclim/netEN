"""
Common utilities for Week 12 - Email and RPC protocols.
"""

from .net_utils import (
    setup_logging,
    is_port_available,
    is_port_open,
    wait_for_port,
    find_free_port,
    resolve_hostname,
    format_address,
    parse_address,
    validate_email,
    validate_hostname,
    tcp_connection,
    send_all,
    recv_until,
    recv_exactly,
    Timer,
    measure_latency,
)

__all__ = [
    'setup_logging',
    'is_port_available',
    'is_port_open',
    'wait_for_port',
    'find_free_port',
    'resolve_hostname',
    'format_address',
    'parse_address',
    'validate_email',
    'validate_hostname',
    'tcp_connection',
    'send_all',
    'recv_until',
    'recv_exactly',
    'Timer',
    'measure_latency',
]
