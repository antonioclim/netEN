# Lecture 8 – Transport Layer
## TCP, UDP, TLS, QUIC

---

## Objectives

At the end of the lecture, the student will be able to:

- Explain the role of the transport layer in network architecture
- Describe the port mechanism and process multiplexing
- Detail TCP protocol operation (handshake, flow control, reliability)
- Compare TCP and UDP from the application requirements perspective
- Understand the role of TLS/DTLS in securing transport
- Appreciate the motivation for QUIC emergence and its impact on HTTP/3

---

## 1. The Role of the Transport Layer

### Position in the TCP/IP Stack

```
┌─────────────────────────────┐
│       Application           │ ← HTTP, FTP, DNS, SMTP...
├─────────────────────────────┤
│       Transport             │ ← TCP, UDP (this lecture)
├─────────────────────────────┤
│       Network (Internet)    │ ← IP, ICMP, routing
├─────────────────────────────┤
│       Data Link             │ ← Ethernet, Wi-Fi
├─────────────────────────────┤
│       Physical              │ ← Cable, radio waves
└─────────────────────────────┘
```

### Main Functions

1. **Process identification** – the port mechanism
2. **Communication multiplexing** – multiple applications on the same host
3. **Flow control** – adapting to receiver capacity
4. **Reliability** (optional) – guaranteeing delivery and order

---

## 2. The Port Mechanism

### What is a port?

- Numeric identifier (16 bits): 0–65535
- Identifies one end of communication (process/service)
- **5-tuple** uniquely defines a connection:
  - Source IP, Source Port, Destination IP, Destination Port, Protocol

### Port Classification

| Range | Type | Examples |
|-------|------|----------|
| 0–1023 | Well-known | HTTP (80), HTTPS (443), SSH (22), FTP (21) |
| 1024–49151 | Registered | MySQL (3306), PostgreSQL (5432) |
| 49152–65535 | Ephemeral | Client ports (dynamically allocated) |

### Client vs Server

- **Server**: listens on a **fixed** port (e.g. 80 for HTTP)
- **Client**: uses an **ephemeral** port (allocated by the OS)

---

## 3. The TCP Protocol

### Fundamental Characteristics

- **Connection-oriented** – requires handshake before transfer
- **Reliable** – guarantees delivery and order
- **Byte stream** – no concept of "message"
- **Full-duplex** – simultaneous bidirectional communication

### The TCP Header (20+ bytes)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
├─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┤
│          Source Port          │       Destination Port        │
├───────────────────────────────┴───────────────────────────────┤
│                        Sequence Number                        │
├───────────────────────────────────────────────────────────────┤
│                    Acknowledgment Number                      │
├───────┬───────┬─┬─┬─┬─┬─┬─┬───────────────────────────────────┤
│  Off  │ Res   │U│A│P│R│S│F│            Window                 │
│       │       │R│C│S│S│Y│I│                                   │
│       │       │G│K│H│T│N│N│                                   │
├───────┴───────┴─┴─┴─┴─┴─┴─┴───────────────────────────────────┤
│           Checksum            │         Urgent Pointer        │
├───────────────────────────────┴───────────────────────────────┤
│                    Options (if any)                           │
└───────────────────────────────────────────────────────────────┘
```

### TCP Flags

| Flag | Name | Role |
|------|------|------|
| SYN | Synchronize | Connection initiation |
| ACK | Acknowledge | Receipt confirmation |
| FIN | Finish | Controlled closure |
| RST | Reset | Forced closure/error |
| PSH | Push | Immediate delivery to application |
| URG | Urgent | Priority data |

---

## 4. Three-Way Handshake

### Establishing TCP Connection

```
Client                                Server
   │                                     │
   │ ─────── SYN, Seq=x ──────────────→  │
   │         (1. Connection request)     │
   │                                     │
   │ ←────── SYN-ACK, Seq=y, Ack=x+1 ──  │
   │         (2. Acceptance + ISN)       │
   │                                     │
   │ ─────── ACK, Seq=x+1, Ack=y+1 ───→  │
   │         (3. Final confirmation)     │
   │                                     │
   │ ═══════ ESTABLISHED ════════════════│
```

### Why three steps?

1. **ISN synchronisation** (Initial Sequence Number) – both parties communicate their initial sequence number
2. **Old packet prevention** – avoids confusion with previous connections
3. **Bidirectional confirmation** – both parties know the other is active

---

## 5. TCP Connection Termination

### Four-Way Termination

```
Client                                Server
   │                                     │
   │ ─────── FIN, Seq=u ──────────────→  │
   │         (1. I want to close)        │
   │                                     │
   │ ←────── ACK, Ack=u+1 ────────────── │
   │         (2. OK, received)           │
   │                                     │
   │ ←────── FIN, Seq=v ──────────────── │
   │         (3. I want to close too)    │
   │                                     │
   │ ─────── ACK, Ack=v+1 ─────────────→ │
   │         (4. Final confirmation)     │
   │                                     │
   │          TIME_WAIT (2×MSL)          │
   │                                     │
