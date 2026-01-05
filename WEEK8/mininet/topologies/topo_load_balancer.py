#!/usr/bin/env python3
"""
Mininet Topology for Load Balancing Demo
=========================================
Course: Computer Networks, Week 8

TOPOLOGY (star with multiple backends):

                         +----------+
                         |   sw1    |
                         +----+-----+
                              |
    +-------+-------+---------+--------+-------+-------+
    |       |       |         |        |       |       |
   h1      h2      h3        h4       h5      h6      h7
 client  proxy  backend1  backend2  backend3  ...    ...
10.0.0.1 10.0.0.2 10.0.0.3  10.0.0.4  10.0.0.5

USAGE:
    sudo python3 topo_load_balancer.py [--backends N] [--delay N] [--loss N]

SCENARIOS:
    1. Proxy distributes requests among multiple backends (Round Robin)
    2. We observe uniform distribution
    3. We simulate backend failure and observe failover

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


def create_topology(num_backends=3, delay_ms=0, loss_pct=0):
    """
    Creates topology for Load Balancing demo.
    
    Args:
        num_backends: Number of backends (default: 3)
        delay_ms: Artificial delay per link (milliseconds)
        loss_pct: Packet loss percentage
    
    Returns:
        Tuple (net, backends_list)
    """
    info(f"*** Creating Load Balancing topology with {num_backends} backends ***\n")
    
    net = Mininet(controller=Controller, switch=OVSSwitch, link=TCLink)
    
    info("*** Adding controller ***\n")
    net.addController('c0')
    
    info("*** Adding switch ***\n")
    sw1 = net.addSwitch('sw1')
    
    link_opts = {}
    if delay_ms > 0:
        link_opts['delay'] = f'{delay_ms}ms'
    if loss_pct > 0:
        link_opts['loss'] = loss_pct
    
    info("*** Adding hosts ***\n")
    
    # h1: Client
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    net.addLink(h1, sw1, **link_opts)
    
    # h2: Reverse Proxy / Load Balancer
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    net.addLink(h2, sw1, **link_opts)
    
    # Backends: h3, h4, h5, ...
    backends = []
    for i in range(num_backends):
        host_num = i + 3
        ip = f'10.0.0.{host_num}/24'
        host = net.addHost(f'h{host_num}', ip=ip)
        net.addLink(host, sw1, **link_opts)
        backends.append({
            'host': f'h{host_num}',
            'ip': f'10.0.0.{host_num}',
            'port': 8081 + i
        })
        info(f"    Backend {i+1}: h{host_num} (10.0.0.{host_num}:{8081+i})\n")
    
    return net, backends


def setup_servers(net, backends):
    """
    Configures servers on hosts.
    """
    h2 = net.get('h2')  # Proxy
    
    # Start each backend
    info("*** Starting Backend Servers ***\n")
    for backend in backends:
        host = net.get(backend['host'])
        port = backend['port']
        
        # Create a unique index.html file for each backend
        host.cmd(f'mkdir -p /tmp/www_{backend["host"]}')
        host.cmd(f'echo "<h1>Response from {backend["host"]} (port {port})</h1>" > /tmp/www_{backend["host"]}/index.html')
        
        # Start the server
        host.cmd(f'cd /home/claude/starterkit_s8 && python3 python/demos/demo_http_server.py --port {port} --docroot /tmp/www_{backend["host"]}/ &')
        info(f"    {backend['host']} started on port {port}\n")
        time.sleep(0.5)
    
    # Build backend list for proxy
    backends_str = ','.join([f"{b['ip']}:{b['port']}" for b in backends])
    
    info("*** Starting Load Balancer on h2 (port 8080) ***\n")
    h2.cmd(f'cd /home/claude/starterkit_s8 && python3 python/demos/demo_reverse_proxy.py --port 8080 --backends {backends_str} &')
    info(f"    Backends: {backends_str}\n")
    time.sleep(1)


def run_load_balance_demo(net, backends, num_requests=10):
    """
    Load balancing demonstration.
    """
    h1 = net.get('h1')
    
    print("\n" + "="*60)
    print("DEMO: Load Balancing - Round Robin")
    print("="*60)
    
    print(f"\n[1] Sending {num_requests} requests to Load Balancer...")
    print("    Observing distribution among backends:\n")
    
    responses = {}
    for i in range(num_requests):
        result = h1.cmd('curl -s http://10.0.0.2:8080/')
        # Extract backend name from response
        if 'from h' in result:
            # Simplified: count responses
            backend_id = result.split('from ')[1].split(' ')[0] if 'from ' in result else 'unknown'
            responses[backend_id] = responses.get(backend_id, 0) + 1
        print(f"    Request {i+1}: {result.strip()[:50]}...")
        time.sleep(0.3)
    
    print("\n" + "-"*40)
    print("DISTRIBUTION STATISTICS:")
    print("-"*40)
    for backend_id, count in sorted(responses.items()):
        pct = (count / num_requests) * 100
        bar = "█" * int(pct / 5)
        print(f"    {backend_id}: {count} requests ({pct:.1f}%) {bar}")
    
    # Test failover
    print("\n" + "="*60)
    print("DEMO: Failover - Simulating backend failure")
    print("="*60)
    
    if len(backends) > 1:
        failed_backend = backends[0]
        host = net.get(failed_backend['host'])
        
        print(f"\n[2] Stopping backend {failed_backend['host']}...")
        host.cmd('pkill -f demo_http_server')
        time.sleep(1)
        
        print(f"[3] Sending 5 requests (without {failed_backend['host']})...")
        for i in range(5):
            result = h1.cmd('curl -s --connect-timeout 2 http://10.0.0.2:8080/')
            print(f"    Request {i+1}: {result.strip()[:50]}...")
            time.sleep(0.3)
        
        print(f"\n[4] Restarting {failed_backend['host']}...")
        host.cmd(f'cd /home/claude/starterkit_s8 && python3 python/demos/demo_http_server.py --port {failed_backend["port"]} --docroot /tmp/www_{failed_backend["host"]}/ &')
        time.sleep(1)


def run_latency_demo(net, delay_ms):
    """
    Demo for observing latency.
    """
    if delay_ms <= 0:
        return
    
    h1 = net.get('h1')
    
    print("\n" + "="*60)
    print(f"DEMO: Latency Effect ({delay_ms}ms delay per hop)")
    print("="*60)
    
    print("\n[1] Measuring RTT with ping...")
    print(h1.cmd('ping -c 5 10.0.0.2'))
    
    print("[2] Measuring HTTP request time...")
    for i in range(3):
        start = time.time()
        h1.cmd('curl -s http://10.0.0.2:8080/ > /dev/null')
        elapsed = (time.time() - start) * 1000
        print(f"    Request {i+1}: {elapsed:.1f}ms")


def interactive_mode(net, backends):
    """
    Interactive mode.
    """
    print("\n" + "="*60)
    print("INTERACTIVE MODE")
    print("="*60)
    
    backends_info = "\n".join([f"    h1 curl http://{b['ip']}:{b['port']}/    - Direct to {b['host']}" for b in backends])
    
    print(f"""
