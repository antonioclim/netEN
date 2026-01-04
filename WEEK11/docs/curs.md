# Lecture 11: Application Protocols – FTP, DNS, SSH

## Overview

**Week**: 11 of 14  
**Duration**: 2 hours lecture  
**Syllabus topic**: Application layer – FTP, DNS, SSH

---

## 1. What We Will Learn

This week we explore three fundamental application layer protocols that support the modern Internet infrastructure:

- **FTP (File Transfer Protocol)** – file transfer between systems
- **DNS (Domain Name System)** – translating names into IP addresses
- **SSH (Secure Shell)** – secure access to remote systems

These protocols illustrate different communication paradigms: FTP uses multiple connections (control + data), DNS operates predominantly over UDP with structured messages and SSH establishes multiplexed encrypted channels.

## 2. Why It Matters

| Protocol | Practical Relevance |
|----------|---------------------|
| **FTP** | Application deployment, backup, data transfer between servers |
| **DNS** | Foundation of web browsing, service discovery, CDN configuration |
| **SSH** | Server administration, secure tunnelling, Git over SSH |

For a programmer or DevOps engineer, understanding these protocols is essential for debugging network problems, configuring infrastructure and developing distributed applications.

---

## 3. Prerequisites

From previous weeks:
- OSI/TCP-IP model (W2)
- TCP/UDP socket programming (W3-W4)
- IP addressing, subnetting (W5-W6)
- Transport layer: TCP, UDP, TLS (W8)
- HTTP and web services (W10)

**Quick recap**: TCP guarantees in-order delivery and flow control, making it suitable for FTP and SSH. UDP offers low latency for simple queries such as DNS.

---

## 4. FTP – File Transfer Protocol

### 4.1 Introduction

FTP is one of the oldest Internet protocols (RFC 959, 1985), designed for efficient file transfer between heterogeneous systems.

**Key characteristics**:
- Operates over TCP
- Uses two separate connections: **control** (port 21) and **data** (port 20 or dynamic)
- Supports authentication (user/password) and anonymous access
- Operates in text mode (ASCII commands) and binary (for files)

### 4.2 FTP Architecture

```
┌─────────────────┐                 ┌─────────────────┐
│     Client      │                 │     Server      │
│                 │                 │                 │
│  ┌───────────┐  │   Control :21   │  ┌───────────┐  │
│  │ Protocol  │◄─┼────────────────►│  │ Protocol  │  │
│  │Interpreter│  │   (commands)    │  │Interpreter│  │
│  └───────────┘  │                 │  └───────────┘  │
│                 │                 │                 │
│  ┌───────────┐  │   Data :20/X    │  ┌───────────┐  │
│  │  Data     │◄─┼────────────────►│  │  Data     │  │
│  │ Transfer  │  │   (files)       │  │ Transfer  │  │
│  └───────────┘  │                 │  └───────────┘  │
│                 │                 │                 │
│  ┌───────────┐  │                 │  ┌───────────┐  │
│  │   File    │  │                 │  │   File    │  │
│  │  System   │  │                 │  │  System   │  │
│  └───────────┘  │                 │  └───────────┘  │
└─────────────────┘                 └─────────────────┘
```

### 4.3 Control Connection

- **Port**: 21 (server listens)
- **Function**: transmitting commands and responses
- **Format**: ASCII text, each command terminated with CRLF
- **Persistence**: remains open for the session duration

**Main commands**:

| Command | Function |
|---------|----------|
| `USER` | Specifies username |
| `PASS` | Specifies password |
| `PWD` | Displays current directory |
| `CWD` | Changes directory |
| `LIST` | Lists directory contents |
| `RETR` | Downloads a file |
| `STOR` | Uploads a file |
| `TYPE` | Sets transfer type (A=ASCII, I=Binary) |
| `PORT` | Specifies address for active mode |
| `PASV` | Requests passive mode |
| `QUIT` | Ends session |

**Response codes** (first 3 digits):

| Code | Meaning |
|------|---------|
| 1xx | Positive preliminary response |
| 2xx | Success |
| 3xx | Intermediate response (continuation expected) |
| 4xx | Temporary error |
| 5xx | Permanent error |

### 4.4 Transfer Modes: Active vs Passive

**Active Mode (PORT)**:
1. Client opens a local port and sends `PORT ip,ip,ip,ip,port_hi,port_lo`
2. Server initiates data connection from port 20 to client port
3. **Problem**: Client firewall may block incoming connections

