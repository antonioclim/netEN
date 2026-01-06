#!/usr/bin/env python3
"""Week 10 - Base routed Mininet topology.

This topology creates two IPv4 subnets separated by a Linux router.
It is intended for basic routing exercises and packet captures.
"""

from __future__ import annotations

import argparse
import sys

from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.net import Mininet
from mininet.node import Controller, Node, OVSKernelSwitch
from mininet.topo import Topo


class LinuxRouter(Node):
    """A Node with IPv4 forwarding enabled."""

    def config(self, **params):
        super().config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super().terminate()


class BaseTopo(Topo):
    """h1 --- r1 --- h2 (two subnets)."""

    def build(self):
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        h1 = self.addHost('h1', ip='10.0.1.10/24', defaultRoute='via 10.0.1.1')
        h2 = self.addHost('h2', ip='10.0.2.10/24', defaultRoute='via 10.0.2.1')

        r1 = self.addNode('r1', cls=LinuxRouter, ip='10.0.1.1/24')

        self.addLink(h1, s1)
        self.addLink(s1, r1, intfName2='r1-eth0', params2={'ip': '10.0.1.1/24'})

        self.addLink(h2, s2)
        self.addLink(s2, r1, intfName2='r1-eth1', params2={'ip': '10.0.2.1/24'})


def run_tests(net: Mininet) -> bool:
    """Basic reachability test between subnets."""

    info('*** Running base topology tests\n')
    h1 = net.get('h1')
    h2 = net.get('h2')

    out = h1.cmd('ping -c 2 -W 1 10.0.2.10')
    ok = (' 0% packet loss' in out) or ('2 received' in out)
    info(f"*** h1 -> h2 ping: {'PASS' if ok else 'FAIL'}\n")
    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description='Week 10 base Mininet topology')
    parser.add_argument('--test', action='store_true', help='Run a small automated test and exit')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose Mininet logs')
    args = parser.parse_args()

    setLogLevel('debug' if args.verbose else 'info')

    topo = BaseTopo()
    net = Mininet(
        topo=topo,
        controller=Controller,
        switch=OVSKernelSwitch,
        link=TCLink,
        build=True,
        autoSetMacs=True,
    )

    try:
        info('*** Starting network\n')
        net.start()

        if args.test:
            ok = run_tests(net)
            sys.exit(0 if ok else 1)

        info('\n*** Interactive CLI\n')
        info('Try: h1 ping 10.0.2.10\n')
        info('Try: r1 ip route\n')
        info('Try: h1 traceroute 10.0.2.10\n\n')
        CLI(net)

    finally:
        info('*** Stopping network\n')
        net.stop()


if __name__ == '__main__':
    main()
