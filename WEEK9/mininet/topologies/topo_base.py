#!/usr/bin/env python3
"""
Base Mininet Topology for Seminar/Laboratory 9
Computer Networks - ASE Bucharest

Simple topology with 2 hosts and 1 switch:
    h1 (server) ──── s1 ──── h2 (client)
    10.0.9.11              10.0.9.12

Plan IP Week 9: 10.0.9.0/24
  - Gateway: 10.0.9.1
  - Hosts: 10.0.9.11-19
  - Server: 10.0.9.100

Usage:
    sudo python topo_base.py
    
In Mininet CLI:
    mininet> pingall
    mininet> h1 python /path/to/server.py &
    mininet> h2 python /path/to/client.py --host 10.0.9.11

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

# Week 9 IP Plan
WEEK = 9
NETWORK = f"10.0.{WEEK}"
H1_IP = f"{NETWORK}.11/24"
H2_IP = f"{NETWORK}.12/24"
SERVER_IP = f"{NETWORK}.100/24"

class FTPBaseTopo(Topo):
    """
    Base topology with 2 hosts for server-client testing.
    
    Configuration:
    - h1: Server FTP (10.0.0.1)
    - h2: Client FTP (10.0.0.2)
    - s1: Switch OpenFlow
    - Links with configurable bandwidth
    """
    
    def build(self, bw=100, delay='0ms', loss=0):
        """
        Builds the topology.
        
        Args:
            bw: Bandwidth in Mbps (default: 100)
            delay: Unidirectional latency (default: '0ms')
            loss: Packet loss in percentage (default: 0)
        """
        info('*** Building base topology (Week 9: 10.0.9.0/24)\n')
        
        # Adding switch
        s1 = self.addSwitch('s1', cls=OVSSwitch)
        
        # Adding hosts with Week 9 IPs
        h1 = self.addHost('h1', ip=H1_IP)  # 10.0.9.11
        h2 = self.addHost('h2', ip=H2_IP)  # 10.0.9.12
        
        # Configuring links with performance parameters
        link_opts = {
            'bw': bw,
            'delay': delay,
            'loss': loss,
            'use_htb': True  # Hierarchical Token Bucket for rate limiting
        }
        
        # Adding links
        self.addLink(h1, s1, **link_opts)
        self.addLink(h2, s1, **link_opts)
        
        info(f'*** Topology: h1 --[{bw}Mbps, {delay}, {loss}% loss]-- s1 --[{bw}Mbps, {delay}, {loss}% loss]-- h2\n')


def setup_environment(net):
    """
    Configures the environment for demos.
    
    - Creates necessary directories
    - Copies test files
    """
    h1 = net.get('h1')
    h2 = net.get('h2')
    
    # Creates directories for server and client
    h1.cmd('mkdir -p /tmp/server-files')
    h2.cmd('mkdir -p /tmp/client-files')
    
    # Creates test files on server
    h1.cmd('echo "Test file content for FTP demo" > /tmp/server-files/test.txt')
    h1.cmd('dd if=/dev/urandom of=/tmp/server-files/binary.bin bs=1024 count=10 2>/dev/null')
    
    info('*** Environment configured:\n')
    info('    h1:/tmp/server-files/ - server directory\n')
    info('    h2:/tmp/client-files/ - client directory\n')


def print_help():
    """Displays instructions for CLI usage."""
    help_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    MININET FTP BASE TOPOLOGY - HELP                          ║
║                    Week 9 IP Plan: 10.0.9.0/24                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

HOST INFORMATION:
  h1 (10.0.9.11) - Server FTP
  h2 (10.0.9.12) - Client FTP

USEFUL COMMANDS:

  Verify connectivity:
    mininet> pingall
    mininet> h1 ping -c 3 h2

  Starting server (example):
    mininet> h1 python3 /path/to/ex_9_02_pseudo_ftp.py server --port 5900 &

  Starting client (example):
    mininet> h2 python3 /path/to/ex_9_02_pseudo_ftp.py client --host 10.0.9.11 --port 5900

  Verify processes:
    mininet> h1 ps aux | grep python
    
  Stopping server:
    mininet> h1 pkill -f pseudo_ftp

  Capture traffic:
    mininet> h1 tcpdump -i h1-eth0 -w /tmp/capture.pcap &
    
  Add latency at runtime:
    mininet> sh tc qdisc add dev s1-eth1 root netem delay 50ms
    
  Verify latency:
    mininet> h1 ping -c 5 h2

DIRECTORIES:
  Server: h1:/tmp/server-files/
  Client: h2:/tmp/client-files/

EXIT:
  mininet> exit
  or Ctrl+D

═══════════════════════════════════════════════════════════════════════════════
"""
    print(help_text)


def run_topology(bw=100, delay='0ms', loss=0, interactive=True):
    """
    Starts the Mininet topology.
    
    Args:
        bw: Bandwidth in Mbps
        delay: Latency as string (ex: '10ms')
        loss: Packet loss in percentage
        interactive: If True, starts CLI; otherwise returns the network
    """
    setLogLevel('info')
    
    info('*** Creating FTP Base topology\n')
    topo = FTPBaseTopo(bw=bw, delay=delay, loss=loss)
    
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
    
    if interactive:
        info('\n*** Type "help" for instructions\n')
        
        # Register help command
        CLI.do_ftphelp = lambda self, _: print_help()
        
        CLI(net)
        
        info('*** Stopping network\n')
        net.stop()
    else:
        return net


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Base Mininet Topology for Seminar 9 - FTP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python topo_base.py                    # Default configuration
  sudo python topo_base.py --delay 50ms       # With 50ms latency
  sudo python topo_base.py --loss 5           # With 5% packet loss
  sudo python topo_base.py --bw 10            # Bandwidth limited to 10 Mbps
        """
    )
    
    parser.add_argument(
        '--bw', type=int, default=100,
        help='Bandwidth in Mbps (default: 100)'
    )
    parser.add_argument(
        '--delay', type=str, default='0ms',
        help='Unidirectional latency (default: 0ms)'
    )
    parser.add_argument(
        '--loss', type=float, default=0,
        help='Packet loss in percentage (default: 0)'
    )
    
    args = parser.parse_args()
    
    # Verify root privileges
    if os.geteuid() != 0:
        print("ERROR: This script requires root privileges.")
        print("Run with: sudo python topo_base.py")
        sys.exit(1)
    
    run_topology(bw=args.bw, delay=args.delay, loss=args.loss)


if __name__ == '__main__':
    main()
