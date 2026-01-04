#!/usr/bin/env python3
"""Wrapper kept for backwards compatibility.

Canonical location: python/apps/tcp_client.py
"""

from python.apps.tcp_client import main

if __name__ == "__main__":
    raise SystemExit(main())
