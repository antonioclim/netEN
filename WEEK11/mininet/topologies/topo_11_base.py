#!/usr/bin/env python3
"""
Mininet Topology – Week 11 (base)
h1 (client) -> lb (load balancer) -> b1,b2,b3 (backends) through switch s1.

Usage:
  sudo python3 topo_11_base.py --test
  sudo python3 topo_11_base.py --cli
"""
from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.net import Mininet
from mininet.node import OVSController
from mininet.topo import Topo


class LBTopo(Topo):
    """
    Topology for load balancing: client -> lb -> b1,b2,b3
    
    Standard IP plan WEEK 11 (10.0.11.0/24):
      - Gateway/LB:  10.0.11.1
      - Client h1:   10.0.11.11
      - Backend b1:  10.0.11.101
      - Backend b2:  10.0.11.102
      - Backend b3:  10.0.11.103
    """
    def build(self, delay="0ms", loss=0, bw=None):
        s1 = self.addSwitch("s1")

        # Hosts - Standard IP plan WEEK 11
        h1 = self.addHost("h1", ip="10.0.11.11/24")
        lb = self.addHost("lb", ip="10.0.11.1/24")
        b1 = self.addHost("b1", ip="10.0.11.101/24")
        b2 = self.addHost("b2", ip="10.0.11.102/24")
        b3 = self.addHost("b3", ip="10.0.11.103/24")

        linkopts = dict()
        if bw is not None:
            linkopts["bw"] = bw
        if delay:
            linkopts["delay"] = delay
        if loss:
            linkopts["loss"] = loss

        for h in (h1, lb, b1, b2, b3):
            self.addLink(h, s1, cls=TCLink, **linkopts)


def _cmd_bg(host, cmd, pidfile):
    # run in background and save PID
    host.cmd(f"sh -lc '{cmd} > /tmp/{pidfile}.log 2>&1 & echo $! > /tmp/{pidfile}.pid'")
    time.sleep(0.2)


def _kill_bg(host, pidfile):
    pid_path = f"/tmp/{pidfile}.pid"
    pid = host.cmd(f"cat {pid_path} 2>/dev/null || true").strip()
    if pid:
        host.cmd(f"kill {pid} 2>/dev/null || true")
        host.cmd(f"rm -f {pid_path} 2>/dev/null || true")


def run_test(net, kit_root: Path):
    h1, lb, b1, b2, b3 = net.get("h1", "lb", "b1", "b2", "b3")

    info("\n[TEST] Starting backends...\n")
    backend_py = kit_root / "python" / "exercises" / "ex_11_01_backend.py"
    _cmd_bg(b1, f"python3 {backend_py} --id 1 --port 8000", "b1_backend")
    _cmd_bg(b2, f"python3 {backend_py} --id 2 --port 8000", "b2_backend")
    _cmd_bg(b3, f"python3 {backend_py} --id 3 --port 8000", "b3_backend")

    info("[TEST] Starting load balancer...\n")
    lb_py = kit_root / "python" / "exercises" / "ex_11_02_loadbalancer.py"
    backends = "10.0.11.101:8000,10.0.11.102:8000,10.0.11.103:8000"
    _cmd_bg(lb, f"python3 {lb_py} --listen 0.0.0.0:8080 --backends {backends} --algo rr --fail-timeout 5", "lb_proxy")

    time.sleep(1.0)

    info("[TEST] Client requests (curl) – expected distribution 1-2-3...\n")
    out = h1.cmd("sh -lc 'for i in 1 2 3 4 5 6; do curl -s http://10.0.11.1:8080/; done'")
    info(out + "\n")

    info("[TEST] Simulating failure: stopping b2 and repeating (passive failover)...\n")
    _kill_bg(b2, "b2_backend")
    time.sleep(0.5)
    out2 = h1.cmd("sh -lc 'for i in 1 2 3 4 5 6; do curl -s http://10.0.11.1:8080/; done'")
    info(out2 + "\n")

    info("[TEST] Cleanup processes...\n")
    _kill_bg(lb, "lb_proxy")
    _kill_bg(b1, "b1_backend")
    _kill_bg(b3, "b3_backend")
    # b2 already stopped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--delay", default="0ms")
    ap.add_argument("--loss", type=int, default=0)
    ap.add_argument("--bw", type=float, default=None)
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--cli", action="store_true")
    args = ap.parse_args()

    kit_root = Path(__file__).resolve().parents[2]

    topo = LBTopo(delay=args.delay, loss=args.loss, bw=args.bw)
    net = Mininet(topo=topo, controller=OVSController, link=TCLink, autoSetMacs=True, autoStaticArp=True)
    net.start()

    try:
        if args.test:
            run_test(net, kit_root)
        if args.cli or (not args.test):
            info("\n[INFO] Entering Mininet CLI. Exit with 'exit'.\n")
            CLI(net)
    finally:
        net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    main()
