# CLI Cheatsheet — Week 5: IP Addressing

## Week 5 Network Plan

| Component | Value |
|-----------|-------|
| Main Network | `10.0.5.0/24` |
| Gateway/Router | `10.0.5.1` |
| Application server | `10.0.5.100`, `10.0.5.101` |
| Standard Hosts | `h1=10.0.5.11`, `h2=10.0.5.12`, `h3=10.0.5.13` |
| port Base | `5500-5599` |

## Quick Commands

### CIDR Analysis

```bash
# Complete analysis
python3 python/exercises/ex_5_01_cidr_flsm.py analyze 192.168.10.14/26

# With details and binary
python3 python/exercises/ex_5_01_cidr_flsm.py analyze 192.168.10.14/26 --verbose

# JSON output
python3 python/exercises/ex_5_01_cidr_flsm.py analyze 192.168.10.14/26 --json

# Binary conversion
python3 python/exercises/ex_5_01_cidr_flsm.py binary 10.0.5.1
```

### FLSM Subnetting

```bash
# Split into 4 equal subnets
python3 python/exercises/ex_5_01_cidr_flsm.py flsm 192.168.100.0/24 4

# Split into 8 subnets
python3 python/exercises/ex_5_01_cidr_flsm.py flsm 10.0.0.0/24 8

# JSON output
python3 python/exercises/ex_5_01_cidr_flsm.py flsm 10.0.0.0/24 4 --json
```

### VLSM Allocation

```bash
# Allocation for 60, 20, 10, 2 hosts
python3 python/exercises/ex_5_02_vlsm_ipv6.py vlsm 172.16.0.0/24 60 20 10 2

# Complex scenario
python3 python/exercises/ex_5_02_vlsm_ipv6.py vlsm 10.10.0.0/22 200 100 50 25 10 2 2 2

# JSON output
python3 python/exercises/ex_5_02_vlsm_ipv6.py vlsm 10.0.5.0/24 50 30 10 2 --json
```

### IPv6

```bash
# Address compression
python3 python/exercises/ex_5_02_vlsm_ipv6.py ipv6 2001:0db8:0000:0000:0000:0000:0000:0001

# Address expansion
python3 python/exercises/ex_5_02_vlsm_ipv6.py ipv6-expand 2001:db8::1

# Subnet generation
python3 python/exercises/ex_5_02_vlsm_ipv6.py ipv6-subnets 2001:db8:10::/48 64 10

# IPv6 address types
python3 python/exercises/ex_5_02_vlsm_ipv6.py ipv6-types
```

## Mininet

### Starting Topologies

```bash
# Base topology (2 subnets)
sudo python3 mininet/topologies/topo_5_base.py --cli

# Extended topology (VLSM)
sudo python3 mininet/topologies/topo_5_extended.py --cli

# With IPv6 enabled
sudo python3 mininet/topologies/topo_5_extended.py --cli --ipv6

# Automatic test
sudo python3 mininet/topologies/topo_5_base.py --test
```

### Mininet CLI Commands

```bash
# List nodes and topology
nodes
net
links

# IP information
h1 ip addr
h1 ip route
r1 ip route

# Ping and connectivity
h1 ping -c 3 10.0.2.10
h1 ping6 -c 3 2001:db8:10:20::10

# Packet capture
r1 tcpdump -ni r1-eth0 icmp &
h1 ping -c 5 10.0.2.10
r1 kill %tcpdump

# Separate terminal
xterm h1

# Exit
exit
```

### Mininet Cleanup

```bash
# Standard cleanup
sudo mn -c

# Restart OVS
sudo systemctl restart openvswitch-switch

# Cleanup script
./scripts/cleanup.sh --mininet
```

## Linux IP Commands

### Display Configuration

```bash
# IP addresses
ip addr show
ip -4 addr show     # IPv4 only
ip -6 addr show     # IPv6 only

# Routing table
ip route show
ip -6 route show

# Interfaces
ip link show
```

### Manual Configuration

```bash
# Add address
sudo ip addr add 10.0.5.100/24 dev eth0

# Delete address
sudo ip addr del 10.0.5.100/24 dev eth0

# Default gateway
sudo ip route add default via 10.0.5.1

# Specific route
sudo ip route add 192.168.0.0/16 via 10.0.5.1

# Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1
sudo sysctl -w net.ipv6.conf.all.forwarding=1
```

## Traffic Capture

### tcpdump

```bash
# Capture all packets on eth0
sudo tcpdump -i eth0

# ICMP only
sudo tcpdump -i eth0 icmp

# Single address only
sudo tcpdump -i eth0 host 10.0.5.100

# Save to file
sudo tcpdump -i eth0 -w /tmp/capture.pcap

# With timestamps and verbose
sudo tcpdump -i eth0 -tttt -vv
```

### tshark

```bash
# Read capture
tshark -r /tmp/capture.pcap

# IP filtering
tshark -r /tmp/capture.pcap -Y "ip.addr == 10.0.5.1"

# Specific fields
tshark -r /tmp/capture.pcap -T fields -e ip.src -e ip.dst -e ip.ttl

# Statistics
tshark -r /tmp/capture.pcap -q -z io,stat,1
```

## Quick Formulas

| prefix | Mask | Hosts | Increment |
|--------|------|-------|-----------|
| /24 | 255.255.255.0 | 254 | 256 |
| /25 | 255.255.255.128 | 126 | 128 |
| /26 | 255.255.255.192 | 62 | 64 |
| /27 | 255.255.255.224 | 30 | 32 |
| /28 | 255.255.255.240 | 14 | 16 |
| /29 | 255.255.255.248 | 6 | 8 |
| /30 | 255.255.255.252 | 2 | 4 |

**Formula**: Hosts = 2^(32-prefix) - 2

## Make Targets

```bash
make help           # All commands
make setup          # Installation
make test           # Smoke tests
make demo           # Complete demo
make demo-cidr      # CIDR demo
make demo-vlsm      # VLSM demo
make quiz           # Interactive quiz
make clean          # Cleanup
make reset          # Complete reset

# Mininet (with sudo)
sudo make mininet-base
sudo make mininet-extended-ipv6
sudo make mininet-test
sudo make mininet-clean
```

## References

- RFC 791: IPv4
- RFC 8200: IPv6
- RFC 1918: Private Addresses
- RFC 4291: IPv6 Architecture
- Mininet: http://mininet.org/walkthrough/

---

*Rezolvix&Hypotheticalandrei | ASE-CSIE | MIT Licence*
