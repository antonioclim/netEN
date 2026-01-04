#!/usr/bin/env python3
"""Wrapper kept for backwards compatibility.

Canonical location: python/apps/firewallctl.py
"""

from python.apps.firewallctl import main

if __name__ == "__main__":
    raise SystemExit(main())
