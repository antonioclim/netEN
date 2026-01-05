# Lecture 9 — Session Layer (L5) and Presentation Layer (L6)

## What We Will Learn

Week 9 explores the two intermediate layers of the OSI model that ensure **logical communication continuity** (session) and **uniform data representation** (presentation). Although in the TCP/IP stack these functions are often absorbed by the application layer, understanding them separately provides a fundamental perspective on how distributed applications maintain conversational state and negotiate data formats.

**Concrete objectives:**
1. Differentiating between connection (L4) and session (L5)
2. Implementing authentication, checkpoint and resumption mechanisms
3. Understanding data transformations: serialisation, compression, encryption
4. Building a multi-command text protocol (pseudo-FTP)
5. Analysing FTP traffic with Wireshark/tshark

---

## Why It Matters

In a distributed environment, connection losses are inevitable. The session layer provides **save points** (checkpoints) and mechanisms for **resuming from the point of interruption** — essential for large file transfers or complex transactions. The presentation layer ensures that data sent by a big-endian system is correctly interpreted by a little-endian one, that UTF-8 text arrives intact, and that sensitive information can be transparently encrypted.

For a programmer, these concepts manifest in:
- **Session tokens** (JWT, session cookies)
- **Serialisation** (JSON, Protocol Buffers, MessagePack)
- **Compression** (gzip, zlib, brotli)
- **TLS/SSL** (end-to-end encryption)

---

## Prerequisites

| Week | Required Concept |
|------|------------------|
| W4 | IP addressing, subnetting |
| W8 | TCP handshake, segmentation, retransmission |
| W3 | Basic socket programming |

**Ultra-brief recap:** TCP provides a reliable byte stream between two endpoints. But TCP knows nothing about user "sessions", authentication, or data format — these are the responsibility of higher layers.

---

## 1. Session Layer (L5 OSI)

### 1.1 Role and Responsibilities

The session layer manages the **dialogue** between applications:

| Function | Description |
|----------|-------------|
| **Session establishment** | Parameter initialisation, authentication |
| **Synchronisation** | Checkpoints for resumption |
| **Dialogue control** | Half-duplex vs full-duplex |
| **Termination** | Graceful closure with confirmation |

### 1.2 Connection vs Session

```
TCP CONNECTION (L4)         SESSION (L5)
─────────────────           ─────────────
IP:port ↔ IP:port           User_A ↔ User_B
Byte stream                 Semantic context
Semantically stateless      Stateful (auth, history)
Timeout: system             Timeout: application
```

**Practical example:** A user connects to an FTP server. The TCP connection is established (L4). Then the user authenticates (USER/PASS) — this creates a **session**. If the connection is lost, a reconnection requires re-authentication to restore the session.

### 1.3 Synchronisation and Checkpoints

In file transfer protocols, synchronisation points allow:
- Resuming transfer from the last confirmed position
- Partial integrity verification (CRC on blocks)
- Rollback in case of error

```python
# Pseudo-code: checkpoint in transfer
def transfer_with_checkpoints(file, block_size=8192):
    checkpoint = 0
    while True:
        block = file.read(block_size)
        if not block:
            break
        send_block(block, seq=checkpoint)
        ack = wait_ack()
        if ack.seq == checkpoint:
            checkpoint += 1
            save_checkpoint(checkpoint)
```

### 1.4 Dialogue Modes

| Mode | Description | Example |
|------|-------------|---------|
| Simplex | Unidirectional | Video streaming |
| Half-duplex | Alternating | Walkie-talkie, HTTP/1.0 |
| Full-duplex | Simultaneous | Telnet, SSH, WebSocket |

---

## 2. Presentation Layer (L6 OSI)

### 2.1 Role and Responsibilities

The presentation layer handles data **syntax**:

| Function | Description |
|----------|-------------|
| **Serialisation** | Converting structures → bytes |
| **Translation** | Big-endian ↔ little-endian |
| **Compression** | Size reduction |
| **Encryption** | Confidentiality |

### 2.2 The Byte Order Problem (Endianness)

```
Value: 0x12345678 (hex)

Big-endian (network byte order):
┌──────┬──────┬──────┬──────┐
│  12  │  34  │  56  │  78  │
└──────┴──────┴──────┴──────┘
Address: 0      1      2      3

Little-endian (x86):
┌──────┬──────┬──────┬──────┐
│  78  │  56  │  34  │  12  │
└──────┴──────┴──────┴──────┘
Address: 0      1      2      3
```

**Golden rule:** Network protocols use **network byte order** (big-endian). The functions `htons()`, `htonl()`, `ntohs()`, `ntohl()` ensure the necessary conversions.

### 2.3 Serialisation: From Structure to Bytes

```python
import struct

# Binary header serialisation
def pack_header(magic, version, length, checksum):
    # >: big-endian, I: unsigned int (4B), H: unsigned short (2B)
    return struct.pack('>IIHH', magic, version, length, checksum)

# Deserialisation
def unpack_header(data):
    magic, version, length, checksum = struct.unpack('>IIHH', data[:12])
    return {'magic': magic, 'version': version, 
            'length': length, 'checksum': checksum}
```

### 2.4 Transparent Compression

```python
import zlib

def compress_payload(data):
    """Compression with zlib level 6 (speed/ratio balance)"""
    return zlib.compress(data, level=6)

def decompress_payload(compressed):
    return zlib.decompress(compressed)

# Example of gain
original = b"A" * 10000  # 10KB repetitive
compressed = compress_payload(original)
ratio = len(original) / len(compressed)
print(f"Compression ratio: {ratio:.1f}x")  # ~1000x for repetitive data
```

