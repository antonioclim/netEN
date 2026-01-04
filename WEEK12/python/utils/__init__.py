#!/usr/bin/env python3
"""
python/utils/__init__.py — Wrapper For src/common

Acest Module este un wrapper For utilitarele canonice din src/common.
Toate functiile sunt re-exportate For compatibilitate cu structura standard.

Utilizare:
    from python.utils import is_port_available, wait_for_port
    # sau
    from python.utils.net_utils import validate_email, resolve_hostname

Note: Implementarea canonica se afla in src/common/net_utils.py
"""

import sys
from pathlib import Path

# Adauga src/ in path For import
_project_root = Path(__file__).parent.parent.parent
_src_path = _project_root / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

# Re-export toate functiile din src/common/net_utils
from common.net_utils import (
    # Logging
    setup_logging,
    
    # Port utilities
    is_port_available,
    is_port_open,
    wait_for_port,
    find_free_port,
    
    # DNS
    resolve_hostname,
    resolve_hostname_full,
    get_mx_records,
    
    # Formatare
    format_address,
    parse_address,
    validate_email,
    validate_hostname,
    
    # Socket helpers
    tcp_connection,
    send_all,
    recv_until,
    recv_exactly,
    
    # Timing
    Timer,
    measure_latency,
    
    # Protocol helpers
    create_smtp_ehlo,
    create_smtp_mail_from,
    create_smtp_rcpt_to,
    parse_smtp_response,
)

__all__ = [
    'setup_logging',
    'is_port_available',
    'is_port_open',
    'wait_for_port',
    'find_free_port',
    'resolve_hostname',
    'resolve_hostname_full',
    'get_mx_records',
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
    'create_smtp_ehlo',
    'create_smtp_mail_from',
    'create_smtp_rcpt_to',
    'parse_smtp_response',
]
