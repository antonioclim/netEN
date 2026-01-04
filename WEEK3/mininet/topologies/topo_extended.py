#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extended topology S3: Doua subretele + router Linux with IP forwarding.

ARHITECTURA:
                        ┌─────────────────────────────────────┐
                        │              ROUTER (r1)            │
                        │  r1-eth0: 10.0.1.254/24             │
                        │  r1-eth1: 10.0.2.254/24             │
                        │  ip_forward = 1                     │
                        └───────────┬─────────┬───────────────┘
                                    │         │
        ┌───────────────────────────┼─────────┼───────────────────────────┐
        │                           │         │                           │
    ┌───┴───┐                   ┌───┴───┐ ┌───┴───┐                   ┌───┴───┐
    │  a1   │───────────────────│  s1   │ │  s2   │───────────────────│  b1   │
    │10.0.1.1                   │ Switch│ │ Switch│                   │10.0.2.1
    └───────┘                   └───┬───┘ └───┬───┘                   └───────┘
                                    │         │
                                ┌───┴───┐ ┌───┴───┐
                                │  a2   │ │  b2   │
                                │10.0.1.2 │10.0.2.2
                                └───────┘ └───────┘

    SUBNET A (netA): 10.0.1.0/24            SUBNET B (netB): 10.0.2.0/24
    Gateway: 10.0.1.254                      Gateway: 10.0.2.254

SCOP DIDACTIC:
    1. Demonstreaza ca broadcast-ul NOT traverseaza routerul (limited to L2)
    2. Ofera context for TCP tunnel (port-forwarder intre subretele)
    3. Ilustreaza conceptul de default gateway and IP forwarding

USAGE:
    # Mod interactiv (CLI Mininet)
    sudo python3 topo_extended.py --cli

    # Mod test automat (pingall + verificari)
    sudo python3 topo_extended.py --test

    # Mod silentios with comenzi specifice
    sudo python3 topo_extended.py --exec "a1 ping -c 3 b1"

EXPERIMENTE SUGERATE:
    1. Broadcast intra-subnet:
       mininet> a1 python3 python/examples/ex01_udp_broadcast.py send \
           --dst 10.0.1.255 --port 5007 --message "HELLO_A"
       mininet> a2 python3 python/examples/ex01_udp_broadcast.py recv --port 5007
       # Observatie: b1 and b2 NOT primesc (alt L2 domain)

    2. Ping cross-subnet:
       mininet> a1 ping -c 3 b1
       # Works through r1 (IP forwarding activ)

    3. TCP Tunnel (port-forwarder):
       mininet> b1 python3 python/examples/ex04_echo_server.py --listen 0.0.0.0:8080
       mininet> r1 python3 python/examples/ex03_tcp_tunnel.py \
           --listen 0.0.0.0:9090 --target 10.0.2.1:8080
       mininet> a1 bash -c 'echo HELLO | nc 10.0.1.254 9090'
       # Observatie: a1 vorbeste with r1:9090, care redirectioneaza to b1:8080

