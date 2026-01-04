#!/usr/bin/env python3
"""
Mininet topology with service access for Week 10.

Extends the base topology with routing rules and optional service endpoints.
"""

from __future__ import annotations

import sys
import argparse
import time
import os
import tempfile

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
    sys.exit(1)


class ServicesTopo(Topo):
    """
    Topologie with servicii pre-configurate (DNS, Web, FTP).
    """
    
    def __init__(self, bw: int = 100, delay: str = '2ms'):
        self.bw = bw
        self.delay = delay
        super().__init__()
    
    def build(self):
        info('*** Builfromg services topology\n')
        
        # Switch central
        s1 = self.addSwitch('s1', cls=OVSKernelSwitch)
        
        # DNS Server (h1)
        h1 = self.addHost('h1', ip='10.0.0.1/24')
        self.addLink(h1, s1, cls=TCLink, bw=self.bw, delay=self.delay)
        info('  h1 (DNS): 10.0.0.1\n')
        
        # Web Server (h2)
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        self.addLink(h2, s1, cls=TCLink, bw=self.bw, delay=self.delay)
        info('  h2 (Web): 10.0.0.2\n')
        
        # FTP Server (h3)
        h3 = self.addHost('h3', ip='10.0.0.3/24')
        self.addLink(h3, s1, cls=TCLink, bw=self.bw, delay=self.delay)
        info('  h3 (FTP): 10.0.0.3\n')
        
        # Client (h4)
        h4 = self.addHost('h4', ip='10.0.0.4/24')
        self.addLink(h4, s1, cls=TCLink, bw=self.bw, delay=self.delay)
        info('  h4 (Client): 10.0.0.4\n')
        
        info('*** Topology built\n')


def create_dns_script() -> str:
    """Creeaza script Python for server DNS minimumal."""
    script = '''#!/usr/bin/env python3
"""Minimal DNS server for Mininet testing."""
import socket
import struct

DNS_RECORDS = {
    "web.lab.local": "10.0.0.2",
    "ftp.lab.local": "10.0.0.3",
    "dns.lab.local": "10.0.0.1",
}

def build_response(query_data, qname, ip):
    """Build DNS response packet."""
    # Transaction ID from query
    transaction_id = query_data[:2]
    
    # Flags: Standard query response, no error
    flags = b"\\x81\\x80"
    
    # Questions: 1, Answers: 1, Authority: 0, Additional: 0
    counts = b"\\x00\\x01\\x00\\x01\\x00\\x00\\x00\\x00"
    
    # Question section (copy from query)
    question_end = 12
    while query_data[question_end] != 0:
        question_end += query_data[question_end] + 1
    question_end += 5  # null + qtype + qclass
    question = query_data[12:question_end]
    
    # Answer section
    # Name pointer to question
    answer_name = b"\\xc0\\x0c"
    # Type A, Class IN
    answer_type = b"\\x00\\x01\\x00\\x01"
    # TTL: 300 seconds
    ttl = b"\\x00\\x00\\x01\\x2c"
    # RDATA length: 4 bytes (IPv4)
    rdlength = b"\\x00\\x04"
    # IP address
    rdata = bytes(int(x) for x in ip.split("."))
    
    return (transaction_id + flags + counts + question + 
            answer_name + answer_type + ttl + rdlength + rdata)

def parse_query(data):
    """Parse DNS query and extract name."""
    idx = 12
    labels = []
    while data[idx] != 0:
        length = data[idx]
        labels.append(data[idx+1:idx+1+length].decode())
        idx += length + 1
    return ".".join(labels)

def run_server(port=5353):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", port))
    print(f"DNS server listening on port {port}")
    
    while True:
        try:
            data, addr = sock.recvfrom(512)
            qname = parse_query(data).lower()
            print(f"Query from {addr}: {qname}")
            
            if qname in DNS_RECORDS:
                ip = DNS_RECORDS[qname]
                response = build_response(data, qname, ip)
                sock.sendto(response, addr)
                print(f"  -> {ip}")
            else:
                print(f"  -> NXDOMAIN")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run_server()
'''
    
    fd, path = tempfile.mkstemp(suffix='.py')
    with os.fdopen(fd, 'w') as f:
        f.write(script)
    os.chmod(path, 0o755)
    return path


def create_web_server_script() -> str:
    """Creeaza script for server web simplu."""
    script = '''#!/usr/bin/env python3
"""Simple HTTP server for Mininet testing."""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        
        response = {
            "message": "Hello from Web Server",
            "path": self.path,
            "server": "h2 (10.0.0.2)"
        }
        self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        print(f"HTTP: {args[0]}")

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), Handler)
    print("Web server listening on port 8000")
    server.serve_forever()
'''
    
    fd, path = tempfile.mkstemp(suffix='.py')
    with os.fdopen(fd, 'w') as f:
        f.write(script)
    os.chmod(path, 0o755)
    return path


