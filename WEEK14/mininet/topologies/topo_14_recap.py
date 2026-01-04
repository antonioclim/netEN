#!/usr/bin/env python3
"""topo_14_recap.py — Mininet topology for Week 14 (Review).

Compact topology for load balancing demonstrations and diagnostics:

    cli ─── s1 ─── s2 ─── app1
             │       └─── app2
             └─── lb

Fixed IPs (class /24) — according to W14 plan:
  cli  : 10.0.14.11  (client)
  app1 : 10.0.14.100 (backend 1)
  app2 : 10.0.14.101 (backend 2)
  lb   : 10.0.14.1   (load balancer / gateway)

Usage:
  # Interactive CLI
  sudo python3 topo_14_recap.py --cli
  
  # Automated test
  sudo python3 topo_14_recap.py --test
  
  # From mn directly
  sudo mn --custom topo_14_recap.py --topo recap14
"""

from __future__ import annotations

import argparse
import os
import sys

# Avoid conflict with local 'mininet/' directory
for p in ["", os.getcwd()]:
    if p in sys.path:
        sys.path.remove(p)

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel


class Recap14Topo(Topo):
    """Topology for W14 review: client, load balancer, 2 backends."""

    def build(self, delay: str = "1ms", bw: int = 100):
        """
        Builds the topology.
        
        Args:
            delay: Link delay (default: 1ms)
            bw: Link bandwidth in Mbps (default: 100)
        """
        # Switches
        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")

        # Hosts with fixed IPs (according to W14 plan)
        cli = self.addHost("cli", ip="10.0.14.11/24")
        lb = self.addHost("lb", ip="10.0.14.1/24")
        app1 = self.addHost("app1", ip="10.0.14.100/24")
        app2 = self.addHost("app2", ip="10.0.14.101/24")

        # Links
        # cli and lb connected to s1
        self.addLink(cli, s1, delay=delay, bw=bw)
        self.addLink(lb, s1, delay=delay, bw=bw)

        # s1 connected to s2
        self.addLink(s1, s2, delay=delay, bw=bw)

        # app1 and app2 connected to s2
        self.addLink(app1, s2, delay=delay, bw=bw)
        self.addLink(app2, s2, delay=delay, bw=bw)


# Dictionary for mn --custom --topo
topos = {"recap14": Recap14Topo}


def run_cli():
    """Starts the topology with interactive CLI."""
    setLogLevel("info")
    
    topo = Recap14Topo()
    net = Mininet(
        topo=topo,
        link=TCLink,
        controller=Controller,
        autoSetMacs=True,
        autoStaticArp=True
    )
    net.addController("c0")
    
    print("\n" + "=" * 60)
    print("Topology W14 - Review")
    print("=" * 60)
    print("""
Hosts (W14 IP plan):
  cli  : 10.0.14.11  (client)
  lb   : 10.0.14.1   (load balancer)
  app1 : 10.0.14.100 (backend 1)
  app2 : 10.0.14.101 (backend 2)

Useful CLI commands:
  cli ping lb
  cli ping app1
  app1 python3 -m http.server 8080 &
  cli curl http://10.0.14.100:8080/
  net
  dump
  exit
""")
    print("=" * 60 + "\n")
    
    net.start()
    CLI(net)
    net.stop()


def run_test():
    """Runs an automated connectivity test."""
    setLogLevel("info")
    
    topo = Recap14Topo()
    net = Mininet(
        topo=topo,
        link=TCLink,
        controller=Controller,
        autoSetMacs=True,
        autoStaticArp=True
    )
    net.addController("c0")
    
    net.start()
    
    print("\n" + "=" * 60)
    print("Automated test W14")
    print("=" * 60 + "\n")
    
    # Test ping all
    print("[test] Ping all pairs...")
    net.pingAll()
    
    # Specific test
    cli = net.get("cli")
    lb = net.get("lb")
    app1 = net.get("app1")
    
    print("\n[test] Testing specific connections...")
    
    # cli -> lb
    result = cli.cmd("ping -c 2 -W 1 10.0.14.1")
    print(f"cli -> lb:\n{result}")
    
    # cli -> app1
    result = cli.cmd("ping -c 2 -W 1 10.0.14.100")
    print(f"cli -> app1:\n{result}")
    
    # Test HTTP (start server on app1)
    print("[test] Starting HTTP server on app1:8080...")
    app1.cmd("python3 -m http.server 8080 &")
    
    import time
    time.sleep(0.5)
    
    print("[test] Testing HTTP from cli...")
    result = cli.cmd("curl -s -o /dev/null -w '%{http_code}' http://10.0.14.100:8080/ 2>/dev/null || echo 'FAILED'")
    print(f"HTTP status: {result}")
    
    # Cleanup
    app1.cmd("pkill -f 'python3 -m http.server' || true")
    
    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60 + "\n")
    
    net.stop()


def main():
    parser = argparse.ArgumentParser(description="Mininet topology W14")
    parser.add_argument("--cli", action="store_true", help="Start interactive CLI")
    parser.add_argument("--test", action="store_true", help="Run automated test")
    args = parser.parse_args()
    
    if args.cli:
        run_cli()
    elif args.test:
        run_test()
    else:
        print("Usage: python3 topo_14_recap.py [--cli | --test]")
        print("  --cli   Start interactive Mininet CLI")
        print("  --test  Run automated connectivity test")


if __name__ == "__main__":
    main()
