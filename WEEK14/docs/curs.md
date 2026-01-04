# Lecture 14 — Integrated Review

**Course:** Computer Networks / Networking  
**Week:** 14 (final)  
**Duration:** 90 minutes

---

## What We Will Learn

Week 14 consolidates all concepts from the semester into a coherent mental model. We do not memorise lists of protocols, but rather practise a **reproducible diagnostic process**: from symptom to probable cause, with verifiable evidence (captures, logs, measurements).

### Operational Objectives

At the end of the lecture, the student can:

1. **Reconstruct the complete path** of a message: application → socket → TCP/UDP → IP → Ethernet/ARP (and reverse)
2. **Apply a diagnostic checklist** in logical order: L3 connectivity → ports → capture → application
3. **Interpret a pcap capture** and correlate the symptom with the cause (timeout vs RST, retransmissions, HTTP codes)
4. **Justify technical decisions** in a project presentation

---

## Why It Matters (for Programmers)

Network defects manifest as application bugs: inexplicable timeouts, intermittent errors, unstable performance. A programmer who understands the layer beneath the socket API can:

- **Reduce debugging time** from hours to minutes
- **Communicate efficiently** with DevOps/Infra teams using precise terms
- **Build more robust services** (correct timeouts, retry with backoff, health checks)

### Concrete Examples

| Application Symptom | Real Cause | How It Shows |
|---------------------|------------|--------------|
| `Connection timeout` | Firewall blocks SYN | pcap: SYN without SYN-ACK |
| `Connection refused` | Port not listening | ss: not in LISTEN |
| `504 Gateway Timeout` | Slow/down backend | LB log + pcap to backend |
| Variable latency | TCP retransmissions | pcap: duplicate packets |

---

## Review: Concept Map

### 1. Layers and Encapsulation

```
Application  → [Data]
Transport    → [TCP/UDP Header | Data] = Segment/Datagram
Network      → [IP Header | Segment]   = Packet
Link         → [Eth Header | Packet]   = Frame
```

**Check question:** What overhead does each layer introduce? (Ethernet: 14B, IP: 20B+, TCP: 20B+)

### 2. Addressing by Levels

| Level | Address | Purpose | Resolution |
|-------|---------|---------|------------|
| Link (2) | MAC (48 bits) | LAN identification | ARP |
| Network (3) | IP (32/128 bits) | Global identification | DNS, routing |
| Transport (4) | Port (16 bits) | Process identification | Application |

**Check question:** Why do you need ARP before sending a ping?

### 3. TCP vs UDP

| Characteristic | TCP | UDP |
|----------------|-----|-----|
| Connection | Yes (3-way handshake) | No |
| Reliability | Guaranteed (retransmissions) | Best-effort |
| Ordering | Guaranteed | No |
| Flow control | Yes (window) | No |
| Overhead | Higher | Lower |
| Usage | HTTP, SSH, FTP | DNS, VoIP, gaming |

**Check question:** What does an RST mean in a TCP capture?

### 4. Routing

- **Routing table:** list of rules (destination, mask, next-hop, interface)
- **Longest Prefix Match:** the most specific route is chosen
- **Default gateway:** route 0.0.0.0/0 when no better match exists

```bash
ip route
# Example output:
# default via 192.168.1.1 dev eth0
# 10.0.0.0/24 dev mininet-h1 scope link
```

### 5. HTTP (Layer 7)

```
Request:  GET /path HTTP/1.1\r\nHost: example.com\r\n\r\n
Response: HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html>...
```

**Important codes:** 200 OK, 301/302 Redirect, 404 Not Found, 500/502/503/504 Server Errors

---

## Diagnostic Checklist

When something "does not work", apply in order:

```
1. Minimal reproduction
   └─ Same request, same topology, same version?

2. L3 Connectivity
   └─ ping <ip>
   └─ ip route get <ip>
   └─ ip neigh (ARP cache)

3. Ports and sockets
   └─ ss -lntp (what is listening?)
   └─ ss -tnp (active connections)

4. Capture at boundary
   └─ tcpdump -i <iface> host <ip> -w capture.pcap
   └─ tshark -r capture.pcap -Y "tcp.port==80"

5. Interpretation
   └─ Complete handshake? Retransmissions? RST? HTTP codes?

6. Remediation + validation
   └─ Small change → measurement → comparison
```

---

## Recommended Demonstrations

### Demo 1: TCP Handshake vs Timeout (5 min)

```bash
# Terminal 1: simple server
python3 -m http.server 8000

# Terminal 2: capture
sudo tcpdump -i lo port 8000 -nn

# Terminal 3: client
curl http://localhost:8000/

# Observe: SYN → SYN-ACK → ACK → GET → 200 OK → FIN
```

### Demo 2: Connection Refused vs Timeout (5 min)

```bash
# Closed port (immediately refused)
curl http://localhost:9999/
# → Connection refused (immediate RST)

# Filtered port (timeout)
sudo iptables -A INPUT -p tcp --dport 8888 -j DROP
curl --connect-timeout 3 http://localhost:8888/
# → Timeout (SYN without response)
```

### Demo 3: DNS as a Failure Point (5 min)

```bash
# With working DNS
curl http://example.com/

# With broken DNS
echo "nameserver 1.2.3.4" | sudo tee /etc/resolv.conf
curl http://example.com/
# → DNS resolution failed

# With direct IP (bypasses DNS)
curl http://93.184.216.34/
# → Works
```

---

## Typical Mistakes

| Mistake | Consequence | How to Avoid |
|---------|-------------|--------------|
| IP vs Port confusion | "Does not respond on 10.0.0.2:8080" | Check `ss -lntp` on host |
| Ping OK = Service OK | Service may be down | Test with `curl`/client |
| Ignoring retransmissions | Congestion/loss not noticed | Analyse pcap in detail |
| Forgotten firewall | Mysteriously blocked traffic | `iptables -L -n` |
| DNS cache | Changes do not propagate | `dig +short` or `nslookup` |

---

## What We Learned / How It Helps

Week 14 does not add new concepts, but rather **integrates** them into a working process. Practical value:

1. **Faster debugging:** you know where to look first
2. **Precise communication:** you use correct terms (SYN, RST, 502)
3. **More robust services:** you set informed timeouts and retries
4. **Industry preparation:** technical interviews test exactly these skills

---

## Connection to the Team Project

In the project presentation, you demonstrate:

- **Reproducibility:** you start from a clean environment, clear steps
- **Evidence:** pcap capture that supports a technical claim
- **Diagnostic:** you can explain a symptom (what do we see?) and cause (why?)
- **Justification:** why you chose TCP/UDP, ports, architecture

---

## Bibliography

- Kurose, J. F., & Ross, K. W. (2017). *Computer Networking: A Top-Down Approach* (7th ed.). Pearson.
- Stevens, W. R. (1994). *TCP/IP Illustrated, Volume 1*. Addison-Wesley.
- RFC 791 (IP), RFC 793 (TCP), RFC 768 (UDP)
