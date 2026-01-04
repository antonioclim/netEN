#!/usr/bin/env python3
"""Mininet scenario (optional): ARP demonstration for Week 4.

Creates three hosts connected to one switch and shows how ARP tables change
before and after traffic is generated.

Subnet convention: 10.0.4.0/24
Clean up after use:
- sudo mn -c
"""

from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel, info
import time


def run():
    net = Mininet(controller=Controller, switch=OVSSwitch, link=TCLink, autoSetMacs=True)

    info("*** Creating nodes\n")
    net.addController("c0")
    s1 = net.addSwitch("s1")

    h1 = net.addHost("h1", ip="10.0.4.11/24")
    h2 = net.addHost("h2", ip="10.0.4.12/24")
    h3 = net.addHost("h3", ip="10.0.4.13/24")

    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)

    info("*** Starting network\n")
    net.start()

    info("*** ARP tables before traffic\n")
    info(h1.cmd("arp -n || ip neigh"))
    info(h2.cmd("arp -n || ip neigh"))

    info("*** Generating traffic (ping)\n")
    h1.cmd("ping -c 1 10.0.4.12 >/dev/null 2>&1 || true")
    h2.cmd("ping -c 1 10.0.4.11 >/dev/null 2>&1 || true")
    time.sleep(0.5)

    info("*** ARP tables after traffic\n")
    info(h1.cmd("arp -n || ip neigh"))
    info(h2.cmd("arp -n || ip neigh"))

    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()
