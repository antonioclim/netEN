#!/usr/bin/env python3
"""Week 2 base topology: one switch and three hosts.

h1 = server (TCP/UDP)
h2 and h3 = clients

running:
  sudo python3 topo_2_base.py --cli
  sudo python3 topo_2_base.py --test

In --test mode, the script:
- starts un server TCP on h1, sends messages from h2/h3 (including concurrently);
- starts un server UDP on h1, sends messages from h2;
- creates a tcpdump capture on h2 for TCP traffic.

Note: Mininet requires root privileges.
"""

from __future__ import annotations

import argparse
import os
import signal
import time
from pathlib import Path

from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.net import Mininet
from mininet.node import OVSController
from mininet.topo import Topo


class S2BaseTopo(Topo):
    def build(self, bw: float = 10.0, delay: str = "5ms", loss: float = 0.0) -> None:
        s1 = self.addSwitch("s1")
        h1 = self.addHost("h1", ip="10.0.0.1/24")
        h2 = self.addHost("h2", ip="10.0.0.2/24")
        h3 = self.addHost("h3", ip="10.0.0.3/24")

        for h in (h1, h2, h3):
            self.addLink(h, s1, cls=TCLink, bw=bw, delay=delay, loss=loss)


def run_demo(net: Mininet) -> None:
    info("*** Running demo (TCP + UDP)\n")
    root = Path(__file__).resolve().parents[2]  # starterkit root
    ex_tcp = str(root / "python/apps/ex_2_01.py")
    ex_udp = str(root / "python/apps/ex_2_02.py")
    cap_dir = root / "captures"
    cap_dir.mkdir(exist_ok=True)

    h1, h2, h3 = net.get("h1", "h2", "h3")

    info("*** Starting TCP server on h1 (threaded)\n")
    tcp_srv = h1.popen(["python3", "-u", ex_tcp, "server", "--bind", "10.0.2.100", "--port", "9090", "--mode", "threaded"])
    time.sleep(0.5)

    info("*** Capturing TCP traffic on h2 (tcpdump)\n")
    cap_path = cap_dir / "tcp_9999_h2.pcap"
    tcpdump = h2.popen(["tcpdump", "-i", "h2-eth0", "-w", str(cap_path), "tcp", "port", "9090"],
                       stdout=open(os.devnull, "wb"), stderr=open(os.devnull, "wb"))
    time.sleep(0.3)

    info("*** Sending concurrent TCP clients from h2 and h3\n")
    c2 = h2.popen(["python3", ex_tcp, "client", "--host", "10.0.2.100", "--port", "9090", "--message", "hello from h2"])
    c3 = h3.popen(["python3", ex_tcp, "client", "--host", "10.0.2.100", "--port", "9090", "--message", "hello from h3"])
    c2.wait(); c3.wait()

    info("*** Stopping tcpdump\n")
    tcpdump.send_signal(signal.SIGINT)
    tcpdump.wait(timeout=2)

    info(f"*** Capture saved: {cap_path}\n")

    info("*** Starting UDP server on h1\n")
    udp_srv = h1.popen(["python3", "-u", ex_udp, "server", "--bind", "10.0.2.100", "--port", "9091"])
    time.sleep(0.5)

    info("*** UDP client (once) from h2\n")
    h2.cmd(["python3", ex_udp, "client", "--host", "10.0.2.100", "--port", "9091", "--once", "ping"])

    info("*** Cleaning demo processes\n")
    for p in (tcp_srv, udp_srv):
        try:
            p.send_signal(signal.SIGINT)
            p.wait(timeout=2)
        except Exception:
            p.terminate()


def main() -> None:
    setLogLevel("info")
    ap = argparse.ArgumentParser()
    ap.add_argument("--bw", type=float, default=10.0)
    ap.add_argument("--delay", default="5ms")
    ap.add_argument("--loss", type=float, default=0.0)
    ap.add_argument("--cli", action="store_true", help="start interactive CLI")
    ap.add_argument("--test", action="store_true", help="run a short demo and exit")
    args = ap.parse_args()

    topo = S2BaseTopo(bw=args.bw, delay=args.delay, loss=args.loss)
    net = Mininet(topo=topo, controller=OVSController, link=TCLink, autoSetMacs=True, autoStaticArp=False)
    net.start()
    try:
        if args.test:
            run_demo(net)
        if args.cli or (not args.test):
            CLI(net)
    finally:
        net.stop()


if __name__ == "__main__":
    main()
