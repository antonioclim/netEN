#!/usr/bin/env python3
"""Mininet scenario (optional): UDP sensor demo for Week 4.

This script creates a tiny topology and runs:
- UDP sensor server on h2
- UDP sensor client on h1 (sends a short sequence)

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

    info("*** Starting UDP sensor server on h2\n")
    server_cmd = f"cd {apps_dir} && python3 udp_sensor_server.py --host 0.0.0.0 --port 5402 --once"
    h2.cmd(server_cmd + " > /tmp/week4_udp_server.log 2>&1 &")
    time.sleep(1)

    info("*** Sending UDP sensor messages from h1\n")
    temps = [22.5, 23.1, 22.8]
    for t in temps:
        client_cmd = (
            f"cd {apps_dir} && python3 udp_sensor_client.py --host 10.0.4.12 --port 5402 "
            f"--sensor-id 1001 --temperature {t} --location Lab_A1 --count 1"
        )
        h1.cmd(client_cmd)
        time.sleep(0.2)

    info("*** Done. Check /tmp/week4_udp_server.log on h2 for output\n")
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()
