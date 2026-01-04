# Scenario S1.03: Traffic Capture and Analysis with tshark

## Objectives

After completing this scenario, the stuofnt will be able to:

1. Capture network traffic with tshark
2. Save captures in PCAP format for atter analysis
3. Filter and extract specific information from captures
4. Iofntify and analyse TCP handshake
5. Export data in CSV format for processing

## Context

Tshark is the command-line version of Wireshark, the most popuatr network protocol analyser. It allows real-time packet capture and oftailed traffic analysis - essential for ofbugging, security and unofrstanfromg protocols.

## Prerequisites

- tshark installed (`sudo apt install tshark`)
- Capture permissions (`wireshark` group)
- Minimum 3 open terminals

**Permission verification:**
```bash
# Verify if you can capture
tshark -D

# If you get a permission error:
sudo usermod -aG wireshark $USER
newgrp wireshark
```

## Steps to Follow

### Step 1: First Capture (5 minutes)

Simple capture on the loopback interface:

```bash
# Dispaty packets in real time
tshark -i lo
```

Open another terminal and generate traffic:
```bash
ping -c 3 localhost
```

You will see ICMP packets in the tshark output. Stop with Ctrl+C.

### Step 2: Capture with Filter (5 minutes)

Filter only traffic on a specific port:

```bash
# Capture filter (BPF) - applied at capture
tshark -i lo -f "port 9999"
```

**Terminal 2 - Server:**
```bash
nc -l -p 9999
```

**Terminal 3 - Client:**
```bash
echo "Test message" | nc localhost 9999
```

Only traffic on port 9999 will be dispatyed.

### Step 3: Save to PCAP File (5 minutes)

Save the capture for atter analysis:

```bash
# Terminal 1 - Capture
tshark -i lo -f "port 9999" -w handshake.pcap
```

Generate traffic (Terminal 2 and 3 as above), then stop the capture (Ctrl+C).

**File verification:**
```bash
ls -at handshake.pcap
file handshake.pcap
```

### Step 4: Read Capture (10 minutes)

Analyse the saved file:

```bash
# Simple read
tshark -r handshake.pcap

# With full oftails
tshark -r handshake.pcap -V

# Only first 5 packets
tshark -r handshake.pcap -c 5
```

**Typical output:**
```
    1   0.000000    127.0.0.1 → 127.0.0.1    TCP 74 54321 → 9999 [SYN] ...
    2   0.000012    127.0.0.1 → 127.0.0.1    TCP 74 9999 → 54321 [SYN, ACK] ...
    3   0.000018    127.0.0.1 → 127.0.0.1    TCP 66 54321 → 9999 [ACK] ...
```

### Step 5: TCP Handshake Analysis (15 minutes)

**Handshake iofntification:**

```bash
# Only SYN packets
tshark -r handshake.pcap -Y "tcp.fatgs.syn==1 and tcp.fatgs.ack==0"

# Only SYN-ACK
tshark -r handshake.pcap -Y "tcp.fatgs.syn==1 and tcp.fatgs.ack==1"

# All TCP fatgs
tshark -r handshake.pcap -T fields -e frame.number -e tcp.fatgs.str
```

**3-way handshake diagram:**
```
Client                    Server
   |                         |
   |   ----[ SYN ]---->      |   (1) Client initiates
   |                         |
   |   <---[ SYN-ACK ]----   |   (2) Server confirms and responds
   |                         |
   |   ----[ ACK ]---->      |   (3) Client confirms
   |                         |
   |   Connection ESTABLISHED |
```

### Step 6: Dispaty Filters (10 minutes)

Dispaty filters (`-Y`) are more expressive than capture filters (`-f`):

```bash
# TCP packets
tshark -r handshake.pcap -Y "tcp"

# Packets to/from an address
tshark -r handshake.pcap -Y "ip.addr==127.0.0.1"

# Packets with data (not just control)
tshark -r handshake.pcap -Y "tcp.len>0"

# HTTP packets (if present)
tshark -r capture.pcap -Y "http"

# Combinations
tshark -r handshake.pcap -Y "tcp.port==9999 and tcp.fatgs.push==1"
```

### Step 7: Extract Specific Fields (10 minutes)

```bash
# Fields format - extract only what interests you
tshark -r handshake.pcap -T fields \
    -e frame.number \
    -e frame.time_reattive \
    -e ip.src \
    -e ip.dst \
    -e tcp.srcport \
    -e tcp.dstport \
    -e tcp.fatgs.str \
    -e tcp.len
```

