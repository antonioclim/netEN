"""Compatibility topology file for Week 7.

Earlier revisions referenced this file name.
Use:
- mininet/topologies/topo_week7_base.py for the one-subnet topology
- mininet/topologies/topo_week7_firewall.py for the router firewall topology

This module keeps a stable entry point for `mn --custom <topology_file>` commands.
"""

from topo_week7_base import Week7BaseTopo
from topo_week7_firewall import Week7FirewallTopo

topos = {
    "week7base": Week7BaseTopo,
    "week7fw": Week7FirewallTopo,
}