```

### TCP Socket States

- LISTEN → SYN_RECEIVED → ESTABLISHED
- ESTABLISHED → FIN_WAIT_1 → FIN_WAIT_2 → TIME_WAIT → CLOSED
- ESTABLISHED → CLOSE_WAIT → LAST_ACK → CLOSED

---

## 6. TCP Options

### MSS (Maximum Segment Size)

- Maximum data size in a segment
- MSS + TCP header + IP header ≤ MTU
- Negotiated in SYN (avoids IP fragmentation)

### SACK (Selective Acknowledgment)

- Classic TCP: cumulative ACK (only "received up to X")
- SACK: allows acknowledgment of discontinuous ranges
- **Reduces unnecessary retransmissions**

### Window Scaling

- Window field in header: 16 bits (max 65535)
- Window scaling: multiplication factor (negotiated in SYN)
- Allows windows of millions of bytes (needed for fast networks)

### TCP Timestamps

- Precise RTT (Round-Trip Time) estimation
- PAWS (Protection Against Wrapped Sequences)

---

## 7. The UDP Protocol

### Characteristics

- **Connectionless** – no handshake exists
- **Best-effort** – no delivery guarantees
- **Datagrams** – each message is independent
- **Minimal overhead** – only 8 bytes header

### The UDP Header

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
├─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┤
│          Source Port          │       Destination Port        │
├───────────────────────────────┼───────────────────────────────┤
│            Length             │           Checksum            │
├───────────────────────────────┴───────────────────────────────┤
│                            Data ...                           │
└───────────────────────────────────────────────────────────────┘
```

### When is UDP used?

- **DNS** – short queries, fast responses
- **DHCP** – bootstrap, no connection exists
- **Streaming** – loss tolerance, minimal latency
- **Gaming** – current state more important than history
- **VoIP** – real-time, losing a packet < delay

---

## 8. TCP vs UDP – Comparison

| Aspect | TCP | UDP |
|--------|-----|-----|
| Connection | Connection-oriented | Connectionless |
| Reliability | Guaranteed | Best-effort |
| Order | Preserved | Not guaranteed |
| Flow control | Yes (window) | No |
| Overhead | 20+ bytes header | 8 bytes header |
| Setup latency | 1 RTT (handshake) | 0 |
| Transfer unit | Stream (bytes) | Datagrams (messages) |
| Usage | HTTP, FTP, email | DNS, VoIP, gaming |

---

## 9. TLS (Transport Layer Security)

### Why TLS?

- TCP and UDP transmit data **in clear text**
- Anyone on the route can intercept and read the traffic
- TLS provides: **confidentiality**, **integrity**, **authentication**

### Position in Stack

```
┌─────────────────────────────┐
│       Application           │
├─────────────────────────────┤
│       TLS/SSL               │ ← Encryption (this layer)
├─────────────────────────────┤
│       TCP                   │
└─────────────────────────────┘
```

### TLS 1.3 – Improvements

- **1-RTT handshake** (vs 2-RTT in TLS 1.2)
- **0-RTT** for repeated connections
- Deprecated algorithms removed
- Mandatory forward secrecy

### Simplified TLS 1.3 Handshake

```
Client                                Server
   │                                     │
   │ ─── ClientHello + KeyShare ──────→  │
   │                                     │
   │ ←── ServerHello + KeyShare ──────── │
   │ ←── {EncryptedExtensions} ───────── │
   │ ←── {Certificate} ───────────────── │
   │ ←── {CertificateVerify} ──────────  │
   │ ←── {Finished} ──────────────────── │
   │                                     │
   │ ─── {Finished} ──────────────────→  │
   │                                     │
   │ ═══ Application Data (encrypted) ═══│
```

---

## 10. QUIC and HTTP/3

### Why QUIC?

- **Head-of-line blocking** in TCP: one lost packet blocks everything
- **Combined handshake**: connection + encryption in 1-RTT
- **0-RTT** for repeated connections
- **Connection migration**: IP/port change without reconnection

### QUIC Architecture

```
┌─────────────────────────────┐
│       HTTP/3                │
├─────────────────────────────┤
│       QUIC                  │ ← Combines TCP + TLS
├─────────────────────────────┤
│       UDP                   │
└─────────────────────────────┘
```

### QUIC vs TCP+TLS

| Aspect | TCP + TLS | QUIC |
|--------|-----------|------|
| Handshake | 2-3 RTT | 1 RTT (0-RTT repeat) |
| Multiplexing | HOL blocking | Independent streams |
| Encryption | Clear text header | Encrypted header |
| Migration | Reconnection | Connection ID |

---

## 11. Summary

### Key Concepts

1. **Transport layer** – bridges network and application
2. **Ports** – identify processes, enable multiplexing
3. **TCP** – reliable, connection-oriented, complex
4. **UDP** – fast, simple, no guarantees
5. **TLS** – secures transport (encryption, authentication)
6. **QUIC** – modern evolution, combines TCP+TLS advantages over UDP

### Review Questions

1. Why does TCP need a three-way handshake?
2. What problem does SACK solve?
3. When would an application use UDP instead of TCP?
4. What does TLS provide that TCP does not?
5. Why does QUIC run over UDP and not directly over IP?

---

## Bibliography

- Kurose, J., Ross, K. (2021). *Computer Networking: A Top-Down Approach*. Ch. 3
- RFC 793 – TCP
- RFC 768 – UDP
- RFC 8446 – TLS 1.3
- RFC 9000 – QUIC

---

*Material for Computer Networks, ASE Bucharest, 2025*
