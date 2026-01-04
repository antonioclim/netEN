#!/usr/bin/env python3
"""Mininet scenario (optional): TCP TEXT and BINARY demos for Week 4.

This script creates a tiny topology and runs:
- TEXT server on h2 (TCP/5400), client on h1
- BINARY server on h2 (TCP/5401), client on h1

Subnet convention: 10.0.4.0/24
Clean up after use:
- sudo mn -c
"""

from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel, info
import os
import time


def run():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    apps_dir = os.path.join(root_dir, "python", "apps")

    net = Mininet(controller=Controller, switch=OVSSwitch, link=TCLink, autoSetMacs=True)

    info("*** Creating nodes\n")
    c0 = net.addController("c0")
    s1 = net.addSwitch("s1")

    h1 = net.addHost("h1", ip="10.0.4.11/24")
    h2 = net.addHost("h2", ip="10.0.4.12/24")

    net.addLink(h1, s1, bw=10, delay="5ms")
    net.addLink(h2, s1, bw=10, delay="5ms")

    info("*** Starting network\n")
    net.start()

    info("*** Starting TCP servers on h2\n")
    h2.cmd(f"cd {apps_dir} && python3 text_proto_server.py --host 0.0.0.0 --port 5400 > /tmp/week4_text_server.log 2>&1 &")
    h2.cmd(f"cd {apps_dir} && python3 binary_proto_server.py --host 0.0.0.0 --port 5401 > /tmp/week4_bin_server.log 2>&1 &")
    time.sleep(1)

    info("*** Running TCP clients on h1\n")
    h1.cmd(
        f"cd {apps_dir} && python3 text_proto_client.py --host 10.0.4.12 --port 5400 "
        f"-c PING -c 'SET name Alice' -c 'GET name' -c QUIT"
    )
    h1.cmd(
        f"cd {apps_dir} && python3 binary_proto_client.py --host 10.0.4.12 --port 5401 --demo"
    )

    info("*** Done. Check logs on h2: /tmp/week4_text_server.log and /tmp/week4_bin_server.log\n")
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()
