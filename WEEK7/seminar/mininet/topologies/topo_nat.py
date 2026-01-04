#!/usr/bin/env python3
"""
NAT Topology Wrapper for Seminar Exercises
==========================================

This file imports and re-exports the canonical NAT topology
from mininet/topologies/topo_nat.py to avoid code duplication
whilst maintaining the expected seminar folder structure.

For implementation details, see: ../../mininet/topologies/topo_nat.py
"""

import sys
from pathlib import Path

# Add canonical topology directory to path
CANONICAL_TOPO_DIR = Path(__file__).parent.parent.parent.parent / "mininet" / "topologies"
sys.path.insert(0, str(CANONICAL_TOPO_DIR))

# Import all public names from canonical implementation
from topo_nat import *

# Preserve direct execution capability
if __name__ == '__main__':
    import topo_nat
    # Re-run canonical module's main
    sys.exit(0 if topo_nat.__name__ == '__main__' else 1)
