#!/usr/bin/env python3
"""Week 6 SDN/OpenFlow topology (Mininet).

Topology
--------
    h1 (10.0.6.11/24) ─┐
                        ├── s1 (Open vSwitch, OpenFlow 1.3)
    h2 (10.0.6.12/24) ─┘        │
                               h3 (10.0.6.13/24)

Modes
-----
This script supports two SDN modes:

1) OVS-flow mode (default)
   The OpenFlow policy is installed directly into Open vSwitch, no controller
   process is required. This is the default because OS-Ken 4.x often does not
   ship the legacy `osken-manager` CLI and `os_ken.cmd.*` entry points.

2) Controller mode (legacy, optional)
   The switch connects to an external controller at --controller-ip/--controller-port.

Expected policy (minimal)
-------------------------
    ✓ h1 ↔ h2 : PERMIT
    ✗ h1 → h3 : DROP

Usage
-----
Interactive demo (recommended):
    sudo python3 topo_sdn.py --mode ovs --cli

Automated smoke test:
    sudo python3 topo_sdn.py --mode ovs --test

Controller mode (requires you to run a controller separately):
    sudo python3 topo_sdn.py --mode controller --controller-ip 127.0.0.1 --controller-port 6633 --cli
"""

from __future__ import annotations

import argparse
import time

from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.topo import Topo


class SDNTopo(Topo):
    """A simple SDN topology with three hosts and one switch."""

    def build(self) -> None:
        s1 = self.addSwitch("s1", cls=OVSSwitch, protocols="OpenFlow13")

        h1 = self.addHost("h1", ip="10.0.6.11/24")
        h2 = self.addHost("h2", ip="10.0.6.12/24")
        h3 = self.addHost("h3", ip="10.0.6.13/24")

        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)


def install_ovs_flows(net: Mininet) -> None:
    """Install a deterministic OpenFlow 1.3 policy directly into OVS."""

    s1 = net.get("s1")

    # Ensure OpenFlow 1.3 is enabled and do not fail open if a controller is absent.
    s1.cmd("ovs-vsctl set bridge s1 protocols=OpenFlow13")
    s1.cmd("ovs-vsctl set-fail-mode s1 secure")

    # Remove any previous rules.
    s1.cmd("ovs-ofctl -O OpenFlow13 del-flows s1")

    # Table-miss: drop everything by default.
    s1.cmd("ovs-ofctl -O OpenFlow13 add-flow s1 'priority=0,actions=drop'")

    # Allow ARP so hosts can resolve MAC addresses.
    s1.cmd("ovs-ofctl -O OpenFlow13 add-flow s1 'priority=100,arp,actions=normal'")

    # Allow IPv4 traffic between h1 and h2 in both directions.
    s1.cmd(
        "ovs-ofctl -O OpenFlow13 add-flow s1 'priority=200,ip,nw_src=10.0.6.11,nw_dst=10.0.6.12,actions=normal'"
    )
    s1.cmd(
        "ovs-ofctl -O OpenFlow13 add-flow s1 'priority=200,ip,nw_src=10.0.6.12,nw_dst=10.0.6.11,actions=normal'"
    )

    info("*** Installed OVS flow policy (no controller)\n")


def run_smoke_test(net: Mininet) -> int:
    """Run a minimal smoke test for the expected policy."""

    h1 = net.get("h1")
    h2 = net.get("h2")
    h3 = net.get("h3")
    s1 = net.get("s1")

    info("\n=== Running SDN smoke test ===\n")

    # Warm up ARP and verify permitted path.
    info("Testing PERMIT: h1 ↔ h2...\n")
    ping_ok = ("0% packet loss" in h1.cmd("ping -c 2 -W 1 10.0.6.12"))

    # Verify blocked path.
    info("Testing DROP: h1 → h3...\n")
    out = h1.cmd("ping -c 2 -W 1 10.0.6.13")
    ping_blocked = ("100% packet loss" in out) or ("0 received" in out)

    info("\n=== Current flows on s1 ===\n")
    info(s1.cmd("ovs-ofctl -O OpenFlow13 dump-flows s1"))

    if ping_ok and ping_blocked:
        info("*** ALL TESTS PASSED ***\n")
        return 0

    info("*** SOME TESTS FAILED ***\n")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Week 6 SDN/OpenFlow topology")
    parser.add_argument("--cli", action="store_true", help="Start interactive Mininet CLI")
    parser.add_argument("--test", action="store_true", help="Run automated smoke test and exit")

    parser.add_argument(
        "--mode",
        choices=["ovs", "controller"],
        default="ovs",
        help="SDN mode: 'ovs' installs OpenFlow rules directly in OVS, 'controller' uses an external controller",
    )
    parser.add_argument("--controller-ip", default="127.0.0.1", help="Controller IP (controller mode)")
    parser.add_argument("--controller-port", type=int, default=6633, help="Controller port (controller mode)")

    args = parser.parse_args()

    setLogLevel("info")

    topo = SDNTopo()

    if args.mode == "controller":
        controller = RemoteController("c0", ip=args.controller_ip, port=args.controller_port)
        net = Mininet(topo=topo, controller=controller, switch=OVSSwitch, link=TCLink, autoSetMacs=True)
    else:
        net = Mininet(topo=topo, controller=None, switch=OVSSwitch, link=TCLink, autoSetMacs=True)

    try:
        net.start()

        info("\n=== SDN Topology Started ===\n")
        info("h1: 10.0.6.11/24\n")
        info("h2: 10.0.6.12/24\n")
        info("h3: 10.0.6.13/24\n")
        if args.mode == "controller":
            info(f"Controller: {args.controller_ip}:{args.controller_port}\n")
        else:
            info("Controller: none (OVS flows)\n")

        if args.mode == "ovs":
            install_ovs_flows(net)

        if args.test:
            if args.mode == "controller":
                time.sleep(2)
            return run_smoke_test(net)

        # Default to CLI if not explicitly running tests.
        if args.cli or not args.test:
            CLI(net)
        return 0

    finally:
        net.stop()


if __name__ == "__main__":
    raise SystemExit(main())