Useful commands:

Load Balancer:
    h1 curl http://10.0.0.2:8080/              - Request through LB
    h1 bash -c 'for i in {{1..20}}; do curl -s http://10.0.0.2:8080/; done'  - 20 requests

Direct to backends:
{backends_info}

Monitoring:
    h2 tcpdump -i h2-eth0 -c 20               - Capture on LB
    h3 pkill -f demo_http_server              - Stop backend h3
    
Topology:
    pingall                                    - Check connectivity
    net                                        - Display topology
    links                                      - Display links
    
    exit                                       - Exit
""")
    CLI(net)


def main():
    parser = argparse.ArgumentParser(
        description="Mininet Topology for Load Balancing"
    )
    parser.add_argument(
        '--backends', type=int, default=3,
        help='Number of backends (default: 3)'
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
        '--requests', type=int, default=10,
        help='Number of requests in demo (default: 10)'
    )
    parser.add_argument(
        '--no-demo', action='store_true',
        help='Skip demo, enter CLI directly'
    )
    
    args = parser.parse_args()
    
    if os.geteuid() != 0:
        print("ERROR: This script must be run as root (sudo)")
        sys.exit(1)
    
    if args.backends < 1 or args.backends > 10:
        print("ERROR: Number of backends must be between 1 and 10")
        sys.exit(1)
    
    setLogLevel('info')
    
    net, backends = create_topology(
        num_backends=args.backends,
        delay_ms=args.delay,
        loss_pct=args.loss
    )
    
    try:
        info("*** Starting network ***\n")
        net.start()
        
        setup_servers(net, backends)
        
        if not args.no_demo:
            run_load_balance_demo(net, backends, args.requests)
            run_latency_demo(net, args.delay)
        
        interactive_mode(net, backends)
        
    finally:
        info("*** Stopping network ***\n")
        net.stop()


if __name__ == '__main__':
    main()
