#!/usr/bin/env python3
"""Backwards-compatible wrapper for the base topology.

Preferred entrypoint:
  mininet/topologies/topo_base.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "topologies"))

from topo_base import run  # noqa: E402

if __name__ == "__main__":
    run()
