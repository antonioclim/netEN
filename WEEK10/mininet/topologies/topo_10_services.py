#!/usr/bin/env python3
"""Week 10 - Mininet topology with simple network services.

This topology is a lightweight complement to the Docker-based services.
It starts a few minimal services directly inside Mininet hosts so that students
can:

- Practise name resolution in a controlled environment
- Observe TCP and UDP traffic with tcpdump
- Run simple client commands (curl, nc and dig-like UDP interactions)

The services are intentionally simplistic and are not drop-in replacements for
production daemons.
"""

from __future__ import annotations

import argparse
import sys
import time

from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch
from mininet.topo import Topo


def create_dns_script() -> str:
    """Return a minimal UDP responder used as a DNS-like service."""

    return r'''#!/usr/bin/env python3
import socket

HOST = "10.0.10.53"
PORT = 53

# A tiny static mapping used for demonstration.
RECORDS = {
    b"web.lab.local": b"10.0.20.80",
    b"api.lab.local": b"10.0.20.81",
    b"ftp.lab.local": b"10.0.20.21",
    b"ssh.lab.local": b"10.0.20.22",
}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
print(f"[dns] UDP server listening on {HOST}:{PORT}")

while True:
    data, addr = sock.recvfrom(512)
    name = data.strip()
    ip = RECORDS.get(name, b"0.0.0.0")
    sock.sendto(ip, addr)
'''


def create_tcp_banner_server(port: int, banner: str) -> str:
    """Return a tiny TCP banner server script."""

    return f'''#!/usr/bin/env python3
import socket

HOST = "0.0.0.0"
PORT = {port}
BANNER = {banner!r}

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((HOST, PORT))
sock.listen(5)
print(f"[svc] TCP banner server listening on {{HOST}}:{{PORT}}")

while True:
    conn, addr = sock.accept()
    try:
        conn.sendall(BANNER.encode("utf-8"))
    finally:
        conn.close()
'''


def create_web_content() -> str:
    return """<!doctype html>
<html lang=\"en\">
<head><meta charset=\"utf-8\"><title>Mininet Web Service</title></head>
<body>
  <h1>Mininet Web Service</h1>
  <p>This page is served from a Mininet host via <code>python -m http.server</code>.</p>
</body>
</html>
"""


class ServicesTopo(Topo):
    """A client subnet and a service subnet joined by a switch."""

    def build(self):
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Client subnet
        h1 = self.addHost('h1', ip='10.0.10.10/24', defaultRoute='via 10.0.10.1')
        dns = self.addHost('dns', ip='10.0.10.53/24')

        # Service subnet
        web = self.addHost('web', ip='10.0.20.80/24')
        api = self.addHost('api', ip='10.0.20.81/24')
        ftp = self.addHost('ftp', ip='10.0.20.21/24')
        ssh = self.addHost('ssh', ip='10.0.20.22/24')

        # A simple router implemented as a host with two interfaces
        r1 = self.addHost('r1')

        self.addLink(h1, s1)
        self.addLink(dns, s1)

        self.addLink(web, s2)
        self.addLink(api, s2)
        self.addLink(ftp, s2)
        self.addLink(ssh, s2)

        self.addLink(r1, s1)
        self.addLink(r1, s2)


def configure_router(net: Mininet) -> None:
    r1 = net.get('r1')

    # Assign router interface addresses.
    r1.cmd('ip addr add 10.0.10.1/24 dev r1-eth0')
    r1.cmd('ip addr add 10.0.20.1/24 dev r1-eth1')
    r1.cmd('ip link set r1-eth0 up')
    r1.cmd('ip link set r1-eth1 up')
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Set default route for clients and services.
    net.get('h1').cmd('ip route add default via 10.0.10.1')

    for h in ['web', 'api', 'ftp', 'ssh']:
        net.get(h).cmd('ip route add default via 10.0.20.1')


