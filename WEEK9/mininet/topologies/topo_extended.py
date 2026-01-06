#!/usr/bin/env python3
"""
Extended Mininet Topology for Seminar/Laboratory 9
Computer Networks - ASE Bucharest

Plan IP Week 9: 10.0.9.0/24

Topology with multiple clients and differentiated latency:

    h1 (server) ──── s1 ──┬── s2 ──── h2 (client-local)
        10.0.9.100        │           10.0.9.12
                          │           (low latency)
                          │
                          └── s3 ──── h3 (client-remote)
                                      10.0.9.13
                                      (high latency)

This scenario simulates:
- Un client local (datacenter)
- A remote client (WAN with high latency)

Usage:
    sudo python topo_extended.py
    sudo python topo_extended.py --remote-delay 100ms --remote-loss 2

Revolvix&Hypotheticalandrei | MIT Licence
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import argparse
import os
import sys
import time

# Week 9 IP Plan
WEEK = 9
NETWORK = f"10.0.{WEEK}"
SERVER_IP = f"{NETWORK}.100/24"
CLIENT_LOCAL_IP = f"{NETWORK}.12/24"
CLIENT_REMOTE_IP = f"{NETWORK}.13/24"

class FTPExtendedTopo(Topo):
    """
    Extended topology with server, client local and client remote.
    
    Configuration Week 9 (10.0.9.0/24):
    - h1: Server FTP (10.0.9.100) - conectat to s1
    - h2: Client Local (10.0.9.12) - connected via s2 (low latency)
    - h3: Client Remote (10.0.9.13) - connected via s3 (high latency)
    - s1: Switch central
    - s2: Switch "local" (datacenter)
    - s3: Switch "remote" (WAN)
    """
    
    def build(self, 
              local_bw=100, local_delay='1ms', local_loss=0,
              remote_bw=50, remote_delay='50ms', remote_loss=1,
              backbone_bw=1000, backbone_delay='0ms'):
        """
        Builds the topology.
        
        Args:
            local_bw: Bandwidth for link local (Mbps)
            local_delay: Latency for local
            local_loss: Packet loss for link local (%)
            remote_bw: Bandwidth for link remote (Mbps)
            remote_delay: Latency for remote
            remote_loss: Packet loss for link remote (%)
            backbone_bw: Bandwidth for backbone between switches (Mbps)
            backbone_delay: Backbone latency
        """
        info('*** Building extended topology (Week 9: 10.0.9.0/24)\n')
        
        # Switch-uri
        s1 = self.addSwitch('s1', cls=OVSSwitch)  # Central
        s2 = self.addSwitch('s2', cls=OVSSwitch)  # Local
        s3 = self.addSwitch('s3', cls=OVSSwitch)  # Remote
        
        # Hosts with IP-uri Week 9
        h1 = self.addHost('h1', ip=SERVER_IP)       # 10.0.9.100
        h2 = self.addHost('h2', ip=CLIENT_LOCAL_IP)  # 10.0.9.12
        h3 = self.addHost('h3', ip=CLIENT_REMOTE_IP) # 10.0.9.13
        
        # Backbone links (between switches)
        backbone_opts = {
            'bw': backbone_bw,
            'delay': backbone_delay,
            'use_htb': True
        }
        self.addLink(s1, s2, **backbone_opts)
        self.addLink(s1, s3, **backbone_opts)
        
        # Link server to switch central
        server_opts = {
            'bw': backbone_bw,
            'delay': '0ms',
            'use_htb': True
        }
        self.addLink(h1, s1, **server_opts)
        
        # Link client local
        local_opts = {
            'bw': local_bw,
            'delay': local_delay,
            'loss': local_loss,
            'use_htb': True
        }
        self.addLink(h2, s2, **local_opts)
        
        # Link client remote
        remote_opts = {
            'bw': remote_bw,
            'delay': remote_delay,
            'loss': remote_loss,
            'use_htb': True
        }
        self.addLink(h3, s3, **remote_opts)
        
        info(f'*** Topology configured:\n')
        info(f'    Server h1 ({SERVER_IP.split("/")[0]}) -- s1 [backbone]\n')
        info(f'    Client Local h2 ({CLIENT_LOCAL_IP.split("/")[0]}) -- s2 [{local_bw}Mbps, {local_delay}, {local_loss}% loss]\n')
        info(f'    Client Remote h3 ({CLIENT_REMOTE_IP.split("/")[0]}) -- s3 [{remote_bw}Mbps, {remote_delay}, {remote_loss}% loss]\n')


def setup_environment(net):
    """
    Configures the environment for demos.
    """
    h1, h2, h3 = net.get('h1', 'h2', 'h3')
    
    # Directories
    h1.cmd('mkdir -p /tmp/server-files')
    h2.cmd('mkdir -p /tmp/client-local')
    h3.cmd('mkdir -p /tmp/client-remote')
    
    # Test files of different sizes
    h1.cmd('echo "Small test file" > /tmp/server-files/small.txt')
    h1.cmd('dd if=/dev/urandom of=/tmp/server-files/medium.bin bs=1024 count=100 2>/dev/null')
    h1.cmd('dd if=/dev/urandom of=/tmp/server-files/large.bin bs=1024 count=1000 2>/dev/null')
    
    info('*** Environment configured:\n')
    info('    h1:/tmp/server-files/ - server directory\n')
    info('    h2:/tmp/client-local/ - client directory local\n')
    info('    h3:/tmp/client-remote/ - client directory remote\n')
    info('    Files created: small.txt (16B), medium.bin (100KB), large.bin (1MB)\n')


def run_latency_test(net):
    """
    Runs latency test between hosts.
    """
    h1, h2, h3 = net.get('h1', 'h2', 'h3')
    server_ip = SERVER_IP.split('/')[0]  # 10.0.9.100
    
    info('\n*** Test latency\n')
    
    info(f'h2 (local) -> h1 (server {server_ip}):\n')
    result_local = h2.cmd(f'ping -c 5 {server_ip}')
    # Extract average RTT
    for line in result_local.split('\n'):
        if 'rtt' in line or 'avg' in line:
            info(f'    {line}\n')
    
    info(f'h3 (remote) -> h1 (server {server_ip}):\n')
    result_remote = h3.cmd(f'ping -c 5 {server_ip}')
    for line in result_remote.split('\n'):
        if 'rtt' in line or 'avg' in line:
            info(f'    {line}\n')


def run_bandwidth_test(net):
    """
    Runs bandwidth test using iperf.
    """
    h1, h2, h3 = net.get('h1', 'h2', 'h3')
    server_ip = SERVER_IP.split('/')[0]  # 10.0.9.100
    
    info('\n*** Test bandwidth with iperf\n')
    
    # Starting server iperf pe h1
    h1.cmd('iperf -s &')
    time.sleep(1)
    
    info('h2 (local) -> h1:\n')
    result_local = h2.cmd(f'iperf -c {server_ip} -t 5')
    for line in result_local.split('\n'):
        if 'Mbits' in line or 'Gbits' in line:
            info(f'    {line}\n')
    
    info('h3 (remote) -> h1:\n')
    result_remote = h3.cmd(f'iperf -c {server_ip} -t 5')
    for line in result_remote.split('\n'):
        if 'Mbits' in line or 'Gbits' in line:
            info(f'    {line}\n')
    
    # Stopping iperf server
    h1.cmd('pkill iperf')


def print_extended_help():
    """Displays instructions for extended topology."""
    help_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              MININET FTP EXTENDED TOPOLOGY - HELP                            ║
║              Week 9 IP Plan: 10.0.9.0/24                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

TOPOLOGIE:
                    ┌─── s2 ──── h2 (client-local, 10.0.9.12)
  h1 (server) ─── s1 ───┤           [low latency, high bandwidth]
  10.0.9.100           │
                        └─── s3 ──── h3 (client-remote, 10.0.9.13)
                                    [high latency, lower bandwidth]

HOST INFORMATION:
  h1 (10.0.9.100) - Server FTP
  h2 (10.0.9.12)  - Client Local (datacenter)
  h3 (10.0.9.13)  - Client Remote (WAN)

SCENARII DE TEST:

  1. Latency comparison:
     mininet> h2 ping -c 5 10.0.9.100
     mininet> h3 ping -c 5 10.0.9.100
     
  2. Transfer paralel:
     mininet> h1 python3 server.py --port 5900 &
     mininet> h2 python3 client.py --host 10.0.9.100 --port 5900 &
     mininet> h3 python3 client.py --host 10.0.9.100 --port 5900 &
     
  3. Test bandwidth:
     mininet> h1 iperf -s &
     mininet> h2 iperf -c 10.0.9.100 -t 10
     mininet> h3 iperf -c 10.0.9.100 -t 10
     mininet> h1 pkill iperf

  4. Modificare latency in runtime:
     mininet> sh tc qdisc change dev s3-eth2 root netem delay 200ms

SPECIAL COMMANDS:
  ftphelp     - Display this message
  latencytest - Run latency test
  bwtest      - Run bandwidth test

DIRECTORIES:
  Server: h1:/tmp/server-files/
  Client Local: h2:/tmp/client-local/
  Client Remote: h3:/tmp/client-remote/

═══════════════════════════════════════════════════════════════════════════════
"""
    print(help_text)


