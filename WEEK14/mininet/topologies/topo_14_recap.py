#!/usr/bin/env python3
"""topo_14_recap.py — Mininet topology for Week 14 (integrated review).

This topology supports an end-of-semester integrated recap:
  - a client that generates traffic
  - two backend HTTP servers
  - a simple load balancer / reverse proxy

Design goals:
  - Reproducible IP plan for consistent captures and logs
  - No external OpenFlow controller dependency
  - Works on stock Ubuntu/Debian with Mininet and Open vSwitch

Topology:

    cli ─── s1 ─── s2 ─── app1
             │       └─── app2
             └─── lb

Fixed IP plan (/24):
  - cli  : 10.0.14.11   (client)
  - lb   : 10.0.14.1    (load balancer)
  - app1 : 10.0.14.100  (backend 1)
  - app2 : 10.0.14.101  (backend 2)

Notes:
  - Switches run in OVS "standalone" mode (learning switch behaviour)
  - No controller is started, so the demo does not depend on any 'controller'
    binary or an SDN framework.

Usage:
  # Interactive CLI
  sudo python3 mininet/topologies/topo_14_recap.py --cli

  # Automated connectivity + HTTP sanity check
  sudo python3 mininet/topologies/topo_14_recap.py --test

  # From mn directly
  sudo mn --custom mininet/topologies/topo_14_recap.py --topo recap14
"""

from __future__ import annotations

import argparse
import os
import sys
import time

# Avoid conflicts with the local 'mininet/' directory (namespace package edge case)
for p in ["", os.getcwd()]:
    if p in sys.path:
        sys.path.remove(p)

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel


class Recap14Topo(Topo):
    """Topology for the Week 14 recap: client, load balancer and 2 backends."""

    def build(self, delay: str = "1ms", bw: int = 0):
        """Builds the topology.

        Args:
            delay: Link delay (e.g. '1ms')
            bw: Optional bandwidth limit in Mbps. Use 0 to disable shaping.
        """

        # Switches in standalone mode (no external controller required)
        s1 = self.addSwitch("s1", failMode="standalone")
        s2 = self.addSwitch("s2", failMode="standalone")

        # Hosts with fixed IPs
        cli = self.addHost("cli", ip="10.0.14.11/24")
        lb = self.addHost("lb", ip="10.0.14.1/24")
        app1 = self.addHost("app1", ip="10.0.14.100/24")
        app2 = self.addHost("app2", ip="10.0.14.101/24")

        # Link parameters
        link_opts: dict = {"delay": delay}
        if bw and bw > 0:
            # Bandwidth shaping can trigger kernel HTB warnings for large rates.
            # It is optional and disabled by default.
            link_opts.update({"bw": bw, "use_htb": True})

        # Links
        self.addLink(cli, s1, cls=TCLink, **link_opts)
        self.addLink(lb, s1, cls=TCLink, **link_opts)
        self.addLink(s1, s2, cls=TCLink, **link_opts)
        self.addLink(app1, s2, cls=TCLink, **link_opts)
        self.addLink(app2, s2, cls=TCLink, **link_opts)


# Dictionary for mn --custom --topo
topos = {"recap14": Recap14Topo}


def _banner(title: str) -> None:
    print("\n" + "=" * 64)
    print(title)
    print("=" * 64)


def run_cli(delay: str = "1ms", bw: int = 0) -> None:
    """Starts the topology with an interactive Mininet CLI."""

    setLogLevel("info")

    topo = Recap14Topo(delay=delay, bw=bw)
    net = Mininet(
        topo=topo,
        link=TCLink,
        switch=OVSSwitch,
        controller=None,
        autoSetMacs=True,
        autoStaticArp=True,
    )

    _banner("Week 14 topology started (standalone OVS, no controller)")
    print(
        """Hosts (fixed IP plan):
  cli  : 10.0.14.11   (client)
  lb   : 10.0.14.1    (load balancer)
  app1 : 10.0.14.100  (backend 1)
  app2 : 10.0.14.101  (backend 2)

Useful Mininet CLI commands:
  net
  dump
  cli ping -c 2 10.0.14.1
  cli ping -c 2 10.0.14.100
  app1 python3 -m http.server 8080 &
  cli curl -v http://10.0.14.100:8080/
  exit
"""
    )

    net.start()
    CLI(net)
    net.stop()


def run_test(delay: str = "1ms", bw: int = 0) -> int:
    """Runs an automated sanity test (ping + simple HTTP)."""

    setLogLevel("warning")

    topo = Recap14Topo(delay=delay, bw=bw)
    net = Mininet(
        topo=topo,
        link=TCLink,
        switch=OVSSwitch,
        controller=None,
        autoSetMacs=True,
        autoStaticArp=True,
    )

    net.start()

    _banner("Week 14 automated topology test")

    print("[test] Ping all hosts...")
    net.pingAll()

    cli = net.get("cli")
    app1 = net.get("app1")

    print("\n[test] Starting a minimal HTTP server on app1:8080...")
    app1.cmd("python3 -m http.server 8080 >/dev/null 2>&1 &")
    time.sleep(0.5)

    print("[test] Fetching / from cli (expect HTTP 200)...")
    status = cli.cmd(
        "curl -s -o /dev/null -w '%{http_code}' http://10.0.14.100:8080/ 2>/dev/null || echo 000"
    ).strip()
    print(f"[test] HTTP status: {status}")

    app1.cmd("pkill -f 'python3 -m http.server 8080' >/dev/null 2>&1 || true")

    net.stop()

    ok = status == "200"
    _banner("Test completed")
    print(f"Result: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Week 14 Mininet topology")
    parser.add_argument("--cli", action="store_true", help="Start interactive Mininet CLI")
    parser.add_argument("--test", action="store_true", help="Run automated ping + HTTP test")
    parser.add_argument("--delay", default="1ms", help="Link delay, e.g. '1ms'")
    parser.add_argument(
        "--bw",
        type=int,
        default=0,
        help="Optional bandwidth limit in Mbps (0 disables shaping)",
    )
    args = parser.parse_args()

    if args.cli:
        run_cli(delay=args.delay, bw=args.bw)
        return 0
    if args.test:
        return run_test(delay=args.delay, bw=args.bw)

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
