#!/usr/bin/env python3
"""Week 13 - Mininet base topology (flat network).

This is a simple reference topology used to illustrate:
- basic host connectivity
- the effect of an attacker host being in the same broadcast domain
- how traffic capture and basic reconnaissance looks in a small network

Topology
--------
Single switch (s1) with five hosts:

  sensor1     10.0.1.11/24
  sensor2     10.0.1.12/24
  broker      10.0.1.100/24
  controller  10.0.1.101/24
  attacker    10.0.1.200/24

Usage
-----
Run (requires sudo):
  sudo python3 mininet/topologies/topo_base.py

Then from the Mininet CLI:
  mininet> pingall
  mininet> sensor1 ping broker
  mininet> attacker arp -a
"""

from __future__ import annotations

from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.topo import Topo


class IoTBaseTopo(Topo):
    def build(self) -> None:
        s1 = self.addSwitch("s1")

        hosts = {
            "sensor1": "10.0.1.11/24",
            "sensor2": "10.0.1.12/24",
            "broker": "10.0.1.100/24",
            "controller": "10.0.1.101/24",
            "attacker": "10.0.1.200/24",
        }

        for name, ip in hosts.items():
            h = self.addHost(name, ip=ip)
            self.addLink(h, s1, cls=TCLink)


def run() -> None:
    topo = IoTBaseTopo()
    net = Mininet(
        topo=topo,
        controller=Controller,
        switch=OVSSwitch,
        link=TCLink,
        autoSetMacs=True,
        autoStaticArp=True,
    )

    info("*** Starting Mininet\n")
    net.start()

    info("\n*** Topology ready. Try: pingall\n")
    CLI(net)

    info("\n*** Stopping Mininet\n")
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()
