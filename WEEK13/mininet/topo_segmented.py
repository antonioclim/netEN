#!/usr/bin/env python3
"""Backwards-compatible wrapper for the segmented topology.

Preferred entrypoint:
  mininet/topologies/topo_segmented.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "topologies"))

from topo_segmented import run  # noqa: E402

if __name__ == "__main__":
    run()
