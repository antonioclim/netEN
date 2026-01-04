"""Compatibility wrapper.

This file name existed in earlier iterations of the kit.
Canonical location: python/apps/port_probe.py
"""

from python.apps.port_probe import main

if __name__ == "__main__":
    raise SystemExit(main())