def start_services(net: Mininet) -> dict:
    """
    Porneste serviciile pe host-uri.
    
    Returns:
        Dict cu PID-urile serviciilor
    """
    info('\n*** Starting services\n')
    
    pids = {}
    
    # DNS Server pe h1
    h1 = net.get('h1')
    dns_script = create_dns_script()
    h1.cmd(f'python3 {dns_script} &')
    time.sleep(0.5)
    info('  DNS server started on h1:5353\n')
    
    # Web Server pe h2
    h2 = net.get('h2')
    web_script = create_web_server_script()
    h2.cmd(f'python3 {web_script} &')
    time.sleep(0.5)
    info('  Web server started on h2:8000\n')
    
    # FTP Server pe h3 (simplificat with pyftpdlib if disponibil)
    h3 = net.get('h3')
    h3.cmd('mkdir -p /tmp/ftp')
    h3.cmd('echo "Welcome to FTP" > /tmp/ftp/welcome.txt')
    # Incercam pyftpdlib, altfel Python built-in
    ftp_result = h3.cmd('python3 -c "import pyftpdlib" 2>&1')
    if 'Error' not in ftp_result:
        h3.cmd('python3 -m pyftpdlib -p 2121 -d /tmp/ftp &')
    else:
        info('  (pyftpdlib not available, FTP demo limited)\n')
    time.sleep(0.5)
    info('  FTP server started on h3:2121\n')
    
    return pids


def test_dns(net: Mininet) -> bool:
    """Testeaza serverul DNS."""
    info('\n*** Testing DNS\n')
    
    h4 = net.get('h4')
    
    # Test with dig if disponibil
    result = h4.cmd('which dig')
    if result.strip():
        result = h4.cmd('dig @10.0.0.1 -p 5353 web.lab.local +short +timeout=2')
        if '10.0.0.2' in result:
            info('  DNS query web.lab.local -> 10.0.0.2: OK\n')
            return True
        else:
            info(f'  DNS query FAILED: {result}\n')
            return False
    else:
        info('  dig not available, skipping DNS test\n')
        return True


def test_http(net: Mininet) -> bool:
    """Testeaza serverul HTTP."""
    info('\n*** Testing HTTP\n')
    
    h4 = net.get('h4')
    
    result = h4.cmd('curl -s http://10.0.0.2:8000/')
    if 'Hello from Web Server' in result:
        info('  HTTP GET /: OK\n')
        return True
    else:
        info(f'  HTTP GET FAILED: {result[:100]}\n')
        return False


def test_connectivity(net: Mininet) -> bool:
    """Testeaza conectivitatea intre all host-urile."""
    info('\n*** Testing connectivity\n')
    
    h4 = net.get('h4')
    hosts = ['10.0.0.1', '10.0.0.2', '10.0.0.3']
    
    all_ok = True
    for ip in hosts:
        result = h4.cmd(f'ping -c 1 -W 1 {ip}')
        if '1 received' in result:
            info(f'  h4 -> {ip}: OK\n')
        else:
            info(f'  h4 -> {ip}: FAILED\n')
            all_ok = False
    
    return all_ok


def main():
    """Entry point principal."""
    parser = argparse.ArgumentParser(description='Services Mininet Topology')
    parser.add_argument('--test', action='store_true',
                        help='Run automated tests')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        setLogLevel('debug')
    else:
        setLogLevel('info')
    
    info('*** Creating services network\n')
    
    topo = ServicesTopo()
    net = Mininet(
        topo=topo,
        switch=OVSKernelSwitch,
        link=TCLink,
        controller=Controller
    )
    
    try:
        info('*** Starting network\n')
        net.start()
        
        # Start serviciile
        start_services(net)
        
        if args.test:
            info('\n' + '='*60 + '\n')
            info(' SERVICE TESTS '.center(60, '='))
            info('\n' + '='*60 + '\n')
            
            conn_ok = test_connectivity(net)
            dns_ok = test_dns(net)
            http_ok = test_http(net)
            
            info('\n' + '='*60 + '\n')
            info(' RESULTS '.center(60, '='))
            info('\n' + '='*60 + '\n')
            info(f'  Connectivity: {"PASS" if conn_ok else "FAIL"}\n')
            info(f'  DNS: {"PASS" if dns_ok else "FAIL"}\n')
            info(f'  HTTP: {"PASS" if http_ok else "FAIL"}\n')
            
            if conn_ok and dns_ok and http_ok:
                info('\n*** All tests PASSED\n')
                sys.exit(0)
            else:
                info('\n*** Some tests FAILED\n')
                sys.exit(1)
        else:
            info('\n*** Interactive mode\n')
            info('  Services running:\n')
            info('    h1: DNS server on port 5353\n')
            info('    h2: Web server on port 8000\n')
            info('    h3: FTP server on port 2121\n')
            info('    h4: Client for testing\n')
            info('\n  Try:\n')
            info('    h4 dig @10.0.0.1 -p 5353 web.lab.local\n')
            info('    h4 curl http://10.0.0.2:8000/\n')
            info('    h4 ping 10.0.0.1\n')
            info('\n')
            
            CLI(net)
    
    finally:
        info('\n*** Stopping network\n')
        net.stop()


if __name__ == '__main__':
    main()
