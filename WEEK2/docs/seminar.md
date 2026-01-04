# Seminar 2: Network Analysis and Socket Programming

**Course:** Computer Networks  
**Duration:** 2 hours (120 minutes)  
**Format:** Assisted laboratory with practical exercises  
**Tools:** Python 3, Mininet, Wireshark/tshark, tcpdump, netcat

---

## Week's Purpose

### What We Will Learn
This practical session introduces network programmeming using Python sockets. We will implement TCP/UDP servers and clients, capture traffic for analysis and correlate code with packets observed in capture.

### Why It Matters
The ability to programme network communications and diagnose problems through traffic analysis is essential for any developer of distributed applications, security specialist or systems administrator.

---

## Prerequisites

### From Lecture (Week 2)
- The OSI model: the 7 layers and their roles
- The TCP/IP model: the 4 practical layers
- The difference between TCP (connection-oriented) vs UDP (datagrams)
- The concept of encapsulation

### Working Environment Verification
```bash
python3 --version    # >= 3.8
sudo mn --version    # Mininet 2.3+
tshark -v            # Wireshark CLI
nc -h                # netcat
```

---

## Operational Objectives

At the end of this seminar, the student will be able to:

| Code | Objective |
|------|-----------|
| **O1** | Execute basic Mininet commands for connectivity testing |
| **O2** | Implement a concurrent TCP server using Python sockets |
| **O3** | Capture network traffic with tcpdump/tshark |
| **O4** | Analyse the TCP handshake and identify it in capture |
| **O5** | Compare TCP vs UDP behaviour |
| **O6** | Correlate application logs with packets from capture |

---

## Chronological Structure

### PHASE 0: Preparation (10 minutes)

#### Activity 0.1: Environment Verification
```bash
# Component verification
python3 --version
sudo mn --version
tshark -v | head -n 2
nc -h 2>&1 | head -n 1
```

**Expected result**: All commands return valid versions.

#### Activity 0.2: Previous Environment Cleanup
```bash
# Cleanup previous Mininet sessions
sudo mn -c

# Navigate to starterkit directory
cd starterkit_s2
make verify
```

#### Activity 0.3: Python Script Verification
```bash
# Syntax verification
python3 -m py_compile seminar/python/exercises/ex_2_01_tcp.py
python3 -m py_compile seminar/python/exercises/ex_2_02_udp.py
```

---

### PHASE 1: Mininet Warm-up (15 minutes)

#### Activity 1.1: Starting Topology

```bash
make mininet-cli
# or directly:
sudo python3 seminar/mininet/topologies/topo_2_base.py --cli
```

**Topology**:
- 1 switch (s1)
- 3 hosts (h1: 10.0.2.100, h2: 10.0.0.2, h3: 10.0.0.3)
- All in the same /24 subnet

#### Activity 1.2: Topology Exploration

In Mininet prompt:
```
mininet> nodes
available nodes are: 
h1 h2 h3 s1

mininet> net
h1 h1-eth0:s1-eth1
h2 h2-eth0:s1-eth2
h3 h3-eth0:s1-eth3
s1 lo:  s1-eth1:h1-eth0 s1-eth2:h2-eth0 s1-eth3:h3-eth0

mininet> dump
<Host h1: h1-eth0:10.0.2.100 pid=...>
<Host h2: h2-eth0:10.0.0.2 pid=...>
<Host h3: h3-eth0:10.0.0.3 pid=...>
<OVSSwitch s1: lo:127.0.0.1 ...>

mininet> h1 ifconfig h1-eth0
```

**Reflection questions**:
- What IP address does h1 have?
- What MAC address does the h1-eth0 interface have?
- How are the hosts connected?

#### Activity 1.3: Connectivity Test

```
mininet> pingall
*** Ping: testing ping reachability
h1 -> h2 h3 
h2 -> h1 h3 
h3 -> h1 h2 
*** Results: 0% dropped (6/6 received)

mininet> h1 ping -c 3 10.0.0.2
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=0.234 ms
...
```

**Discussion**: A successsful ping verifies connectivity at level L3 (IP via ICMP). It does not guarantee that an application responds at level L7!

---

### PHASE 2: TCP Lab (35 minutes)

#### Activity 2.1: Starting TCP server

In Mininet:
```
mininet> h1 python3 -u seminar/python/exercises/ex_2_01_tcp.py server --bind 10.0.2.100 --port 9090 --mode threaded &
```

**Parameters explained**:
- `--bind 10.0.2.100`: Listen only on h1 interface
- `--port 9090`: Listening port
- `--mode threaded`: One thread per connection (concurrent server)
- `&`: Run in background

**Verification**:
```
mininet> jobs
[1]+ Running    python3 -u ... &
```

#### Activity 2.2: Starting Traffic Capture

```
mininet> h2 tcpdump -i h2-eth0 -w seminar/captures/tcp_demo.pcap 'tcp port 9090' &
```

