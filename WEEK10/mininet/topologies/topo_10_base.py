#!/usr/bin/env python3
"""
Base Mininet topology for Week 10.

Creates a small network with a switch and three hosts, used to validate connectivity and service reachability.
"""

from __future__ import annotations

import sys
import argparse
import time

try:
    from mininet.topo import Topo
    from mininet.net import Mininet
    from mininet.node import OVSKernelSwitch, Controller
    from mininet.cli import CLI
    from mininet.log import setLogLevel, info, error
    from mininet.link import TCLink
except ImportError:
    print("ERROR: Mininet not installed.")
    print("Install with: sudo apt install mininet openvswitch-switch")
    print("")
    print("Alternativ, acest script poate fi rulat in VM sau container cu Mininet.")
    sys.exit(1)


class BaseTopo(Topo):
    """
    Topologie de baza with 3 host-uri and un switch.
    
    Aceasta clasa defineste structura retelei and poate fi
    extinsa for scenarii mai complexe.
    
    Attributes:
        n_hosts: Numarul de host-uri (default 3)
        bw: Bandwidth in Mbps for link-uri (default 100)
        delay: Latenta for link-uri (default '5ms')
    """
    
    def __init__(self, n_hosts: int = 3, bw: int = 100, delay: str = '5ms'):
        """
        Initializeaza topologia.
        
        Args:
            n_hosts: Numarul de host-uri de creat
            bw: Bandwidth in Mbps
            delay: Latenta (e.g., '5ms', '10ms')
        """
        self.n_hosts = n_hosts
        self.bw = bw
        self.delay = delay
        
        super().__init__()
    
    def build(self):
        """
        Construieste topologia.
        
        Aceasta metoda este apelata automat de Mininet
        for a crea nodurile and link-urile.
        """
        info('*** Builfromg base topology\n')
        
        # Cream switch-ul central
        s1 = self.addSwitch('s1', cls=OVSKernelSwitch)
        info(f'  Added switch: s1\n')
        
        # Cream host-urile
        for i in range(1, self.n_hosts + 1):
            host_name = f'h{i}'
            host_ip = f'10.0.0.{i}/24'
            
            host = self.addHost(
                host_name,
                ip=host_ip,
                defaultRoute='via 10.0.0.254'
            )
            
            # Link with parameters de performanta
            self.addLink(
                host, s1,
                cls=TCLink,
                bw=self.bw,
                delay=self.delay
            )
            
            info(f'  Added host: {host_name} ({host_ip})\n')
        
        info('*** Topology built successfully\n')


def run_connectivity_test(net: Mininet) -> bool:
    """
    Testeaza conectivitatea intre all host-urile.
    
    Args:
        net: Instanta Mininet activa
    
    Returns:
        True if all ping-urile reusesc
    """
    info('\n*** Running connectivity tests\n')
    
    hosts = net.hosts
    success = True
    
    for i, src in enamerate(hosts):
        for dst in hosts[i+1:]:
            info(f'  {src.name} -> {dst.name}: ')
            result = src.cmd(f'ping -c 1 -W 1 {dst.IP()}')
            
            if '1 received' in result:
                info('OK\n')
            else:
                info('FAILED\n')
                success = False
    
    return success


def run_http_server_test(net: Mininet) -> bool:
    """
    Testeaza server HTTP pe h1 and client pe h2.
    
    Args:
        net: Instanta Mininet activa
    
    Returns:
        True if testul reuseste
    """
    info('\n*** Running HTTP server test\n')
    
    h1 = net.get('h1')
    h2 = net.get('h2')
    
    # Pornim server HTTP pe h1
    info('  Starting HTTP server on h1:8000...\n')
    h1.cmd('echo "Hello from h1" > /tmp/index.html')
    h1.cmd('cd /tmp && python3 -m http.server 8000 &')
    time.sleep(1)
    
    # Testam from h2
    info('  Testing from h2...\n')
    result = h2.cmd(f'curl -s http://{h1.IP()}:8000/')
    
    # Cleanup
    h1.cmd('kill %python3 2>/dev/null')
    
    if 'Hello from h1' in result:
        info('  HTTP test: OK\n')
        return True
    else:
        info(f'  HTTP test: FAILED (got: {result[:50]})\n')
        return False


