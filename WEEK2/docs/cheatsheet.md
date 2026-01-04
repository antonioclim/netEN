# CLI Cheatsheet - Week 2: Socket Programming

## Quick Commands

### Start Complete Demo
```bash
# Automatic demo (produces artefacts)
./scripts/run_all.sh

# Verify artefacts
./tests/smoke_test.sh
```

### TCP/UDP Servers Manual

```bash
# TCP server (threaded)
python3 seminar/python/exercises/ex_2_01_tcp.py server --port 9090

# UDP server
python3 seminar/python/exercises/ex_2_02_udp.py server --port 9091
```

### TCP/UDP Clients

```bash
# TCP client
python3 seminar/python/exercises/ex_2_01_tcp.py client \
    --host 127.0.0.1 --port 9090 --message "Hello"

# UDP client (single command)
python3 seminar/python/exercises/ex_2_02_udp.py client \
    --host 127.0.0.1 --port 9091 --once "ping"

# UDP client (interactive)
python3 seminar/python/exercises/ex_2_02_udp.py client \
    --host 127.0.0.1 --port 9091 --interactive
```

### Load Testing

```bash
# 10 concurrent TCP clients
python3 seminar/python/exercises/ex_2_01_tcp.py load \
    --host 127.0.0.1 --port 9090 --clients 10
```

---

## Captures and Analysis

### Capture with tcpdump

```bash
# TCP capture on loopback
sudo tcpdump -i lo -w capture_tcp.pcap tcp port 9090

# UDP capture
sudo tcpdump -i lo -w capture_udp.pcap udp port 9091

# Combined capture
sudo tcpdump -i lo -w capture_all.pcap '(tcp port 9090) or (udp port 9091)'
```

### Analysis with tshark

```bash
# Display all packets
tshark -r capture.pcap

# TCP filtering
tshark -r capture.pcap -Y "tcp"

# TCP handshake filtering
tshark -r capture.pcap -Y "tcp.flags.syn==1"

# Specific fields
tshark -r capture.pcap -T fields \
    -e frame.number -e ip.src -e tcp.srcport \
    -e ip.dst -e tcp.dstport -e tcp.flags.str

# Conversation statistics
tshark -r capture.pcap -z conv,tcp
```

### Netcat for debugging

```bash
# Simple TCP server
nc -l -p 9090

# TCP client
echo "test" | nc localhost 9090

# UDP server
nc -u -l -p 9091

# UDP client
echo "ping" | nc -u localhost 9091
```

---

## Mininet

### Basic Commands

```bash
# Start CLI with base topology
sudo python3 seminar/mininet/topologies/topo_2_base.py --cli

# Start CLI with extended topology
sudo python3 seminar/mininet/topologies/topo_2_extended.py --cli

# Automatic test
sudo python3 seminar/mininet/topologies/topo_2_base.py --test

# Clean previous sessions
sudo mn -c
```

### Commands in Mininet CLI

```
nodes              # Node list
net                # Topology
dump               # Node details
pingall            # Connectivity test
h1 ping h2         # Ping between hosts
h1 ifconfig        # Interface configuration
xterm h1           # Terminal for h1
```

### TCP Demo in Mininet

```
# In Mininet CLI:
h1 python3 /path/to/ex_2_01_tcp.py server --bind 10.0.2.100 --port 9090 &
h2 python3 /path/to/ex_2_01_tcp.py client --host 10.0.2.100 --port 9090 -m "test"
```

---

## Debugging

### port Verification

```bash
# Listening ports
ss -tuln

# Check specific port
ss -tuln | grep 9090

# Processes on port
lsof -i :9090

# Kill process on port
fuser -k 9090/tcp
```

### Connection Verification

```bash
# Active connections
ss -tn

# Socket statistics
ss -s

# Real-time monitoring
watch -n 1 'ss -tn | grep 9090'
```

### Python Log and debugging

```bash
# Run with unbuffered output
python3 -u script.py

# With verbose
python3 script.py --verbose 2>&1 | tee log.txt
```

---

## WEEK 2 IP Plan

| Entity | IP | Note |
|--------|-----|------|
| Network | 10.0.2.0/24 | WEEK 2 |
| Gateway | 10.0.2.1 | Router |
| h1 | 10.0.2.11 | server |
| h2 | 10.0.2.12 | client |
| h3 | 10.0.2.13 | client |
| Application server | 10.0.2.100 | TCP/UDP |

## WEEK 2 port Plan

| Service | port | Protocol |
|---------|------|----------|
| TCP App | 9090 | TCP |
| UDP App | 9091 | UDP |
| HTTP | 8080 | TCP |
| Proxy | 8888 | TCP |
| Week Base | 5200-5299 | Custom |

---

## Quick Troubleshooting

| Problem | Verification command | Solution |
|---------|---------------------|----------|
| port occupied | `ss -tuln \| grep 9090` | `fuser -k 9090/tcp` |
| server not responding | `ping localhost` | Check firewall |
| Empty capture | `tcpdump -D` | Correct interface |
| Mininet blocked | `ps aux \| grep mininet` | `sudo mn -c` |
| Permission denied | `ls -at script.py` | `chmod +x script.py` |

---

*WEEK 2 - Socket Programming TCP/UDP*
*ASE Bucharest, CSIE*
