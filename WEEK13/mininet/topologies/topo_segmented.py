#!/usr/bin/env python3
"""Week 13 - Mininet segmented topology (IoT zone and management zone).

This topology demonstrates:
- network segmentation with a router between zones
- a minimal firewall policy that permits only MQTT traffic from the IoT zone
  to the management zone

Topology
--------
IoT zone (10.0.1.0/24):
  sensor1   10.0.1.11/24
  sensor2   10.0.1.12/24
  attacker  10.0.1.200/24

Management zone (10.0.2.0/24):
  broker      10.0.2.100/24
  controller  10.0.2.101/24

Router:
  r1-eth0  10.0.1.1/24
  r1-eth1  10.0.2.1/24

Firewall policy on r1 (illustrative):
- allow established and related flows
- allow TCP 1883 and 8883 from IoT -> broker
- drop other IoT -> management traffic

Usage
-----
Run (requires sudo):
  sudo python3 mininet/topologies/topo_segmented.py

From the Mininet CLI:
  mininet> pingall
  mininet> sensor1 ping broker
  mininet> sensor1 nc -vz 10.0.2.100 1883
  mininet> sensor1 nc -vz 10.0.2.100 80      # expected to be blocked by r1
"""

from __future__ import annotations

from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.net import Mininet
from mininet.node import Controller, Host, OVSSwitch
from mininet.topo import Topo


class LinuxRouter(Host):
    """A Host that acts as a simple IPv4 router."""

    def config(self, **params):
        super().config(**params)
        self.cmd("sysctl -w net.ipv4.ip_forward=1 >/dev/null")

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0 >/dev/null")
        super().terminate()


class SegmentedTopo(Topo):
    def build(self) -> None:
        s1 = self.addSwitch("s1")  # IoT switch
        s2 = self.addSwitch("s2")  # management switch

        r1 = self.addHost("r1", cls=LinuxRouter, ip="10.0.1.1/24")

        # IoT hosts
        sensor1 = self.addHost("sensor1", ip="10.0.1.11/24", defaultRoute="via 10.0.1.1")
        sensor2 = self.addHost("sensor2", ip="10.0.1.12/24", defaultRoute="via 10.0.1.1")
        attacker = self.addHost("attacker", ip="10.0.1.200/24", defaultRoute="via 10.0.1.1")

        # Management hosts
        broker = self.addHost("broker", ip="10.0.2.100/24", defaultRoute="via 10.0.2.1")
        controller = self.addHost("controller", ip="10.0.2.101/24", defaultRoute="via 10.0.2.1")

        # Links
        self.addLink(sensor1, s1, cls=TCLink)
        self.addLink(sensor2, s1, cls=TCLink)
        self.addLink(attacker, s1, cls=TCLink)

        self.addLink(broker, s2, cls=TCLink)
        self.addLink(controller, s2, cls=TCLink)

        # Router links
        self.addLink(r1, s1, intfName1="r1-eth0", params1={"ip": "10.0.1.1/24"}, cls=TCLink)
        self.addLink(r1, s2, intfName1="r1-eth1", params1={"ip": "10.0.2.1/24"}, cls=TCLink)


def configure_router_firewall(r1: Host) -> None:
    """Apply a minimal firewall policy on the router."""
    info("*** Applying firewall policy on r1\n")

    # Flush existing rules
    r1.cmd("iptables -F")
    r1.cmd("iptables -t nat -F")
    r1.cmd("iptables -t mangle -F")
    r1.cmd("iptables -X")

    # Default policies
    r1.cmd("iptables -P INPUT ACCEPT")
    r1.cmd("iptables -P OUTPUT ACCEPT")
    r1.cmd("iptables -P FORWARD DROP")

    # Allow established and related
    r1.cmd("iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT")

    # Allow IoT -> broker on MQTT ports
    r1.cmd("iptables -A FORWARD -s 10.0.1.0/24 -d 10.0.2.100/32 -p tcp --dport 1883 -j ACCEPT")
    r1.cmd("iptables -A FORWARD -s 10.0.1.0/24 -d 10.0.2.100/32 -p tcp --dport 8883 -j ACCEPT")

    # Allow management -> IoT (ICMP for diagnostics)
    r1.cmd("iptables -A FORWARD -s 10.0.2.0/24 -d 10.0.1.0/24 -p icmp -j ACCEPT")


def run() -> None:
    topo = SegmentedTopo()
    net = Mininet(
        topo=topo,
        controller=Controller,
        switch=OVSSwitch,
        autoSetMacs=True,
        autoStaticArp=True,
    )

    info("*** Starting Mininet\n")
    net.start()

    r1 = net.get("r1")
    configure_router_firewall(r1)

    info("\n*** Topology ready. Try: pingall\n")
    CLI(net)

    info("\n*** Stopping Mininet\n")
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()