### 2.5 Encryption at Presentation Level

In TLS/SSL, the presentation layer encrypts data before transmission:

```
Application: "GET /index.html HTTP/1.1"
     ↓
Presentation (TLS): [encrypted_blob]
     ↓
Transport (TCP): segments with encrypted blob
```

---

## 3. FTP — Integrated Case Study

File Transfer Protocol clearly demonstrates L5/L6 separation:

### 3.1 FTP Architecture

```
┌─────────────────────────────────────────────────┐
│                   FTP CLIENT                     │
├────────────────────┬────────────────────────────┤
│   User Interface   │      Protocol Engine       │
├────────────────────┴────────────────────────────┤
│  Control Connection (port 21)    Data Connection │
│  ─────────────────────────       (port 20/dyn)  │
│  Text commands: USER, PASS,      Binary/ASCII   │
│  CWD, LIST, RETR, STOR, QUIT     transfer       │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│                   FTP SERVER                     │
├────────────────────┬────────────────────────────┤
│  Command Handler   │       File System          │
└────────────────────┴────────────────────────────┘
```

### 3.2 FTP Session (L5)

```
Client                          Server
   │                               │
   │───── TCP SYN ────────────────▶│
   │◀──── TCP SYN-ACK ────────────│
   │───── TCP ACK ────────────────▶│  ← Connection (L4)
   │                               │
   │◀──── 220 Welcome ────────────│
   │───── USER alice ─────────────▶│
   │◀──── 331 Password required ──│
   │───── PASS secret ────────────▶│
   │◀──── 230 Logged in ──────────│  ← Session (L5) established
   │                               │
   │───── PWD ────────────────────▶│
   │◀──── 257 "/" ────────────────│
   │                               │
   │───── QUIT ───────────────────▶│
   │◀──── 221 Goodbye ────────────│  ← Session closed
```

### 3.3 Transfer Modes (L6)

| Mode | Code | Usage |
|------|------|-------|
| ASCII | TYPE A | Text, source code |
| Binary | TYPE I | Executables, images |

```
# TYPE command in FTP
TYPE A  → Line endings conversion (CR LF ↔ LF)
TYPE I  → Byte-by-byte transfer, no modifications
```

### 3.4 Data Connection Modes

| Mode | Initiator | Firewall-friendly |
|------|-----------|-------------------|
| Active | Server → Client:20 | ✗ |
| Passive | Client → Server:dyn | ✓ |

---

## 4. Practical Implementation: Pseudo-FTP Server

Week 9 includes implementing a simplified server that demonstrates:
- Text command-response protocol
- Session-based authentication
- Binary transfer with CRC
- Multi-client via threading/async

**Supported commands:**

| Command | Syntax | Description |
|---------|--------|-------------|
| AUTH | `AUTH user pass` | Authentication |
| PWD | `PWD` | Current directory |
| LIST | `LIST [path]` | File listing |
| GET | `GET filename` | Download |
| PUT | `PUT filename size` | Upload |
| QUIT | `QUIT` | Disconnect |

---

## 5. Review Questions

1. **Conceptual:** What is the fundamental difference between a TCP connection and an application session?

2. **Practical:** Why do network protocols use big-endian, not little-endian?

3. **Analysis:** In a Wireshark capture of an FTP session, how do you identify the moment when the session (not the connection) becomes active?

4. **Application:** How would you implement a checkpoint mechanism for resuming an interrupted transfer?

5. **Evaluation:** What are the advantages and disadvantages of compression at the presentation layer vs. at the application layer?

---

## What We Learned

- The **session layer (L5)** manages application-to-application dialogue: authentication, synchronisation, conversational flow control
- The **presentation layer (L6)** ensures data interoperability: serialisation, endianness, compression, encryption
- **FTP** clearly exemplifies the separation: control channel (session) vs. data channel (presentation/transport)
- The `struct.pack/unpack` functions allow building portable binary protocols
- `zlib` offers transparent compression with a simple API

---

## How It Helps Us

| Context | Applicability |
|---------|---------------|
| API Development | JSON/Protobuf serialisation, versioning |
| Security | Understanding TLS handshake |
| Cloud | Distributed sessions, sticky sessions |
| DevOps | File transfer debugging, SFTP/SCP |
| IoT | Efficient binary protocols |

---

## Where It Fits in a Programmer's Education

A competent programmer does not just use network libraries, but **understands what happens at each level**. When a transfer fails, you must be able to identify whether the problem is:
- At the transport level (connection refused, timeout)
- At the session level (invalid authentication, expired session)
- At the presentation level (corrupted data, wrong endianness)

This week builds the **vocabulary** needed for precise diagnosis and efficient solutions.

---

## Selected Bibliography

| Authors | Title | Publication | Year | DOI |
|---------|-------|-------------|------|-----|
| Kurose, Ross | Computer Networking: A Top-Down Approach | Pearson | 2021 | 10.5555/3312469 |
| Tanenbaum, Wetherall | Computer Networks | Pearson | 2011 | 10.5555/1972505 |
| Postel, Reynolds | File Transfer Protocol (FTP) | RFC 959 | 1985 | 10.17487/RFC0959 |
| Stevens, Fenner, Rudoff | UNIX Network Programming Vol.1 | Addison-Wesley | 2004 | 10.5555/1012850 |

## Standards and Specifications

| Document | Description |
|----------|-------------|
| RFC 959 | File Transfer Protocol |
| RFC 4217 | Securing FTP with TLS |
| RFC 2616 | HTTP/1.1 (persistent connections context) |
| ISO/IEC 7498-1 | OSI Basic Reference Model |
| IEEE 754 | Floating-Point Arithmetic (endianness) |
