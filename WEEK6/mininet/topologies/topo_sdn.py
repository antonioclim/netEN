#!/usr/bin/env python3
"""
Seminar 6 – Mininet Topology: SDN with OpenFlow 1.3

Topology:
    h1 (10.0.6.11) ────┐
                       │
    h2 (10.0.6.12) ────┼──── s1 (OVS) ←───── Controller (OS-Ken)
                       │          ↑
    h3 (10.0.6.13) ────┘      OpenFlow 1.3

All hosts are in the same subnet (10.0.6.0/24).
Switch s1 is controlled by an external controller (OS-Ken) via OpenFlow.

Expected policy (implemented in controller):
- ✓ h1 ↔ h2: PERMIT (all traffic)
- ✗ * → h3: DROP (implicit, with configurable exceptions)
- ? UDP → h3: CONFIGURABLE in controller

Educational purpose:
- Understanding control plane / data plane separation
- Observing flow installation from controller
- Analysing flow table with ovs-ofctl
- Experimenting with allow/drop policies per protocol

Usage:
    # Terminal 1 - start the controller
    osken-manager seminar/python/controllers/sdn_policy_controller.py

    # Terminal 2 - start the topology
    sudo python3 topo_sdn.py --cli

Revolvix&Hypotheticalandrei
"""

from __future__ import annotations

import argparse
import sys

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info


class SDNTopology(Topo):
    """
    Simple SDN topology: 3 hosts connected to an OVS switch.
    
    The switch is configured to use OpenFlow 1.3 and connect
    to an external controller on port 6633.
    """
    
    def build(self):
        # OpenFlow switch
        s1 = self.addSwitch(
            "s1",
            cls=OVSSwitch,
            protocols="OpenFlow13"  # Explicit OpenFlow 1.3
        )
        
        # Hosts
        h1 = self.addHost("h1", ip="10.0.6.11/24")
        h2 = self.addHost("h2", ip="10.0.6.12/24")
        h3 = self.addHost("h3", ip="10.0.6.13/24")
        
        # Links
        # Connection order determines ports:
        #   port 1 → h1, port 2 → h2, port 3 → h3
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)


def run_smoke_test(net: Mininet) -> int:
    """
    Run tests to verify SDN policies.
    """
    h1, h2, h3 = net.get("h1", "h2", "h3")
    
    info("\n*** TEST 1: Ping h1 → h2 (PERMIT expected)\n")
    out1 = h1.cmd("ping -c 2 -W 3 10.0.6.12")
    ok1 = "0% packet loss" in out1 or " 2 received" in out1
    info(f"    Result: {'OK (PERMIT)' if ok1 else 'FAIL'}\n")
    
    info("*** TEST 2: Ping h1 → h3 (DROP expected)\n")
    out2 = h1.cmd("ping -c 2 -W 3 10.0.6.13")
    ok2 = "100% packet loss" in out2 or " 0 received" in out2
    info(f"    Result: {'OK (DROP)' if ok2 else 'FAIL - traffic got through!'}\n")
    
    info("\n*** Flow table s1:\n")
    flows = net.get("s1").cmd("ovs-ofctl -O OpenFlow13 dump-flows s1")
    info(flows + "\n")
    
    if ok1 and ok2:
        info("*** ALL TESTS PASSED ***\n")
        return 0
    else:
        info("*** SOME TESTS FAILED ***\n")
        return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="SDN topology with OpenFlow 1.3"
    )
    parser.add_argument("--cli", action="store_true", help="Interactive mode")
    parser.add_argument("--test", action="store_true", help="Smoke test")
    parser.add_argument(
        "--controller-ip", default="127.0.0.1",
        help="Controller IP (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--controller-port", type=int, default=6633,
        help="Controller port (default: 6633)"
    )
    args = parser.parse_args()
    
    topo = SDNTopology()
    
    # External controller (OS-Ken)
    # Must be started separately: osken-manager ...
    controller = RemoteController(
        "c0",
        ip=args.controller_ip,
        port=args.controller_port
    )
    
    net = Mininet(
        topo=topo,
        controller=controller,
        switch=OVSSwitch,
        link=TCLink,
        autoSetMacs=True
    )
    
    net.start()
    
    try:
        info("\n" + "="*60 + "\n")
        info("  SDN TOPOLOGY STARTED\n")
        info(f"  Controller: {args.controller_ip}:{args.controller_port}\n")
        info("  \n")
        info("  Implemented policies:\n")
        info("    ✓ h1 ↔ h2: PERMIT\n")
        info("    ✗ * → h3: DROP (ICMP, TCP)\n")
        info("    ? UDP → h3: Configurable (ALLOW_UDP_TO_H3)\n")
        info("  \n")
        info("  Useful commands:\n")
        info("    h1 ping 10.0.6.12\n")
        info("    h1 ping 10.0.6.13\n")
        info("    sh ovs-ofctl -O OpenFlow13 dump-flows s1\n")
        info("="*60 + "\n\n")
        
        if args.test:
            import time
            time.sleep(2)  # Wait for controller connection
            return run_smoke_test(net)
        elif args.cli:
            CLI(net)
        else:
            info("Topology started. Use --cli for interactive mode.\n")
        
        return 0
    finally:
        net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    sys.exit(main())