```
Client                              Server
  │                                   │
  │ ──── PORT 192,168,1,100,200,45 ──►│ (client listens on 51245)
  │                                   │
  │ ◄──── Connection from :20 ────────│ (server initiates connection)
  │                                   │
```

**Passive Mode (PASV)**:
1. Client sends `PASV`
2. Server responds with `227 Entering Passive Mode (ip,ip,ip,ip,port_hi,port_lo)`
3. Client initiates data connection to specified port
4. **Advantage**: Client initiates BOTH connections – works with NAT/firewall

```
Client                              Server
  │                                   │
  │ ────────────── PASV ─────────────►│
  │                                   │
  │ ◄─── 227 (209,51,188,116,234,56) ─│ (server listens on 60024)
  │                                   │
  │ ──── Connection to :60024 ───────►│ (client initiates connection)
  │                                   │
```

### 4.5 Security Considerations

FTP transmits credentials in clear text. Secure alternatives:
- **FTPS** (FTP over TLS) – adds encryption to control and data connections
- **SFTP** (SSH File Transfer Protocol) – completely different protocol, based on SSH
- **SCP** (Secure Copy) – simple transfer via SSH

---

## 5. DNS – Domain Name System

### 5.1 Introduction

DNS translates domain names (e.g.: `www.example.com`) into IP addresses (e.g.: `93.184.216.34`). Without DNS, users would have to memorise numerical addresses.

**Characteristics**:
- Distributed and hierarchical database
- Predominantly uses UDP on port 53 (TCP for zone transfers or large responses)
- Multi-level caching for performance
- Delegation system: each level knows the immediately lower level

### 5.2 DNS Hierarchy

```
                        . (root)
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
       .com              .org              .ro
         │                 │                 │
    ┌────┴────┐           ▼            ┌────┴────┐
    ▼         ▼       wikipedia       ▼         ▼
  google   example                  ase      digi
    │         │                       │
    ▼         ▼                       ▼
   www      mail                    www
```

**Components**:
1. **Root servers** (13 sets, globally replicated) – know TLD servers
2. **TLD servers** (.com, .org, .ro) – know authoritative servers
3. **Authoritative servers** – contain final records
4. **Recursive resolvers** (e.g.: 8.8.8.8) – cascading queries for clients

### 5.3 Record Types

| Type | Function | Example |
|------|----------|---------|
| **A** | IPv4 address | `example.com → 93.184.216.34` |
| **AAAA** | IPv6 address | `example.com → 2606:2800:220:1::` |
| **MX** | Mail exchanger | `example.com → 10 mail.example.com` |
| **CNAME** | Alias (canonical name) | `www.example.com → example.com` |
| **NS** | Authoritative nameserver | `example.com → ns1.example.com` |
| **TXT** | Arbitrary text | SPF, DKIM, verifications |
| **SOA** | Start of Authority | Zone information |
| **PTR** | Reverse lookup | IP → name |

### 5.4 DNS Packet Structure (RFC 1035)

```
Header (12 bytes):
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                      ID                       |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE   |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    QDCOUNT                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    ANCOUNT                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    NSCOUNT                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    ARCOUNT                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

Question Section:
  QNAME:  variable (labels: length+chars, terminated with 0)
          e.g.: 03www06google03com00
  QTYPE:  16 bits (A=1, AAAA=28, MX=15, etc.)
  QCLASS: 16 bits (IN=1)
```

**Flags**:
- **QR** (1 bit): 0=query, 1=response
- **RD** (1 bit): Recursion Desired
- **RA** (1 bit): Recursion Available
- **RCODE** (4 bits): 0=no error, 3=NXDOMAIN

### 5.5 TTL and Caching

**TTL (Time To Live)** specifies the lifespan of a record in cache:
- Short TTL (300s) – frequent updates, higher traffic to authoritative
- Long TTL (86400s) – better performance, slow propagation of changes

**Cache levels**:
1. Browser cache
2. OS cache (local resolver)
3. Router/gateway cache
4. ISP recursive resolver cache

### 5.6 DNSSEC

DNSSEC adds authenticity and integrity to DNS responses through cryptographic signatures, protecting against DNS spoofing attacks.

---

## 6. SSH – Secure Shell

### 6.1 Introduction