def run_bandwidth_test(net: Mininet) -> dict:
    """
    Masoara bandwidth-ul intre host-uri using iperf.
    
    Args:
        net: Instanta Mininet activa
    
    Returns:
        Dict with resultele masuratorilor
    """
    info('\n*** Running bandwidth test\n')
    
    results = {}
    
    h1 = net.get('h1')
    h2 = net.get('h2')
    
    # Pornim iperf server pe h1
    h1.cmd('iperf -s &')
    time.sleep(0.5)
    
    # Rulam client pe h2
    result = h2.cmd(f'iperf -c {h1.IP()} -t 2')
    
    # Parsam resultul
    for line in result.split('\n'):
        if 'bits/sec' in line:
            parts = line.split()
            for i, part in enamerate(parts):
                if 'bits/sec' in part:
                    bandwidth = f"{parts[i-1]} {part}"
                    results['h1-h2'] = bandwidth
                    info(f'  h1 <-> h2: {bandwidth}\n')
                    break
    
    # Cleanup
    h1.cmd('kill %iperf 2>/dev/null')
    
    return results


def run_latency_test(net: Mininet) -> dict:
    """
    Masoara latenta intre host-uri.
    
    Args:
        net: Instanta Mininet activa
    
    Returns:
        Dict with latentele masurate
    """
    info('\n*** Running latency test\n')
    
    results = {}
    
    h1 = net.get('h1')
    h2 = net.get('h2')
    
    # Ping with statistici
    result = h1.cmd(f'ping -c 10 {h2.IP()}')
    
    # Parsam rtt
    for line in result.split('\n'):
        if 'rtt' in line:
            # rtt min/avg/max/mdev = 10.123/10.456/10.789/0.123 ms
            parts = line.split('=')[1].strip().split('/')
            if len(parts) >= 2:
                avg_latency = parts[1]
                results['h1-h2'] = f"{avg_latency} ms"
                info(f'  h1 <-> h2 avg latency: {avg_latency} ms\n')
    
    return results


def main():
    """Entry point principal."""
    parser = argparse.ArgumentParser(
        description='Base Mininet Topology for Week 10',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python3 topo_10_base.py           # Interactive CLI
  sudo python3 topo_10_base.py --test    # Run automated tests
  sudo python3 topo_10_base.py --hosts 5 # 5 hosts instead of 3
        """
    )
    parser.add_argument('--test', action='store_true',
                        help='Run automated tests instead of CLI')
    parser.add_argument('--hosts', type=int, default=3,
                        help='Number of hosts (default: 3)')
    parser.add_argument('--bw', type=int, default=100,
                        help='Link bandwidth in Mbps (default: 100)')
    parser.add_argument('--delay', default='5ms',
                        help='Link delay (default: 5ms)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        setLogLevel('debug')
    else:
        setLogLevel('info')
    
    info('*** Creating network\n')
    
    topo = BaseTopo(
        n_hosts=args.hosts,
        bw=args.bw,
        delay=args.delay
    )
    
    net = Mininet(
        topo=topo,
        switch=OVSKernelSwitch,
        link=TCLink,
        controller=Controller
    )
    
    try:
        info('*** Starting network\n')
        net.start()
        
        # Afisam informatii despre network
        info('\n*** Network information:\n')
        for host in net.hosts:
            info(f'  {host.name}: {host.IP()}\n')
        
        if args.test:
            # Rulam testele automate
            info('\n' + '='*60 + '\n')
            info(' AUTOMATED TESTS '.center(60, '='))
            info('\n' + '='*60 + '\n')
            
            conn_ok = run_connectivity_test(net)
            latency = run_latency_test(net)
            bandwidth = run_bandwidth_test(net)
            http_ok = run_http_server_test(net)
            
            info('\n' + '='*60 + '\n')
            info(' TEST SUMMARY '.center(60, '='))
            info('\n' + '='*60 + '\n')
            info(f'  Connectivity: {"PASS" if conn_ok else "FAIL"}\n')
            info(f'  Latency: {latency}\n')
            info(f'  Bandwidth: {bandwidth}\n')
            info(f'  HTTP: {"PASS" if http_ok else "FAIL"}\n')
            
            # Exit code based on tests
            if conn_ok and http_ok:
                info('\n*** All tests PASSED\n')
                sys.exit(0)
            else:
                info('\n*** Some tests FAILED\n')
                sys.exit(1)
        else:
            # Mod interactiv
            info('\n*** Starting CLI\n')
            info('  Useful commands:\n')
            info('    h1 ping h2\n')
            info('    h1 python3 -m http.server 8000 &\n')
            info('    h2 curl http://10.0.0.1:8000/\n')
            info('    pingall\n')
            info('    iperf h1 h2\n')
            info('    exit\n\n')
            
            CLI(net)
    
    finally:
        info('\n*** Stopping network\n')
        net.stop()


if __name__ == '__main__':
    main()