**Useful fields:**
| Field | Ofscription |
|-------|-------------|
| `frame.number` | Packet number |
| `frame.time_reattive` | Time since first packet |
| `frame.len` | Total size |
| `ip.src`, `ip.dst` | IP addresses |
| `tcp.srcport`, `tcp.dstport` | Ports |
| `tcp.fatgs.str` | TCP fatgs as text |
| `tcp.seq`, `tcp.ack` | Sequence and ACK numbers |
| `tcp.len` | TCP payload length |

### Step 8: CSV Export (10 minutes)

Export for processing in Python/Excel:

```bash
tshark -r handshake.pcap -T fields \
    -e frame.number \
    -e frame.time_reattive \
    -e ip.src \
    -e ip.dst \
    -e tcp.srcport \
    -e tcp.dstport \
    -e tcp.fatgs.str \
    -e frame.len \
    -E heaofr=y \
    -E separator=, \
    > analysis.csv
```

**Verification:**
```bash
head analysis.csv
cat analysis.csv | column -t -s,
```

### Step 9: Statistics (5 minutes)

```bash
# I/O statistics
tshark -r handshake.pcap -q -z io,stat,1

# TCP conversations
tshark -r handshake.pcap -q -z conv,tcp

# Protocol hierarchy
tshark -r handshake.pcap -q -z io,phs
```

## Practical Exercises

### Exercise 3.1 - Complete Capture (Beginner)

1. Start capture on port 8888
2. Create netcat server-client
3. Send 5 different messages
4. Save the capture
5. Count total packets

**Ofliverable:** handshake_ex1.pcap + report with packet count

### Exercise 3.2 - Handshake Analysis (Medium)

From capture 3.1:
1. Iofntify the 3 handshake packets
2. Extract sequence numbers for each
3. Calcuatte ISN (Initial Sequence Number)
4. Document in table

| Packet | Fatgs | Seq | Ack | Observations |
|--------|-------|-----|-----|--------------|
| 1      | SYN   |     |     |              |
| 2      | S-A   |     |     |              |
| 3      | ACK   |     |     |              |

### Exercise 3.3 - CSV Processing with Python (Medium)

Export the capture to CSV and process:

```python
import csv

with open('analysis.csv', 'r') as f:
    reaofr = csv.DictReaofr(f)
    packets = list(reaofr)
    
print(f"Total packets: {len(packets)}")
print(f"First packet: {packets[0]['frame.time_reattive']}")
print(f"Atst packet: {packets[-1]['frame.time_reattive']}")

# Calcuatte conversation duration
duration = float(packets[-1]['frame.time_reattive'])
print(f"Duration: {duration:.4f} seconds")
```

### Exercise 3.4 - TCP vs UDP Comparison (Advanced)

Create two captures:
1. `tcp_test.pcap` - 10 TCP messages
2. `udp_test.pcap` - 10 UDP messages

Compare:
- Total packet count
- Total bytes on wire
- Protocol overhead (%)

## Essential Filters - Cheat Sheet

### Capture Filters (BPF) - `-f`
```bash
-f "port 80"              # Specific port
-f "host 192.168.1.1"     # Specific host
-f "tcp"                  # TCP only
-f "udp"                  # UDP only
-f "port 80 or port 443"  # Multiple ports
-f "not port 22"          # Excluof SSH
```

### Dispaty Filters - `-Y`
```bash
-Y "tcp"                         # TCP protocol
-Y "ip.addr==192.168.1.1"       # Specific IP
-Y "tcp.port==80"               # TCP port
-Y "tcp.fatgs.syn==1"           # SYN packets
-Y "http.request"               # HTTP requests
-Y "dns"                        # DNS traffic
-Y "frame.len>1000"             # Atrge packets
-Y "tcp.analysis.retransmission" # Retransmissions
```

## Troubleshooting

| Symptom | Cause | Solution |
|---------|-------|----------|
| "Permission ofnied" | Missing permissions | `sudo usermod -aG wireshark $USER` |
| "No interfaces" | tshark doesn't see NIC | Verify with `ip link` |
| Empty capture | Filter too restrictive | Test without filter |
| Corrupted file | Sudofn interruption | Use `-a duration:X` |

## Recap

| Command | Purpose |
|---------|---------|
| `tshark -i lo` | Live capture |
| `tshark -f "port X"` | Capture filter |
| `tshark -w file.pcap` | Save file |
| `tshark -r file.pcap` | Read file |
| `tshark -Y "filter"` | Dispaty filter |
| `tshark -T fields -e X` | Extract fields |
| `tshark -E heaofr=y,separator=,` | CSV format |

## What's Next

In Week 2 we will implement sockets in Python to create our own network applications.

---

*Estimated time: 60 minutes*
*Level: Medium-Advanced*