SSH (RFC 4251-4254) provides secure access to remote systems, replacing unencrypted protocols such as Telnet and rsh.

**Features**:
- Authentication (password, public keys, certificates)
- Encryption (AES, ChaCha20)
- Integrity (HMAC)
- Tunnels (port forwarding)
- File transfer (SCP, SFTP)

### 6.2 SSH Architecture

```
┌────────────────────────────────────────────────────┐
│                 SSH Connection                      │
│  ┌────────────────────────────────────────────────┐│
│  │            SSH User Auth Layer                 ││
│  │  ┌────────────────────────────────────────────┐││
│  │  │         SSH Transport Layer                │││
│  │  │  ┌────────────────────────────────────────┐│││
│  │  │  │              TCP                        ││││
│  │  │  └────────────────────────────────────────┘│││
│  │  └────────────────────────────────────────────┘││
│  └────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────┘
```

**Layers**:
1. **Transport Layer** – encryption, integrity, key exchange
2. **User Authentication Layer** – identity verification
3. **Connection Layer** – multiplexed channels (shell, forwarding)

### 6.3 Key Exchange

At connection, client and server negotiate:
1. Protocol version
2. Encryption algorithms
3. Session keys (via Diffie-Hellman)
4. Server identity verification (host key)

```
Client                                 Server
   │                                      │
   │ ──── SSH-2.0-OpenSSH_8.9 ──────────►│
   │ ◄──── SSH-2.0-OpenSSH_8.9 ─────────│
   │                                      │
   │ ──── Key Exchange Init ────────────►│
   │ ◄──── Key Exchange Init ───────────│
   │                                      │
   │ ◄──── DH Key Exchange ─────────────►│
   │                                      │
   │ ◄──── Server Host Key + Sig ───────│
   │       (verification: ~/.ssh/known_hosts)
   │                                      │
   │ ═════════ Encrypted Channel ════════│
```

### 6.4 Authentication

**Methods** (in order of preference):
1. **Publickey** – private key signs a challenge
2. **Password** – transmitted encrypted through secure channel
3. **Keyboard-interactive** – 2FA, TOTP
4. **GSSAPI** – Kerberos

**Key generation**:
```bash
ssh-keygen -t ed25519 -C "user@example.com"
# Result: ~/.ssh/id_ed25519 (private) + ~/.ssh/id_ed25519.pub (public)
```

### 6.5 Channels and Port Forwarding

SSH multiplexes multiple logical channels over a single TCP connection.

**Local Port Forwarding** (`-L`):
```
ssh -L 8080:remote-db:3306 user@bastion
# Connection to localhost:8080 → tunnel → remote-db:3306
```

**Remote Port Forwarding** (`-R`):
```
ssh -R 9000:localhost:80 user@public-server
# public-server:9000 → tunnel → localhost:80
```

**Dynamic Port Forwarding** (`-D`):
```
ssh -D 1080 user@proxy
# SOCKS5 proxy on localhost:1080
```

---

## 7. Review Questions

1. Why does FTP use two separate connections for control and data?
2. What is the advantage of passive FTP mode over active in the presence of NAT?
3. What role do root servers play in the DNS hierarchy?
4. Why does TTL affect the speed of DNS change propagation?
5. How does SSH protect against man-in-the-middle attacks?
6. What is "known_hosts" and why is it important?

---

## 8. What We Learned

- FTP: file transfer protocol with dual-connection architecture
- DNS: distributed hierarchical system for name resolution
- SSH: secure channel for remote access and tunnelling
- Importance of encryption and authentication in modern protocols

---

## 9. Bibliography

| Reference | DOI/Link |
|-----------|----------|
| J. Kurose, K. Ross - Computer Networking: A Top-Down Approach, 8th Ed., Pearson, 2021 | ISBN: 978-0135928615 |
| B. Rhodes, J. Goetzen - Foundations of Python Network Programming, 3rd Ed., Apress, 2014 | DOI: 10.1007/978-1-4302-5855-1 |

**Standards and Specifications** (without DOI):
- RFC 959 – File Transfer Protocol (FTP)
- RFC 1035 – Domain Names - Implementation and Specification
- RFC 4251-4254 – The Secure Shell (SSH) Protocol Architecture
- RFC 4253 – SSH Transport Layer Protocol

---

*Document generated for Lecture 11 – Computer Networks*  
*Revolvix&Hypotheticalandrei*