def run_topology(local_bw=100, local_delay='1ms', local_loss=0,
                 remote_bw=50, remote_delay='50ms', remote_loss=1,
                 interactive=True):
    """
    Starts extended Mininet topology.
    """
    setLogLevel('info')
    
    info('*** Creare topology FTP Extended\n')
    topo = FTPExtendedTopo(
        local_bw=local_bw, local_delay=local_delay, local_loss=local_loss,
        remote_bw=remote_bw, remote_delay=remote_delay, remote_loss=remote_loss
    )
    
    info('*** Starting Mininet network\n')
    net = Mininet(
        topo=topo,
        controller=Controller,
        link=TCLink,
        autoSetMacs=True
    )
    
    net.start()
    
    info('*** Configuring environment\n')
    setup_environment(net)
    
    info('*** Testing connectivity\n')
    net.pingAll()
    
    # Initial latency test
    run_latency_test(net)
    
    if interactive:
        info('\n*** Type "ftphelp" for instructions\n')
        
        # Register custom commands
        CLI.do_ftphelp = lambda self, _: print_extended_help()
        CLI.do_latencytest = lambda self, _: run_latency_test(net)
        CLI.do_bwtest = lambda self, _: run_bandwidth_test(net)
        
        CLI(net)
        
        info('*** Stopping network\n')
        net.stop()
    else:
        return net


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Extended Mininet Topology for Seminar 9 - FTP with local/remote clients',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python topo_extended.py                           # Default configuration
  sudo python topo_extended.py --remote-delay 100ms      # High latency for remote
  sudo python topo_extended.py --remote-loss 5           # 5% packet loss pe remote
  sudo python topo_extended.py --local-bw 1000           # Gigabit for local
        """
    )
    
    # Parametri link local
    parser.add_argument('--local-bw', type=int, default=100,
                        help='Bandwidth link local (Mbps, default: 100)')
    parser.add_argument('--local-delay', type=str, default='1ms',
                        help='Local link latency (default: 1ms)')
    parser.add_argument('--local-loss', type=float, default=0,
                        help='Packet loss link local (%%, default: 0)')
    
    # Parametri link remote
    parser.add_argument('--remote-bw', type=int, default=50,
                        help='Bandwidth link remote (Mbps, default: 50)')
    parser.add_argument('--remote-delay', type=str, default='50ms',
                        help='Remote link latency (default: 50ms)')
    parser.add_argument('--remote-loss', type=float, default=1,
                        help='Packet loss link remote (%%, default: 1)')
    
    args = parser.parse_args()
    
    # Verify root privileges
    if os.geteuid() != 0:
        print("ERROR: This script requires root privileges.")
        print("Run with: sudo python topo_extended.py")
        sys.exit(1)
    
    run_topology(
        local_bw=args.local_bw, local_delay=args.local_delay, local_loss=args.local_loss,
        remote_bw=args.remote_bw, remote_delay=args.remote_delay, remote_loss=args.remote_loss
    )


if __name__ == '__main__':
    main()
