#!/usr/bin/env python3
"""
Mininet Topology - Base: 2 Subnets + 1 Router
=============================================
Demonstrates static routing between two IPv4 subnets.

Architecture (Week 5 - IP Addressing):
    10.0.5.0/25              10.0.5.128/25
    (126 hosts)              (126 hosts)
        |                        |
       h1 -------- r1 -------- h2
    .11    .1          .129    .140

Port plan: WEEK_PORT_BASE = 5500

Usage:
    sudo python topo_5_base.py --test    # Automatic pingall test
    sudo python topo_5_base.py --cli     # Interactive CLI

© 2025 ASE-CSIE | Rezolvix&Hypotheticalandrei | MIT Licence
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

try:
    from mininet.net import Mininet
    from mininet.node import Node, OVSSwitch
    from mininet.cli import CLI
    from mininet.log import setLogLevel, info
    from mininet.link import TCLink
except ImportError:
    print("Error: Mininet is not installed.")
    print("Install: sudo apt-get install mininet openvswitch-switch")
    sys.exit(1)


class LinuxRouter(Node):
    """
    Linux node configured as router with IP forwarding enabled.
    """
    
    def config(self, **params):
        super().config(**params)
        # Enable IP forwarding
        self.cmd('sysctl -w net.ipv4.ip_forward=1')
        self.cmd('sysctl -w net.ipv6.conf.all.forwarding=1')
    
    def terminate(self):
        # Disable forwarding on stop (optional)
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super().terminate()


def build_base_topology() -> Mininet:
    """
    Build the base topology with 2 subnets and 1 router.
    
    Returns:
        Mininet: The configured network
    """
    info("*** Building base topology ***\n")
    
    net = Mininet(
        switch=OVSSwitch,
        link=TCLink,
        waitConnected=True
    )
    
    # ═══════════════════════════════════════════════════════
    # Address configuration (Week 5: 10.0.5.0/24 split into 2)
    # ═══════════════════════════════════════════════════════
    subnet1 = {
        'network': '10.0.5.0/25',
        'router_ip': '10.0.5.1/25',
        'host_ip': '10.0.5.11/25',
        'gateway': '10.0.5.1',
    }
    
    subnet2 = {
        'network': '10.0.5.128/25',
        'router_ip': '10.0.5.129/25',
        'host_ip': '10.0.5.140/25',
        'gateway': '10.0.5.129',
    }
    
    # ═══════════════════════════════════════════════════════
    # Create nodes
    # ═══════════════════════════════════════════════════════
    info("*** Adding router and hosts ***\n")
    
    # Router (with IP forwarding)
    r1 = net.addHost('r1', cls=LinuxRouter, ip=None)
    
    # Hosts
    h1 = net.addHost('h1', ip=subnet1['host_ip'], defaultRoute=f"via {subnet1['gateway']}")
    h2 = net.addHost('h2', ip=subnet2['host_ip'], defaultRoute=f"via {subnet2['gateway']}")
    
    # L2 switches (one per subnet)
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    
    # ═══════════════════════════════════════════════════════
    # Create links
    # ═══════════════════════════════════════════════════════
    info("*** Creating links ***\n")
    
    # Subnet 1 links
    net.addLink(h1, s1)
    net.addLink(r1, s1,
                intfName1='r1-eth0',
                params1={'ip': subnet1['router_ip']})
    
    # Subnet 2 links
    net.addLink(h2, s2)
    net.addLink(r1, s2,
                intfName1='r1-eth1',
                params1={'ip': subnet2['router_ip']})
    
    return net


def start_network(net: Mininet, run_test: bool = False, start_cli: bool = True):
    """
    Start the network and optionally run tests or CLI.
    """
    info("*** Starting network ***\n")
    net.start()
    
    # Configuration information
    info("\n*** Node configuration ***\n")
    for host in net.hosts:
        info(f"{host.name}:\n")
        info(f"  IP: {host.cmd('ip -4 addr show dev ' + host.defaultIntf().name + ' | grep inet').strip()}\n")
        if hasattr(host, 'defaultRoute') or host.name == 'r1':
            info(f"  Route: {host.cmd('ip route').strip()}\n")
    
    info("\n*** Topology ***\n")
    info("  h1 (10.0.5.11/25) --- s1 --- r1 --- s2 --- h2 (10.0.5.140/25)\n")
    info("                    10.0.5.1       10.0.5.129\n\n")
    
    if run_test:
        info("*** Running connectivity test (pingall) ***\n")
        packet_loss = net.pingAll()
        
        if packet_loss == 0:
            info("\n*** TEST PASSED: All nodes communicate! ***\n")
        else:
            info(f"\n*** TEST FAILED: {packet_loss}% packet loss ***\n")
        
        net.stop()
        return 0 if packet_loss == 0 else 1
    
    if start_cli:
        info("*** Useful commands ***\n")
        info("  nodes                     - list nodes\n")
        info("  net                       - display topology\n")
        info("  h1 ip addr                - h1 addresses\n")
        info("  h1 ip route               - h1 routes\n")
        info("  h1 ping -c 3 10.0.5.140   - ping to h2\n")
        info("  r1 ip route               - router routes\n")
        info("  r1 tcpdump -ni r1-eth0    - capture on router interface\n")
        info("  xterm h1                  - terminal for h1\n")
        info("  exit                      - exit\n\n")
        
        CLI(net)
    
    info("*** Stopping network ***\n")
    net.stop()
    return 0


def main(argv: Optional[list] = None) -> int:
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Mininet Topology - Base: 2 Subnets + 1 Router",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python %(prog)s --test    # Automatic test
  sudo python %(prog)s --cli     # Interactive CLI
  sudo python %(prog)s           # Just build and stop
"""
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--test", "-t",
        action="store_true",
        help="Run connectivity test (pingall) and exit"
    )
    group.add_argument(
        "--cli", "-c",
        action="store_true",
        help="Start interactive Mininet CLI"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Detailed output"
    )
    
    args = parser.parse_args(argv)
    
    # Set logging level
    if args.verbose:
        setLogLevel('debug')
    else:
        setLogLevel('info')
    
    # Build and run
    net = build_base_topology()
    return start_network(net, run_test=args.test, start_cli=args.cli)


if __name__ == "__main__":
    sys.exit(main())
