#!/usr/bin/env python3
"""
Mininet Topology for HTTP/Proxy Demo
=====================================
Course: Computer Networks, Week 8

TOPOLOGY (chain: client → proxy → backend):

    ┌─────────┐         ┌─────────────┐         ┌───────────┐
    │   h1    │ ──────→ │     h2      │ ──────→ │    h3     │
    │ Client  │         │ Rev. Proxy  │         │  Backend  │
    └─────────┘         └─────────────┘         └───────────┘
   10.0.0.1              10.0.0.2                10.0.0.3

USAGE:
    sudo python3 topo_http_proxy.py [--delay N] [--loss N]

SCENARIOS:
    1. Client (h1) makes HTTP requests to Proxy (h2)
    2. Proxy (h2) forwards to Backend (h3)
    3. We observe traffic with tcpdump on each host

© Revolvix&Hypotheticalandrei
"""

from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import argparse
import os
import sys
import time


def create_topology(delay_ms=0, loss_pct=0):
    """
    Creates topology for HTTP/Proxy demo.
    
    Args:
        delay_ms: Artificial delay per link (milliseconds)
        loss_pct: Packet loss percentage
    
    Returns:
        Mininet network object
    """
    info("*** Creating HTTP/Proxy topology ***\n")
    
    # Create network with TC links for QoS
    net = Mininet(controller=Controller, switch=OVSSwitch, link=TCLink)
    
    info("*** Adding controller ***\n")
    net.addController('c0')
    
    info("*** Adding switch ***\n")
    sw1 = net.addSwitch('sw1')
    
    info("*** Adding hosts ***\n")
    h1 = net.addHost('h1', ip='10.0.0.1/24')  # Client
    h2 = net.addHost('h2', ip='10.0.0.2/24')  # Proxy
    h3 = net.addHost('h3', ip='10.0.0.3/24')  # Backend
    
    info("*** Configuring links ***\n")
    link_opts = {}
    if delay_ms > 0:
        link_opts['delay'] = f'{delay_ms}ms'
    if loss_pct > 0:
        link_opts['loss'] = loss_pct
    
    # Connect all hosts to switch
    net.addLink(h1, sw1, **link_opts)
    net.addLink(h2, sw1, **link_opts)
    net.addLink(h3, sw1, **link_opts)
    
    return net


def setup_servers(net):
    """
    Configures servers on hosts.
    """
    h2 = net.get('h2')  # Proxy
    h3 = net.get('h3')  # Backend
    
    # Assume files are in current directory
    # In practice, should specify full path
    info("*** Starting Backend Server on h3 (port 9001) ***\n")
    h3.cmd('cd /home/claude/starterkit_s8 && python3 python/demos/demo_http_server.py --port 9001 --docroot www/ > /tmp/backend.log 2>&1 &')
    time.sleep(1)
    
    info("*** Starting Reverse Proxy on h2 (port 8888 → backend 10.0.0.3:9001) ***\n")
    h2.cmd('cd /home/claude/starterkit_s8 && python3 python/demos/demo_reverse_proxy.py --port 8888 --backends 10.0.0.3:9001 > /tmp/proxy.log 2>&1 &')
    time.sleep(1)


def run_demo(net):
    """
    Run interactive demonstration.
    """
    h1 = net.get('h1')  # Client
    
    print("\n" + "="*60)
    print("DEMO: Client → Proxy → Backend")
    print("="*60)
    
    print("\n[1] Check connectivity...")
    net.pingAll()
    
    print("\n[2] Verify services started...")
    print("    Backend (h3:9001):")
    result = h1.cmd('curl -s http://10.0.0.3:9001/ 2>&1 | head -3')
    print(f"        {result}")
    
    print("    Proxy (h2:8888):")
    result = h1.cmd('curl -s http://10.0.0.2:8888/ 2>&1 | head -3')
    print(f"        {result}")
    
    print("\n[3] Send requests through proxy...")
    for i in range(3):
        print(f"\n    Request {i+1}/3:")
        result = h1.cmd('curl -v http://10.0.0.2:8888/ 2>&1 | grep -E "(GET|Host:|HTTP|X-Forwarded)"')
        print(f"        {result}")
        time.sleep(1)
    
    print("\n[4] Check logs...")
    print("    Proxy log:")
    proxy_log = net.get('h2').cmd('tail -5 /tmp/proxy.log 2>/dev/null || echo "No log"')
    print(f"        {proxy_log}")
    
    print("    Backend log:")
    backend_log = net.get('h3').cmd('tail -5 /tmp/backend.log 2>/dev/null || echo "No log"')
    print(f"        {backend_log}")
    
    print("\n[5] Optional: Capture traffic (requires tcpdump)...")
    print("    To capture:")
    print("        h1 sudo tcpdump -i h1-eth0 -c 10 -w /tmp/h1_capture.pcap &")
    print("        h2 sudo tcpdump -i h2-eth0 -c 10 -w /tmp/h2_capture.pcap &")
    print("        h3 sudo tcpdump -i h3-eth0 -c 10 -w /tmp/h3_capture.pcap &")
    print("        h1 curl http://10.0.0.2:8888/")
    
    print("\n[6] Test direct backend access...")
    result = h1.cmd('curl -s http://10.0.0.3:9001/ | head -3')
    print(f"    Direct to backend: {result}")
    
    print("\n[7] Analyse capture...")
    print("    tshark -r /tmp/h2_capture.pcap -Y http")


def interactive_mode(net):
    """
    Interactive mode with CLI.
    """
    print("\n" + "="*60)
    print("INTERACTIVE MODE")
    print("="*60)
    
    print("""
Useful commands:

Test Proxy:
    h1 curl http://10.0.0.2:8888/              - Request through proxy
    h1 curl -v http://10.0.0.2:8888/           - Verbose (headers)
    h1 curl http://10.0.0.2:8888/hello.txt     - Specific file

Test Backend:
    h1 curl http://10.0.0.3:9001/              - Direct to backend

Monitoring:
    h1 tcpdump -i h1-eth0                  - Capture on client
    h2 tcpdump -i h2-eth0                  - Capture on proxy
    h3 tail -f /var/log/http_server.log   - Backend logs (if exists)

Topology:
    pingall                                    - Test connectivity
    net                                        - Display topology
    links                                      - Display links
    
    exit                                       - Exit
""")
    CLI(net)


def main():
    parser = argparse.ArgumentParser(
        description="Mininet Topology for HTTP/Proxy Demo"
    )
    parser.add_argument(
        '--delay', type=int, default=0,
        help='Delay per link in milliseconds (default: 0)'
    )
    parser.add_argument(
        '--loss', type=int, default=0,
        help='Packet loss percentage (default: 0)'
    )
    parser.add_argument(
        '--no-demo', action='store_true',
        help='Skip demo, enter CLI directly'
    )
    
    args = parser.parse_args()
    
    if os.geteuid() != 0:
        print("ERROR: This script must be run as root (sudo)")
        sys.exit(1)
    
    setLogLevel('info')
    
    net = create_topology(delay_ms=args.delay, loss_pct=args.loss)
    
    try:
        info("*** Starting network ***\n")
        net.start()
        
        setup_servers(net)
        
        if not args.no_demo:
            run_demo(net)
        
        interactive_mode(net)
        
    finally:
        info("*** Stopping network ***\n")
        net.stop()


if __name__ == '__main__':
    main()
