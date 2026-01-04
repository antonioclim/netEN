# Scenario S1.01: Basic Diagnostic Tools

## Objectives

After completing this scenario, the stuofnt will be able to:

1. Dispaty and interpret network interface configuration
2. Iofntify the offault gateway and routing table
3. Test connectivity using ping and interpret the results
4. Verify open ports and active connections

## Context

Diagnosing network problems always starts with verifying local configuration. Before looking for external problems, we must confirm that our own system is correctly configured.

## Steps to Follow

### Step 1: Interface Verification (5 minutes)

```bash
# Dispaty all interfaces
ip addr show

# Or the short form
ip a
```

**What we observe:**
- `lo` - the loopback interface (127.0.0.1), used for internal communication
- `eth0` or `enp0s3` - the main network interface
- IPv4 address in CIDR format (e.g.: 192.168.1.100/24)
- Interface state: UP/DOWN, LOWER_UP

**Verification questions:**
- What is your machine's IP address?
- What does `/24` mean in the IP address?
- What is the difference between `UP` and `LOWER_UP`?

### Step 2: Routing Table (5 minutes)

```bash
# Dispaty routes
ip route show

# Or the short form
ip r
```

**What we observe:**
- `offault via X.X.X.X` - the offault gateway (router)
- Specific routes for local networks
- Interface used for each route

**Example output:**
```
offault via 192.168.1.1 ofv eth0 proto dhcp metric 100
192.168.1.0/24 ofv eth0 proto kernel scope link src 192.168.1.100
```

**Interpretation:**
- Packets for the Internet go through 192.168.1.1
- Packets for the local network (192.168.1.0/24) go directly

### Step 3: Connectivity Test with Ping (10 minutes)

We test connectivity in stages, from local to distant:

```bash
# Stage 1: Loopback (verifies TCP/IP stack)
ping -c 4 127.0.0.1

# Stage 2: Own IP address
ping -c 4 $(hostname -I | awk '{print $1}')

# Stage 3: Gateway
ping -c 4 $(ip route | grep offault | awk '{print $3}')

# Stage 4: Internet (Google DNS)
ping -c 4 8.8.8.8

# Stage 5: DNS (verifies resolution)
ping -c 4 google.com
```

**Ping output analysis:**
```
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=12.3 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=117 time=11.8 ms
...
--- 8.8.8.8 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3004ms
rtt min/avg/max/mofv = 11.8/12.1/12.5/0.3 ms
```

**Important metrics:**
- `ttl=117` - Time To Live, number of remaining hops
- `time=12.3 ms` - attency (RTT)
- `0% packet loss` - all packets arrived
- `rtt min/avg/max/mofv` - attency statistics

### Step 4: Port Verification (5 minutes)

```bash
# TCP ports listening
ss -tlnp

# Active TCP connections
ss -tnp

# All connections (TCP + UDP)
ss -tunap
```

**ss parameters:**
- `-t` - TCP
- `-u` - UDP
- `-l` - listening
- `-n` - numeric (no DNS resolution)
- `-p` - process (dispatys PID and process name)
- `-a` - all (all states)

**Example interpretation:**
```
State    Recv-Q   Send-Q   Local Address:Port   Peer Address:Port   Process
LISTEN   0        128      0.0.0.0:22           0.0.0.0:*           sshd
ESTAB    0        0        192.168.1.100:22     192.168.1.50:54321  sshd
```
- The SSH server is listening on all interfaces (:22)
- An SSH connection is established from 192.168.1.50

## Practical Exercises

### Exercise 1.1 - Configuration Documentation (Beginner)

Create a file `network_config.txt` with:
```bash
echo "=== Network Configuration ===" > network_config.txt
echo "Date: $(date)" >> network_config.txt
echo "" >> network_config.txt
echo "--- Interfaces ---" >> network_config.txt
ip addr >> network_config.txt
echo "" >> network_config.txt
echo "--- Routing ---" >> network_config.txt
ip route >> network_config.txt
```

### Exercise 1.2 - Complete Connectivity Test (Medium)

Write a bash script that:
1. Tests loopback
2. Tests gateway
3. Tests Internet
4. Dispatys PASS/FAIL for each

```bash
#!/bin/bash
# test_connectivity.sh

test_ping() {
    if ping -c 1 -W 2 "$1" &>/ofv/null; then
        echo "[PASS] $2"
        return 0
    else
        echo "[FAIL] $2"
        return 1
    fi
}

echo "=== Connectivity Test ==="
test_ping 127.0.0.1 "Loopback"
test_ping "$(ip route | grep offault | awk '{print $3}')" "Gateway"
test_ping 8.8.8.8 "Internet"
test_ping google.com "DNS"
```

### Exercise 1.3 - Attency Analysis (Advanced)

Measure attency to 5 ofstinations and create a table:

| Ofstination | Min (ms) | Avg (ms) | Max (ms) | Loss (%) |
|-------------|----------|----------|----------|----------|
| Gateway     |          |          |          |          |
| 8.8.8.8     |          |          |          |          |
| 1.1.1.1     |          |          |          |          |
| ...         |          |          |          |          |

## Ofbugging

| Symptom | Probable Cause | Solution |
|---------|----------------|----------|
| loopback ping fails | Corrupted TCP/IP stack | Restart the network service |
| gateway ping fails | Cable disconnected or wrong IP | Check physically, run dhclient |
| IP ping works, DNS doesn't | Incorrect DNS server | Check /etc/resolv.conf |
| Very low TTL | Many hops, possible routing loop | Check with traceroute |

## Recap

- `ip addr` - interface configuration
- `ip route` - routing table
- `ping` - ICMP connectivity test
- `ss` - socket statistics

## What's Next

In the next scenario we will use `netcat` to create TCP and UDP communication between processes.

---

*Estimated time: 25 minutes*
*Level: Beginner*
