#!/usr/bin/env python3
"""Network utility helpers (Week 1)

This module is part of the transversal standard. In Week 1 it provides a small
set of helpers that can be reused by exercises and scripts without duplicating
logic.
"""

from __future__ import annotations

import ipaddress
import logging
from pathlib import Path


def setup_logging(log_path: Path) -> logging.Logger:
    """Create a logger that writes to both console and a file."""
    logger = logging.getLogger("week1")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    return logger


def is_valid_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def is_valid_port(port: int) -> bool:
    return 1 <= int(port) <= 65535
