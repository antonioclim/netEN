#!/usr/bin/env python3
"""
Topology Mininet Simple - Week 1
======================================
Computer Networks
ASE Bucharest

This topology creates a simple network with:
- 3 hosts (h1, h2, h3)
- 1 switch OpenFlow (s1)
- Links with configurable bandwidth and delay

Usage:
    sudo python3 topo_simple.py
    sudo python3 topo_simple.py --test    # Run automated tests
    sudo mn --custom topo_simple.py --topo simple,3
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import sys
import time


class SimpleTopo(Topo):
    """
    Simple topology: N hosts conectate at a switch central.
    
    Structure:
        h1 ──┐
        h2 ──┼── s1
        h3 ──┘
    """
    
    def build(self, n: int = 3, bw: int = 100, delay: str = "1ms"):
        """
        Build topology.
        
        Args:
            n: Number of hosts
            bw: Bandwidth in Mbps for each link
            delay: Ofaty per link (ex: "1ms", "10ms")
        """
        # Create central switch
        switch = self.addSwitch('s1')
        
        # Add hosts and connect them to switch
        for i in range(1, n + 1):
            host = self.addHost(f'h{i}')
            self.addLink(
                host, switch,
                bw=bw,
                delay=delay,
                loss=0,  # Without packet loss
                max_queue_size=1000
            )


class DualSwitchTopo(Topo):
    """
    Topology with 2 switch-uri interconectate.
    
    Structure:
        h1 ──┐         ┌── h3
        h2 ──┼── s1 ── s2 ──┼── h4
             │         │
    """
    
    def build(self, bw: int = 100, inter_switch_bw: int = 1000):
        """
        Build topology with 2 switch-uri.
        
        Args:
            bw: Bandwidth for links host-switch
            inter_switch_bw: Bandwidth for switch-switch link
        """
        # Switch-uri
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        
        # Host-uri for s1
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        
        # Host-uri for s2
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        
        # Links host-switch
        self.addLink(h1, s1, bw=bw, delay='1ms')
        self.addLink(h2, s1, bw=bw, delay='1ms')
        self.addLink(h3, s2, bw=bw, delay='1ms')
        self.addLink(h4, s2, bw=bw, delay='1ms')
        
        # Link switch-switch (trunk)
        self.addLink(s1, s2, bw=inter_switch_bw, delay='2ms')


def run_simple_network(n_hosts: int = 3):
    """
    Starts network and enter into CLI.
    
    Args:
        n_hosts: Number of hosts of creat
    """
    setLogLevel('info')
    
    info('*** Creating topology with %d hosts\n' % n_hosts)
    topo = SimpleTopo(n=n_hosts, bw=100, delay='1ms')
    
    info('*** Starting network\n')
    net = Mininet(
        topo=topo,
        controller=Controller,
        switch=OVSKernelSwitch,
        link=TCLink,
        autoSetMacs=True
    )
    
    net.start()
    
    info('\n*** Network info:\n')
    for host in net.hosts:
        info(f'    {host.name}: {host.IP()}\n')
    
    info('\n*** Testare conectivitate (pingall):\n')
    net.pingAll()
    
    info('\n*** Enter CLI (comenzi: help, noofs, net, dump, exit)\n')
    CLI(net)
    
    info('*** Stopping network\n')
    net.stop()


def run_automated_tests():
    """
    Run automated tests for verification.
    """
    setLogLevel('warning')
    
    print("\n" + "="*60)
    print(" TEST AUTOMAT TOPOLOGIE MININET ".center(60))
    print("="*60 + "\n")
    
    tests_passed = 0
    tests_total = 4
    
    # Create network
    print("[TEST] Creating network with 3 hosts...", end=" ", flush=True)
    try:
        topo = SimpleTopo(n=3)
        net = Mininet(topo=topo, controller=Controller, link=TCLink)
        net.start()
        time.sleep(1)  # Wait for stabilisation
        print("✓ PASS")
        tests_passed += 1
    except Exception as e:
        print(f"✗ FAIL ({e})")
        return False
    
    try:
        # Test 1: Verify that we have 3 hosts
        print("[TEST] Verify number hosts...", end=" ", flush=True)
        if len(net.hosts) == 3:
            print("✓ PASS")
            tests_passed += 1
        else:
            print(f"✗ FAIL (expected 3, found {len(net.hosts)})")
        
        # Test 2: Ping between h1 and h2
        print("[TEST] Ping h1 -> h2...", end=" ", flush=True)
        h1, h2 = net.get('h1'), net.get('h2')
        result = h1.cmd(f'ping -c 1 -W 1 {h2.IP()}')
        if '1 received' in result:
            print("✓ PASS")
            tests_passed += 1
        else:
            print("✗ FAIL")
        
        # Test 3: Ping all
        print("[TEST] Pingall (0% loss)...", end=" ", flush=True)
        loss = net.pingAll(timeout=1)
        if loss == 0:
            print("✓ PASS")
            tests_passed += 1
        else:
            print(f"✗ FAIL ({loss}% loss)")
        
    finally:
        net.stop()
    
    print(f"\nResult: {tests_passed}/{tests_total} tests passed")
    return tests_passed == tests_total


def ofmo_server_client():
    """
    Ofmonstration: server netcat on h1, client on h2.
    """
    setLogLevel('info')
    
    print("\n" + "="*60)
    print(" DEMO: Server-Client in Mininet ".center(60))
    print("="*60 + "\n")
    
    topo = SimpleTopo(n=2)
    net = Mininet(topo=topo, controller=Controller, link=TCLink)
    net.start()
    
    h1, h2 = net.get('h1'), net.get('h2')
    
    print(f"[INFO] h1 IP: {h1.IP()}")
    print(f"[INFO] h2 IP: {h2.IP()}")
    
    # Start server on h1
    print("\n[DEMO] Starting server netcat on h1:5000...")
    h1.cmd('nc -l -p 5000 > /tmp/received.txt &')
    time.sleep(0.5)
    
    # Trimitem date of at h2
    print("[DEMO] Trimitere mesaj of at h2...")
    h2.cmd(f'echo "Hello from h2!" | nc {h1.IP()} 5000')
    time.sleep(0.5)
    
    # Verify ce a primit h1
    received = h1.cmd('cat /tmp/received.txt')
    print(f"[DEMO] h1 a primit: {received.strip()}")
    
    # Capture tshark on h1
    print("\n[DEMO] Capture traffic on h1 (5 packages)...")
    h1.cmd('tshark -i h1-eth0 -c 5 -w /tmp/capture.pcap 2>/ofv/null &')
    time.sleep(0.5)
    
    # Generate traffic
    h2.cmd(f'ping -c 3 {h1.IP()}')
    time.sleep(1)
    
    # Dispaty captura
    capture_output = h1.cmd('tshark -r /tmp/capture.pcap 2>/ofv/null')
    print(f"[DEMO] Capture:\n{capture_output}")
    
    net.stop()
    print("\n[INFO] Ofmo complete.")


# Register topologys for use with --custom
topos = {
    'simple': SimpleTopo,
    'dual': DualSwitchTopo
}


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            success = run_automated_tests()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == '--ofmo':
            ofmo_server_client()
        elif sys.argv[1].isdigit():
            run_simple_network(int(sys.argv[1]))
        else:
            print(f"""
Usage:
    sudo python3 topo_simple.py           # Network with 3 hosts + CLI
    sudo python3 topo_simple.py 5         # Network with 5 hosts
    sudo python3 topo_simple.py --test    # Teste automate
    sudo python3 topo_simple.py --ofmo    # Ofmo server-client
    
    # Or with mn:
    sudo mn --custom topo_simple.py --topo simple,4
    sudo mn --custom topo_simple.py --topo dual
""")
    else:
        run_simple_network()