**BPF filter explanation**:
- `-i h2-eth0`: Capture interface
- `-w ...pcap`: Save in PCAP format
- `'tcp port 9090'`: Only TCP packets on port 9090

#### Activity 2.3: Sending Messages

**client from h2**:
```
mininet> h2 python3 seminar/python/exercises/ex_2_01_tcp.py client --host 10.0.2.100 --port 9090 --message "Hello from h2"
[14:32:15.123][client] RX 17B in 2.3ms: b'OK: HELLO FROM H2'
```

**client from h3**:
```
mininet> h3 python3 seminar/python/exercises/ex_2_01_tcp.py client --host 10.0.2.100 --port 9090 --message "Hello from h3"
```

**Test with netcat** (to demonstrate interoperability):
```
mininet> h2 sh -c 'echo "netcat test" | nc 10.0.2.100 9090'
OK: NETCAT TEST
```

**Observations in server log**:
- Precise timestamp
- Thread ID for each connection
- client IP:port
- Received message and sent response

#### Activity 2.4: Stopping Capture and Analysis

**Stop capture**:
```
mininet> jobs
[1]+ Running    python3 ... server ...
[2]+ Running    tcpdump ...

mininet> kill %2
```

**Analysis with tshark** (in separate terminal, not Mininet):
```bash
tshark -r seminar/captures/tcp_demo.pcap -Y "tcp.port==9090" -T fields \
  -e frame.number -e ip.src -e tcp.srcport -e ip.dst -e tcp.dstport -e tcp.flags.str
```

**Expected output** (for one session):
```
1   10.0.0.2   45678   10.0.2.100   9090   ··········S·    # SYN
2   10.0.2.100   9090    10.0.0.2   45678  ·······A··S·    # SYN-ACK
3   10.0.0.2   45678   10.0.2.100   9090   ·······A····    # ACK
4   10.0.0.2   45678   10.0.2.100   9090   ·······AP···    # DATA (PSH+ACK)
5   10.0.2.100   9090    10.0.0.2   45678  ·······A····    # ACK
6   10.0.2.100   9090    10.0.0.2   45678  ·······AP···    # RESPONSE
7   10.0.0.2   45678   10.0.2.100   9090   ·······A····    # ACK
...
```

**Analysis questions**:
1. Identify the 3 handshake packets (SYN → SYN-ACK → ACK)
2. How many distinct TCP sessions do you observe? (unique 4-tuple)
3. Where does the application payload appear?

**Payload visualisation**:
```bash
tshark -r seminar/captures/tcp_demo.pcap -Y "tcp.port==9090 and data" -T fields \
  -e frame.number -e ip.src -e ip.dst -e tcp.payload
```

---

### PHASE 3: UDP Lab (25 minutes)

#### Activity 3.1: Starting UDP server

First, stop TCP server:
```
mininet> jobs
mininet> kill %1
```

Start UDP server:
```
mininet> h1 python3 -u seminar/python/exercises/ex_2_02_udp.py server --bind 10.0.2.100 --port 9091 &
```

#### Activity 3.2: Starting UDP Capture

```
mininet> h2 tcpdump -i h2-eth0 -w seminar/captures/udp_demo.pcap 'udp port 9091' &
```

#### Activity 3.3: Interactive UDP client

```
mininet> h2 python3 seminar/python/exercises/ex_2_02_udp.py client --host 10.0.2.100 --port 9091 --interactive
```

**Test commands** (custom application protocol):
```
> ping
PONG (RTT: 0.8ms)

> upper:hello world
HELLO WORLD (RTT: 0.9ms)

> abc
UNKNOWN COMMAND (RTT: 0.7ms)

> exit
--- Stats: sent=3, received=3, timeouts=0 ---
```

#### Activity 3.4: TCP vs UDP Comparison

**Stop capture**:
```
mininet> kill %<job_number_tcpdump>
```

**UDP analysis**:
```bash
tshark -r seminar/captures/udp_demo.pcap -Y "udp.port==9091" -T fields \
  -e frame.number -e ip.src -e udp.srcport -e ip.dst -e udp.dstport -e frame.len
```

**Expected output**:
```
1   10.0.0.2   54321   10.0.2.100   9091   46
2   10.0.2.100   9091    10.0.0.2   54321   46
3   10.0.0.2   54321   10.0.2.100   9091   53
4   10.0.2.100   9091    10.0.0.2   54321   53
```

**Comparative questions**:

| Aspect | TCP | UDP |
|--------|-----|-----|
| Packets for one message | 9+ (handshake + data + ACK + FIN) | 2 (request + response) |
| Header overhead | 20+ bytes | 8 bytes |
| Handshake | Yes (SYN-SYN/ACK-ACK) | No |
| Acknowledgements | Yes (ACK for each segment) | No |
| Sequence numbers | Yes | No |
| Reordering | Yes | No |

