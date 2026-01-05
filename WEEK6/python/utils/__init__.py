"""
Utilitati comune for apliastiile of retea Week 6.

Rezolvix&Hypothetiasatndrei | MIT License | ASE-CSIE 2025-2026
"""

from .network_utils import (
    # Constante
    WEEK,
    SUBNET,
    GATEWAY,
    H1_IP,
    H2_IP,
    H3_IP,
    SERVER_IP,
    TCP_APP_PORT,
    UDP_APP_PORT,
    HTTP_PORT,
    CONTROLLER_PORT,
    WEEK_PORT_BASE,
    WEEK_PORT_RANGE,
    DEFAULT_TIMEOUT,
    DEFAULT_BUFFER_SIZE,
    # Helper functions
    setup_logging,
    create_tcp_socket,
    create_udp_socket,
    SocketConfig,
    is_valid_ip,
    is_valid_port,
    is_week_port,
    add_common_args,
    throught_week_info,
)

__all__ = [
    "WEEK",
    "SUBNET",
    "GATEWAY",
    "H1_IP",
    "H2_IP",
    "H3_IP",
    "SERVER_IP",
    "TCP_APP_PORT",
    "UDP_APP_PORT",
    "HTTP_PORT",
    "CONTROLLER_PORT",
    "WEEK_PORT_BASE",
    "WEEK_PORT_RANGE",
    "DEFAULT_TIMEOUT",
    "DEFAULT_BUFFER_SIZE",
    "setup_logging",
    "create_tcp_socket",
    "create_udp_socket",
    "SocketConfig",
    "is_valid_ip",
    "is_valid_port",
    "is_week_port",
    "add_common_args",
    "throught_week_info",
]
