#!/usr/bin/env python3
"""Wrapper kept for backwards compatibility.

Canonical location: python/apps/port_probe.py
"""

from python.apps.port_probe import main

if __name__ == "__main__":
    raise SystemExit(main())
