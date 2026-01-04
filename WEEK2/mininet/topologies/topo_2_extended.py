#!/usr/bin/env python3
"""Week 2 extended topology: two subnets and an L3 router.

Teaching idea:
- L2: L2: switches connect hosts within the same subnet (same prefix).
- L3: L3: the router connects different subnets and forwards packets based on its routing table.

Topologie:
  (h1,h2) -- s1 -- r1 -- s2 -- (h3,h4)

IP plan:
  h1: 10.0.2.11/24   gw 10.0.3.254
  h2: 10.0.2.12/24   gw 10.0.3.254
  h3: 10.0.3.13/24   gw 10.0.3.254
  h4: 10.0.3.14/24   gw 10.0.3.254
  r1-eth0: 10.0.3.254/24
  r1-eth1: 10.0.3.254/24

running:
  sudo python3 topo_2_extended.py --cli
"""

from __future__ import annotations

import argparse
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.net import Mininet
from mininet.node import Node, OVSController
from mininet.topo import Topo


class LinuxRouter(Node):
    """Node with IP forwarding active."""

    def config(self, **params):
        super().config(**params)
        self.cmd("sysctl -w net.ipv4.ip_forward=1")
        # rp_filter poate bloca packete in anumite scenarii of test; il dezactivam for laborator.
        self.cmd("sysctl -w net.ipv4.conf.all.rp_filter=0")
        self.cmd("sysctl -w net.ipv4.conf.default.rp_filter=0")

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0")
        super().terminate()


class S2ExtendedTopo(Topo):
    def build(self, bw: float = 10.0, delay: str = "5ms", loss: float = 0.0) -> None:
        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")
        r1 = self.addNode("r1", cls=LinuxRouter, ip="10.0.3.254/24")

        h1 = self.addHost("h1", ip="10.0.2.11/24", defaultRoute="via 10.0.3.254")
        h2 = self.addHost("h2", ip="10.0.2.12/24", defaultRoute="via 10.0.3.254")
        h3 = self.addHost("h3", ip="10.0.3.13/24", defaultRoute="via 10.0.3.254")
        h4 = self.addHost("h4", ip="10.0.3.14/24", defaultRoute="via 10.0.3.254")

        self.addLink(h1, s1, cls=TCLink, bw=bw, delay=delay, loss=loss)
        self.addLink(h2, s1, cls=TCLink, bw=bw, delay=delay, loss=loss)
        self.addLink(h3, s2, cls=TCLink, bw=bw, delay=delay, loss=loss)
        self.addLink(h4, s2, cls=TCLink, bw=bw, delay=delay, loss=loss)

        # r1-eth0 <-> s1, r1-eth1 <-> s2
        self.addLink(r1, s1, cls=TCLink, bw=bw, delay=delay, loss=loss)
        self.addLink(r1, s2, cls=TCLink, bw=bw, delay=delay, loss=loss)


def configure_router(net: Mininet) -> None:
    r1 = net.get("r1")
    # Setam adresa on interfata to s2 (eth1). eth0 a primit ip from params (10.0.3.254/24).
    r1.cmd("ip addr add 10.0.3.254/24 dev r1-eth1")
    r1.cmd("ip link set r1-eth0 up")
    r1.cmd("ip link set r1-eth1 up")
    info("*** Router configured: r1-eth0=10.0.3.254/24, r1-eth1=10.0.3.254/24\n")


def main() -> None:
    setLogLevel("info")
    ap = argparse.ArgumentParser()
    ap.add_argument("--bw", type=float, default=10.0)
    ap.add_argument("--delay", default="5ms")
    ap.add_argument("--loss", type=float, default=0.0)
    ap.add_argument("--cli", action="store_true", help="start interactive CLI")
    ap.add_argument("--test", action="store_true", help="runs un auto-test (ping + rute) şi opreşte")
    args = ap.parse_args()

    topo = S2ExtendedTopo(bw=args.bw, delay=args.delay, loss=args.loss)
    net = Mininet(topo=topo, controller=OVSController, link=TCLink, autoSetMacs=True)
    net.start()
    try:
        configure_router(net)
        if args.test:
            info("*** Auto-test: pingall()\n")
            net.pingAll()
            info("*** Auto-test: ping h1 -> h3 (traverseaza r1)\n")
            net.get('h1').cmd('ping -c 2 10.0.2.3')
            info("*** Auto-test finalizat.\n")
        elif args.cli:
            CLI(net)
        else:
            info("*** running fara CLI. Folositi --cli for explorare interactiva or --test for auto-test.\n")
    finally:
        net.stop()


if __name__ == "__main__":
    main()