def start_services(net: Mininet) -> None:
    """Start lightweight servers on the corresponding hosts."""

    dns = net.get('dns')
    web = net.get('web')
    api = net.get('api')
    ftp = net.get('ftp')
    ssh = net.get('ssh')

    # DNS-like UDP service
    dns.cmd('cat > /tmp/dns_server.py <<\'PY\'\n' + create_dns_script() + '\nPY')
    dns.cmd('chmod +x /tmp/dns_server.py')
    dns.cmd('python3 /tmp/dns_server.py >/tmp/dns.log 2>&1 &')

    # Web (HTTP)
    web.cmd('mkdir -p /tmp/www')
    web.cmd('cat > /tmp/www/index.html <<\'HTML\'\n' + create_web_content() + '\nHTML')
    web.cmd('python3 -m http.server 80 --directory /tmp/www >/tmp/web.log 2>&1 &')

    # API (dummy banner over TCP 8080)
    api_script = create_tcp_banner_server(8080, 'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nHello from the API host\n')
    api.cmd('cat > /tmp/api_server.py <<\'PY\'\n' + api_script + '\nPY')
    api.cmd('chmod +x /tmp/api_server.py')
    api.cmd('python3 /tmp/api_server.py >/tmp/api.log 2>&1 &')

    # FTP and SSH (dummy TCP banner services)
    ftp_script = create_tcp_banner_server(21, '220 FTP service demo (Mininet)\r\n')
    ftp.cmd('cat > /tmp/ftp_banner.py <<\'PY\'\n' + ftp_script + '\nPY')
    ftp.cmd('chmod +x /tmp/ftp_banner.py')
    ftp.cmd('python3 /tmp/ftp_banner.py >/tmp/ftp.log 2>&1 &')

    ssh_script = create_tcp_banner_server(22, 'SSH-2.0-DemoSSH (Mininet)\r\n')
    ssh.cmd('cat > /tmp/ssh_banner.py <<\'PY\'\n' + ssh_script + '\nPY')
    ssh.cmd('chmod +x /tmp/ssh_banner.py')
    ssh.cmd('python3 /tmp/ssh_banner.py >/tmp/ssh.log 2>&1 &')


def run_tests(net: Mininet) -> bool:
    """Simple reachability and service checks."""

    h1 = net.get('h1')

    info('*** Running services topology tests\n')

    # Ping across router
    ping = h1.cmd('ping -c 1 -W 1 10.0.20.80')
    ok_ping = (' 0% packet loss' in ping) or ('1 received' in ping)
    info(f"*** Ping web host: {'PASS' if ok_ping else 'FAIL'}\n")

    # HTTP on Mininet web host
    http = h1.cmd('wget -q -O - http://10.0.20.80/ | head -n 1')
    ok_http = '<!doctype html>' in http.lower() or '<html' in http.lower()
    info(f"*** HTTP fetch: {'PASS' if ok_http else 'FAIL'}\n")

    # DNS-like UDP query (name as payload, IP as response)
    dns = h1.cmd("python3 - <<'PY'\nimport socket\nq=b'web.lab.local'\ns=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)\ns.settimeout(1.0)\ns.sendto(q,('10.0.10.53',53))\nprint(s.recvfrom(64)[0].decode())\nPY")
    ok_dns = dns.strip() == '10.0.20.80'
    info(f"*** UDP name resolution: {'PASS' if ok_dns else 'FAIL'}\n")

    return ok_ping and ok_http and ok_dns


def main() -> None:
    parser = argparse.ArgumentParser(description='Week 10 Mininet services topology')
    parser.add_argument('--test', action='store_true', help='Run a small automated test and exit')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose Mininet logs')
    args = parser.parse_args()

    setLogLevel('debug' if args.verbose else 'info')

    topo = ServicesTopo()
    net = Mininet(
        topo=topo,
        controller=Controller,
        switch=OVSKernelSwitch,
        link=TCLink,
        build=True,
        autoSetMacs=True,
    )

    try:
        info('*** Starting network\n')
        net.start()

        configure_router(net)
        start_services(net)
        time.sleep(1.0)

        if args.test:
            ok = run_tests(net)
            sys.exit(0 if ok else 1)

        info('\n*** Services started. Useful commands:\n')
        info('  h1 ping 10.0.20.80\n')
        info('  h1 wget -O - http://10.0.20.80/\n')
        info('  h1 nc -nv 10.0.20.22 22\n')
        info('  h1 nc -nv 10.0.20.21 21\n')
        info('  h1 tcpdump -ni h1-eth0\n\n')

        CLI(net)

    finally:
        info('*** Stopping network\n')
        net.stop()


if __name__ == '__main__':
    main()
