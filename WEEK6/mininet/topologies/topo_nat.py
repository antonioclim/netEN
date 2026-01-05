#!/usr/bin/env python3
"""
Seminar 6 – Mininet Topology: NAT/PAT

Topology:
    (private)                      (public)
   h1 ───┐                        ┌─── h3
        s1 ─── rnat ─── s2 ───────┘
   h2 ───┘

Addressing:
- h1: 192.168.1.10/24   gw 192.168.1.1
- h2: 192.168.1.20/24   gw 192.168.1.1
- rnat(private): 192.168.1.1/24
- rnat(public): 203.0.113.1/24  (TEST-NET-3, RFC 5737)
- h3: 203.0.113.2/24    gw 203.0.113.1

Educational purpose:
- Demonstrating PAT translation (MASQUERADE)
- Observing the difference between private and public addresses
- Understanding the NAT table and bidirectional mapping

Usage:
    sudo python3 topo_nat.py --cli     # Interactive mode
    sudo python3 topo_nat.py --test    # Automated smoke test

Revolvix&Hypotheticalandrei
"""

from __future__ import annotations

import argparse
import sys

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, OVSSwitch
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info


class LinuxRouter(Node):
    """
    Mininet node configured as a Linux router.
    
    Enables IP forwarding and provides cleanup for NAT rules.
    """
    
    def config(self, **params):
        super().config(**params)
        # Enable IPv4 forwarding
        self.cmd("sysctl -w net.ipv4.ip_forward=1")

    def terminate(self):
        # Clean up iptables rules on shutdown
        self.cmd("iptables -t nat -F 2>/dev/null || true")
        self.cmd("iptables -F 2>/dev/null || true")
        super().terminate()


class NatTopology(Topo):
    """
    NAT topology with:
    - 2 private hosts (h1, h2)
    - 1 Linux router with NAT (rnat)
    - 1 "public" host (h3)
    - 2 OVS switches (s1 private, s2 public)
    """
    
    def build(self):
        # Switches
        s1 = self.addSwitch("s1")  # Private network
        s2 = self.addSwitch("s2")  # Public network
        
        # Linux router with NAT
        rnat = self.addNode("rnat", cls=LinuxRouter)
        
        # Hosts
        h1 = self.addHost("h1")
        h2 = self.addHost("h2")
        h3 = self.addHost("h3")
        
        # Links
        self.addLink(h1, s1)       # h1-eth0 ↔ s1
        self.addLink(h2, s1)       # h2-eth0 ↔ s1
        self.addLink(s1, rnat)     # rnat-eth0 (private)
        self.addLink(rnat, s2)     # rnat-eth1 (public)
        self.addLink(s2, h3)       # h3-eth0 ↔ s2


def configure_network(net: Mininet) -> None:
    """
    Configure IP addresses, routes and NAT rules.
    
    This function demonstrates:
    1. Configuring addresses on specific interfaces
    2. Adding default routes (default gateway)
    3. Configuring NAT with iptables (MASQUERADE)
    """
    h1, h2, h3 = net.get("h1", "h2", "h3")
    rnat = net.get("rnat")
    
    # === IP address configuration ===
    # Private network (192.168.1.0/24)
    h1.setIP("192.168.1.10/24", intf="h1-eth0")
    h2.setIP("192.168.1.20/24", intf="h2-eth0")
    rnat.setIP("192.168.1.1/24", intf="rnat-eth0")
    
    # Public network (203.0.113.0/24 - TEST-NET-3)
    rnat.setIP("203.0.113.1/24", intf="rnat-eth1")
    h3.setIP("203.0.113.2/24", intf="h3-eth0")
    
    # === Route configuration ===
    # Private hosts use rnat as default gateway
    h1.cmd("ip route add default via 192.168.1.1")
    h2.cmd("ip route add default via 192.168.1.1")
    # Public host also uses rnat (for simplicity)
    h3.cmd("ip route add default via 203.0.113.1")
    
    # === NAT configuration (iptables) ===
    # Clear existing rules to avoid duplication
    rnat.cmd("iptables -t nat -F")
    rnat.cmd("iptables -F")
    
    # Allow forwarding between interfaces
    rnat.cmd("iptables -A FORWARD -i rnat-eth0 -o rnat-eth1 -j ACCEPT")
    rnat.cmd("iptables -A FORWARD -i rnat-eth1 -o rnat-eth0 "
             "-m state --state ESTABLISHED,RELATED -j ACCEPT")
    
    # NAT MASQUERADE for traffic from private network
    # MASQUERADE: automatically uses the outgoing interface's IP
    rnat.cmd("iptables -t nat -A POSTROUTING -o rnat-eth1 "
             "-s 192.168.1.0/24 -j MASQUERADE")
    
    info("*** NAT configuration complete\n")
    info("*** h1/h2 (192.168.1.x) → NAT → 203.0.113.1 → h3\n")


def run_smoke_test(net: Mininet) -> int:
    """
    Run basic tests to verify functionality.
    
    Returns:
        0 if all tests pass, 1 otherwise
    """
    h1, h2, h3 = net.get("h1", "h2", "h3")
    rnat = net.get("rnat")
    
    info("\n*** TEST 1: Ping h1 → h3 (through NAT)\n")
    out1 = h1.cmd("timeout 4s ping -c 1 -W 1 203.0.113.2")
    ok1 = "0% packet loss" in out1 or "2 received" in out1
    info(f"    Result: {'OK' if ok1 else 'FAIL'}\n")
    
    info("*** TEST 2: Ping h2 → h3 (through NAT)\n")
    out2 = h2.cmd("timeout 4s ping -c 1 -W 1 203.0.113.2")
    ok2 = "0% packet loss" in out2 or "2 received" in out2
    info(f"    Result: {'OK' if ok2 else 'FAIL'}\n")
    
    info("*** TEST 3: Verify NAT table\n")
    nat_table = rnat.cmd("iptables -t nat -L -n -v")
    ok3 = "MASQUERADE" in nat_table
    info(f"    MASQUERADE present: {'OK' if ok3 else 'FAIL'}\n")
    
    info("\n*** NAT table (rnat):\n")
    info(nat_table + "\n")
    
    if ok1 and ok2 and ok3:
        info("*** ALL TESTS PASSED ***\n")
        return 0
    else:
        info("*** SOME TESTS FAILED ***\n")
        if not ok1:
            info(f"    h1 ping output: {out1}\n")
        if not ok2:
            info(f"    h2 ping output: {out2}\n")
        return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Mininet topology for NAT/PAT demonstration"
    )
    parser.add_argument(
        "--cli", action="store_true",
        help="Launch interactive Mininet CLI"
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Run automated smoke test"
    )
    args = parser.parse_args()
    
    # Build topology
    topo = NatTopology()
    net = Mininet(
        topo=topo,
        controller=None,      # No SDN controller needed
        switch=OVSSwitch,
        link=TCLink,
        autoSetMacs=True      # Predictable MACs
    )
    
    net.start()
    
    try:
        configure_network(net)
        
        if args.test:
            return run_smoke_test(net)
        elif args.cli:
            info("\n" + "="*60 + "\n")
            info("  NAT/PAT TOPOLOGY STARTED\n")
            info("  Useful commands:\n")
            info("    h1 ping 203.0.113.2\n")
            info("    rnat iptables -t nat -L -n -v\n")
            info("    h3 tcpdump -ni h3-eth0 icmp\n")
            info("="*60 + "\n\n")
            CLI(net)
        else:
            info("Topology started. Use --cli for interactive mode.\n")
        
        return 0
    finally:
        net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    sys.exit(main())