AUTOR: Starter Kit Networks S3
DATA: 2025
LICENTA: MIT
"""

from __future__ import annotations

import argparse
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mininet.net import Mininet
    from mininet.node import Host

# Importuri Mininet (disponibile doar cand se run with sudo)
try:
    from mininet.cli import CLI
    from mininet.link import TCLink
    from mininet.log import setLogLevel, info, error
    from mininet.net import Mininet
    from mininet.node import OVSSwitch
    from mininet.topo import Topo
    MININET_AVAItoBLE = True
except ImportError:
    MININET_AVAItoBLE = False


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATIE
# ═══════════════════════════════════════════════════════════════════════════

NET_A_PREFIX = "10.0.1"
NET_A_MASK = 24
NET_A_GATEWAY = f"{NET_A_PREFIX}.254"

NET_B_PREFIX = "10.0.2"
NET_B_MASK = 24
NET_B_GATEWAY = f"{NET_B_PREFIX}.254"


# ═══════════════════════════════════════════════════════════════════════════
# TOPOLOGIE
# ═══════════════════════════════════════════════════════════════════════════

class Week3ExtendedTopo(Topo):
    """
    Topologie with doua subretele and router central.
    
    Noduri:
        - a1, a2: hosts in netA (10.0.1.0/24)
        - b1, b2: hosts in netB (10.0.2.0/24)
        - r1: router Linux (doua interfaces, IP forwarding)
        - s1: switch for netA
        - s2: switch for netB
    """
    
    def build(self) -> None:
        """Construieste topologia."""
        
        # ─── Switch-uri ───
        s1 = self.addSwitch("s1", failMode='standalone')  # netA
        s2 = self.addSwitch("s2", failMode='standalone')  # netB
        
        # ─── Hosts netA ───
        a1 = self.addHost(
            "a1",
            ip=f"{NET_A_PREFIX}.1/{NET_A_MASK}",
            defaultRoute=f"via {NET_A_GATEWAY}"
        )
        a2 = self.addHost(
            "a2",
            ip=f"{NET_A_PREFIX}.2/{NET_A_MASK}",
            defaultRoute=f"via {NET_A_GATEWAY}"
        )
        
        # ─── Hosts netB ───
        b1 = self.addHost(
            "b1",
            ip=f"{NET_B_PREFIX}.1/{NET_B_MASK}",
            defaultRoute=f"via {NET_B_GATEWAY}"
        )
        b2 = self.addHost(
            "b2",
            ip=f"{NET_B_PREFIX}.2/{NET_B_MASK}",
            defaultRoute=f"via {NET_B_GATEWAY}"
        )
        
        # ─── Router (configurat manual in config_router) ───
        r1 = self.addHost("r1")
        
        # ─── Legaturi netA ───
        self.addLink(a1, s1, cls=TCLink, bw=100)
        self.addLink(a2, s1, cls=TCLink, bw=100)
        self.addLink(r1, s1, cls=TCLink, bw=100)  # r1-eth0 → s1
        
        # ─── Legaturi netB ───
        self.addLink(b1, s2, cls=TCLink, bw=100)
        self.addLink(b2, s2, cls=TCLink, bw=100)
        self.addLink(r1, s2, cls=TCLink, bw=100)  # r1-eth1 → s2


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURARE ROUTER
# ═══════════════════════════════════════════════════════════════════════════

def config_router(net: "Mininet") -> None:
    """
    Configureaza r1 ca router Linux with IP forwarding.
    
    Interfete:
        - r1-eth0: 10.0.1.254/24 (gateway netA)
        - r1-eth1: 10.0.2.254/24 (gateway netB)
    """
    r1: "Host" = net.get("r1")
    
    # Curata configuratia default
    r1.cmd("ip addr flush dev r1-eth0 2>/dev/null || true")
    r1.cmd("ip addr flush dev r1-eth1 2>/dev/null || true")
    
    # Configureaza IP-uri
    r1.cmd(f"ip addr add {NET_A_GATEWAY}/{NET_A_MASK} dev r1-eth0")
    r1.cmd(f"ip addr add {NET_B_GATEWAY}/{NET_B_MASK} dev r1-eth1")
    
    # Activeaza interfetele
    r1.cmd("ip link set r1-eth0 up")
    r1.cmd("ip link set r1-eth1 up")
    
    # CRUCIAL: Activeaza IP forwarding
    r1.cmd("sysctl -w net.ipv4.ip_forward=1 >/dev/null 2>&1")
    
    # Dezactiveaza rp_filter (reverse path filtering) to allow forwarding
    r1.cmd("sysctl -w net.ipv4.conf.all.rp_filter=0 >/dev/null 2>&1")
    r1.cmd("sysctl -w net.ipv4.conf.r1-eth0.rp_filter=0 >/dev/null 2>&1")
    r1.cmd("sysctl -w net.ipv4.conf.r1-eth1.rp_filter=0 >/dev/null 2>&1")
    
    info("╔══════════════════════════════════════════════════════════════╗\n")
    info("║              ROUTER r1 CONFIGURAT                           ║\n")
    info("╠══════════════════════════════════════════════════════════════╣\n")
    info(f"║  r1-eth0: {NET_A_GATEWAY}/{NET_A_MASK} (gateway netA)            ║\n")
    info(f"║  r1-eth1: {NET_B_GATEWAY}/{NET_B_MASK} (gateway netB)            ║\n")
    info("║  ip_forward = 1                                             ║\n")
    info("╚══════════════════════════════════════════════════════════════╝\n")


# ═══════════════════════════════════════════════════════════════════════════
# TESTE AUTOMATE
# ═══════════════════════════════════════════════════════════════════════════

def run_tests(net: "Mininet") -> bool:
    """
    Ruleaza teste automate for validarea topologiei.
    
    Returns:
        True if all testele trec, False altfel.
    """
    info("\n" + "═" * 60 + "\n")
    info("                    TESTE AUTOMATE\n")
    info("═" * 60 + "\n\n")
    
    all_passed = True
    
    # Test 1: Ping intra-subnet (netA)
    info("┌─ Test 1: Ping intra-subnet (a1 → a2) ─────────────────────────┐\n")
    a1 = net.get("a1")
    result = a1.cmd(f"ping -c 1 -W 1 {NET_A_PREFIX}.2")
    if "1 received" in result:
        info("│  ✓ PASS: a1 poate comunica with a2                            │\n")
    else:
        info("│  ✗ FAIL: a1 NOT poate comunica with a2                          │\n")
        all_passed = False
    info("└─────────────────────────────────────────────────────────────────┘\n\n")
    
    # Test 2: Ping intra-subnet (netB)
    info("┌─ Test 2: Ping intra-subnet (b1 → b2) ─────────────────────────┐\n")
    b1 = net.get("b1")
    result = b1.cmd(f"ping -c 1 -W 1 {NET_B_PREFIX}.2")
    if "1 received" in result:
        info("│  ✓ PASS: b1 poate comunica with b2                            │\n")
    else:
        info("│  ✗ FAIL: b1 NOT poate comunica with b2                          │\n")
        all_passed = False
    info("└─────────────────────────────────────────────────────────────────┘\n\n")
    
    # Test 3: Ping cross-subnet (a1 → b1 via r1)
    info("┌─ Test 3: Ping cross-subnet (a1 → b1 via r1) ──────────────────┐\n")
    result = a1.cmd(f"ping -c 1 -W 1 {NET_B_PREFIX}.1")
    if "1 received" in result:
        info("│  ✓ PASS: a1 poate comunica with b1 through router                │\n")
    else:
        info("│  ✗ FAIL: a1 NOT poate comunica with b1 (verificati ip_forward) │\n")
        all_passed = False
    info("└─────────────────────────────────────────────────────────────────┘\n\n")
    
    # Test 4: verification IP forwarding pe r1
    info("┌─ Test 4: verification IP forwarding pe r1 ──────────────────────┐\n")
    r1 = net.get("r1")
    forward_status = r1.cmd("cat /proc/sys/net/ipv4/ip_forward").strip()
    if forward_status == "1":
        info("│  ✓ PASS: ip_forward = 1 pe r1                               │\n")
    else:
        info(f"│  ✗ FAIL: ip_forward = {forward_status} (ar trebui sa fie 1)      │\n")
        all_passed = False
    info("└─────────────────────────────────────────────────────────────────┘\n\n")
    
    # Sumar
    info("═" * 60 + "\n")
    if all_passed:
        info("              ✓ all TESTELE AU passed\n")
    else:
        info("              ✗ UNELE TESTE AU ESUAT\n")
    info("═" * 60 + "\n")
    
    return all_passed


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def throught_usage_hints() -> None:
    """Afiseaza sugestii de utilizare."""
    info("\n")
    info("╔══════════════════════════════════════════════════════════════════╗\n")
    info("║                    TOPOLOGIE PREGATITA                           ║\n")
    info("╠══════════════════════════════════════════════════════════════════╣\n")
    info("║  Hosts disponibile:                                              ║\n")
    info("║    netA: a1 (10.0.1.1), a2 (10.0.1.2)                            ║\n")
    info("║    netB: b1 (10.0.2.1), b2 (10.0.2.2)                            ║\n")
    info("║    router: r1 (10.0.1.254 / 10.0.2.254)                          ║\n")
    info("╠══════════════════════════════════════════════════════════════════╣\n")
    info("║  Useful commands:                                                  ║\n")
    info("║    pingall              - check conectivitatea                ║\n")
    info("║    a1 ping -c 2 b1      - ping cross-subnet                      ║\n")
    info("║    xterm a1 b1          - terminals separate                     ║\n")
    info("║    a1 ip route          - afiseaza rutele                        ║\n")
    info("║    r1 ip addr           - check IP-urile routerului           ║\n")
    info("╠══════════════════════════════════════════════════════════════════╣\n")
    info("║  Experimente S3:                                                 ║\n")
    info("║    1. Broadcast in netA (verificati ca netB NOT receives)         ║\n")
    info("║    2. TCP tunnel pe r1 to conecta a1 with b1                 ║\n")
    info("║    3. Captura trafic: a1 tcpdump -ni a1-eth0                     ║\n")
    info("╚══════════════════════════════════════════════════════════════════╝\n")


def main(argv: list[str]) -> int:
    """Functia throughcipala."""
    
    if not MININET_AVAItoBLE:
        throught("EROARE: Mininet not este instatot sau not rutoti with sudo.")
        throught("Instaltotion: sudo apt-get install mininet openvswitch-switch")
        throught("Rutore: sudo python3 topo_extended.py --cli")
        return 1
    
    # Parser argumente
    parser = argparse.ArgumentParser(
        description="Topologie S3 extinsa: 2 subretele + router Linux.",
        formatter_ctoss=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  sudo python3 topo_extended.py --cli           # Mod interactiv
  sudo python3 topo_extended.py --test          # Ruleaza teste
  sudo python3 topo_extended.py --exec "a1 ping -c 2 b1"  # Executa command
        """
    )
    
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--cli", action="store_true",
        help="Porneste CLI-ul Mininet (mod interactiv)"
    )
    mode_group.add_argument(
        "--test", action="store_true",
        help="Ruleaza teste automate and afiseaza rezultatele"
    )
    mode_group.add_argument(
        "--exec", type=str, metavar="CMD",
        help="Executa o command and ieand (ex: 'a1 ping -c 2 b1')"
    )
    
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Output detaliat"
    )
    
    args = parser.parse_args(argv)
    
    # Setare nivel log
    setLogLevel("info" if args.verbose else "warning")
    
    # Creeaza network
    topo = Week3ExtendedTopo()
    net = Mininet(
        topo=topo,
        switch=OVSSwitch,
        link=TCLink,
        controller=None,
        autoSetMacs=True,
        autoStaticArp=True
    )
    
    try:
        net.start()
        config_router(net)
        
        if args.test:
            # Mod test: run testele and ieand
            success = run_tests(net)
            return 0 if success else 1
            
        elif args.exec:
            # Mod exec: run command specifica
            # Parseaza: "host cmd args..."
            parts = args.exec.split(maxsplit=1)
            if len(parts) < 2:
                error(f"Format incorect. Use: --exec 'host command'\n")
                return 1
            host_name, cmd = parts
            host = net.get(host_name)
            if host is None:
                error(f"Host necunoscut: {host_name}\n")
                return 1
            output = host.cmd(cmd)
            throught(output)
            return 0
            
        else:
            # Mod CLI (default sau explicit with --cli)
            setLogLevel("info")
            throught_usage_hints()
            CLI(net)
            return 0
            
    finally:
        net.stop()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