---

### PHASE 4: Templates to Complete (25 minutes)

#### Activity 4.1: TCP server Template

**File**: `seminar/python/templates/tcp_server_template.py`

**Requirements to complete**:
1. Display client IP:port on connection
2. Display received message length
3. Build response: `b"OK: " + message.upper()`
4. Send response with `sendall()`

**Test**:
```bash
# Terminal 1: server
python3 seminar/python/templates/tcp_server_template.py

# Terminal 2: client
echo "test message" | nc 127.0.0.1 12345
# Expected: OK: TEST MESSAGE
```

#### Activity 4.2: UDP server Template

**File**: `seminar/python/templates/udp_server_template.py`

**Requirements to complete**:
1. Decode message (bytes → string with `.decode('utf-8')`)
2. Implement protocol:
   - `ping` → `PONG`
   - `upper:text` → `TEXT` (uppercase)
   - other → `UNKNOWN COMMAND`
3. Logging with timestamp and client address

**Test**:
```bash
# Terminal 1: server
python3 seminar/python/templates/udp_server_template.py

# Terminal 2: client
echo "ping" | nc -u 127.0.0.1 12345
# Expected: PONG
```

---

### PHASE 5: Optional Extension – L3 Router (15 minutes)

#### Activity 5.1: Topology with Two Subnets

**Exit and cleanup**:
```
mininet> exit
```
```bash
sudo mn -c
```

**Start extended topology**:
```bash
make mininet-extended
# or:
sudo python3 seminar/mininet/topologies/topo_2_extended.py --cli
```

**Topology**:
- Subnet 1: h1 (10.0.1.1), h2 (10.0.1.2), gateway 10.0.1.254
- Subnet 2: h3 (10.0.2.3), h4 (10.0.2.4), gateway 10.0.2.254
- Router r1: 10.0.1.254 ↔ 10.0.2.254

#### Activity 5.2: Communication Test Between Subnets

```
mininet> h1 ping -c 2 10.0.2.3
PING 10.0.2.3 (10.0.2.3) 56(84) bytes of data.
64 bytes from 10.0.2.3: icmp_seq=1 ttl=63 time=0.5 ms
...

mininet> h1 traceroute -n 10.0.2.3
traceroute to 10.0.2.3, 30 hops max
 1  10.0.1.254  0.1 ms
 2  10.0.2.3    0.2 ms
```

**Observation**: TTL decreases by 1 at each hop through the router.

#### Activity 5.3: TCP server Between Subnets

```
mininet> h1 python3 -u seminar/python/exercises/ex_2_01_tcp.py server --bind 10.0.1.1 --port 9090 &
mininet> h3 python3 seminar/python/exercises/ex_2_01_tcp.py client --host 10.0.1.1 --port 9090 --message "across router"
```

**Questions**:
- What is the packet route from h3 to h1?
- What role does the router play in OSI terms? (L3 – Network)

---

### PHASE 6: Finalisation (5 minutes)

#### Environment Cleanup
```
mininet> exit
```
```bash
sudo mn -c
make clean
```

#### Deliverables for Student

1. **Text file** with:
   - Commands executed
   - 3 observations about the difference between TCP vs UDP

2. **PCAP captures**:
   - `tcp_demo.pcap`
   - `udp_demo.pcap`

3. **tshark commands** used for analysis

---

## Layer Mapping – Quick Reference

| Observable in capture | OSI Layer | TCP/IP Layer | tshark field |
|-----------------------|-----------|--------------|--------------|
| MAC Address | L2 | Network Access | `eth.src`, `eth.dst` |
| IP Address | L3 | Internet | `ip.src`, `ip.dst` |
| TTL | L3 | Internet | `ip.ttl` |
| port | L4 | Transport | `tcp.srcport`, `udp.dstport` |
| TCP Flags | L4 | Transport | `tcp.flags`, `tcp.flags.str` |
| Payload | L7 | Application | `tcp.payload`, `data.data` |

---

## Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `Address already in use` | port occupied | `pkill -f ex_2_01` or change port |
| `Connection refused` | server stopped | Check `jobs`, restart |
| Empty capture | Wrong filter | Check interface and port |
| `mn: command not found` | Mininet missing | `sudo apt-get install mininet` |
| Mininet crash | Previous session | `sudo mn -c` |
| `Permission denied` tcpdump | Missing sudo | Run with `sudo` |

---

## Formative Evaluation Criteria

| Level | Score | Requirements |
|-------|-------|--------------|
| **Minimum** | 5-6 | Run TCP and UDP server/client, basic capture, identify handshake |
| **Medium** | 7-8 | Functional completed templates, detailed analysis with tshark, explain TCP/UDP differences |
| **Advanced** | 9-10 | Functional extended topology, complete layer correlation, documentation |

---

*Revolvix&Hypotheticalandrei*
