# Lecture 2: Architectural Models for Computer Networks

**Course:** Computer Networks  
**Duration:** 2 hours (100 minutes)  
**Format:** Interactive lecture with diagrams and dialogue  
**Materials:** PPT/reveal.js slides, PNG diagrams, HTML dashboard

---

## Week's Purpose

### What We Will Learn
This session introduces the two fundamental computer network architecture models: the **OSI model** (theoretical, 7 layers) and the **TCP/IP model** (practical, 4 layers). We will analyse the role of each layer, the data encapsulation process and establish the link with network programmeming.

### Why It Matters
Understanding architectural models is essential for any IT professional because it provides the common vocabulary for communicating about network problems, the conceptual structure for diagnosis and debuggingand the foundation for understanding protocols and their implementation.

A business computing specialist must quickly distinguish between an application problem (layer 7, for example an HTTP server returning 500 errors) and a connectivity problem (layer 3, for example lost packets or ping timeout).

---

## Prerequisites

### From Previous Week (Lecture 1)
- **Protocol**: set of rules for communication between entities
- **Protocol stack**: hierarchy of cooperating protocols
- **Encapsulation**: adding headers during transmission
- **Addressing**: unique identification of devices in the network

### Ultra-brief Recap
A protocol defines the message format and exchange rules. Protocols are organised hierarchically in a stack, with each level providing services to the one above. During transmission, data is progressively encapsulated with headers specific to each level.

---

## Part I: Fundamentals of Modelling (25 minutes)

### Why Do We Need Architectural Models?

Computer networks are systems of remarkable complexity, involving diverse hardware (routers, switches, cables, antennas), varied software (drivers, operating systems, applications) and multiple protocols that must cooperate.

**Layer separation** solves this complexity through:
1. **Complexity reduction** – each layer manages a limited set of responsibilities
2. **Interoperability** – equipment from different manufacturers can communicate by respecting layer specifications
3. **Independent development** – a layer can evolve without affecting others
4. **Systematic testing** – problems can be isolated to a specific level

**Architectural analogy**: Just as a building has foundation, structure, installations and finishes that are built independently but work together, a network has distinct layers with well-defined interfaces.

### The Layer Concept

A layer fulfils a specific role in the communication process:
- **Provides services** to the immediately superior layer
- **Uses services** from the immediately inferior layer
- **Communicates through standardised interfaces** with adjacent layers
- **Implements protocols** specific to its role

Communication between layers is done exclusively through defined interfaces; a layer does not "skip" over another.

### Key Concepts

| Term | Definition | Example |
|------|------------|---------|
| **PDU** | Protocol Data Unit – the data unit at a given layer | TCP Segment, IP Packet, Ethernet Frame |
| **SDU** | Service Data Unit – data received from the upper layer | TCP payload is the SDU for IP |
| **SAP** | Service Access Point – access point between layers | TCP port |
| **Encapsulation** | Adding own header to SDU | IP Header + TCP Segment |

---

## Part II: The OSI Model (35 minutes)

### Introduction

**OSI** = Open Systems Interconnection, developed by ISO (International Organization for Standardization) in the 1980s as a response to the proliferation of incompatible proprietary systems.

**Characteristics**:
- Theoretical reference model
- 7 distinct layers
- Purpose: complete and standardised description of communication
- Independence from hardware/software implementation

### The 7 OSI Layers

#### Layer 1 – Physical

| Aspect | Description |
|--------|-------------|
| **Role** | Bit transmission on the physical medium |
| **PDU** | Bit |
| **Functions** | Signal modulation, bit synchronisation, transmission rate control |
| **Implementation** | Hardware (NIC, cable, transceiver) |
| **Examples** | Ethernet Cat5/6, Fibre optic, WiFi radio |

**Reflection question**: What difference exists between representing a "1" bit on copper cable (electrical signal) and on fibre optic (light pulse)?

#### Layer 2 – Data Link

| Aspect | Description |
|--------|-------------|
| **Role** | Frame transfer between directly connected nodes |
| **PDU** | Frame |
| **Functions** | Physical addressing (MAC), error detection (CRC), frame delimitation |
| **Sublayers** | MAC (Media Access Control), LLC (Logical Link Control) |
| **Examples** | Ethernet (IEEE 802.3), WiFi (IEEE 802.11) |

The MAC address is the unique 48-bit identifier "burned" into hardware, consisting of OUI (first 24 bits, identifies manufacturer) and device identifier.

#### Layer 3 – Network

| Aspect | Description |
|--------|-------------|
| **Role** | Packet delivery between different networks |
| **PDU** | Packet |
| **Functions** | Logical (hierarchical) addressing, routing, fragmentation/reassembly |
| **Main protocol** | IP (Internet Protocol) |
| **Devices** | Router |

**Key concept**: The difference between physical address (MAC – globally unique, flat) and logical address (IP – hierarchical, configurable). MAC identifies the hardware interface, IP identifies the position in the logical topology.

#### Layer 4 – Transport

| Aspect | Description |
|--------|-------------|
| **Role** | Process-to-process (end-to-end) communication |
| **PDU** | Segment (TCP) / Datagram (UDP) |
| **Functions** | Multiplexing via ports, flow/error control, reordering |
| **Protocols** | TCP (connection-oriented), UDP (connectionless) |

**Analogy**: If the IP address is the block address, the port is the flat number.

#### Layer 5 – Session

| Aspect | Description |
|--------|-------------|
| **Role** | Managing dialogue between applications |
| **Functions** | Session initiation/maintenance/termination, dialogue control |
| **Note** | Often implemented implicitly in modern applications |

#### Layer 6 – Presentation

| Aspect | Description |
|--------|-------------|
| **Role** | Data representation and transformation |
| **Functions** | Encoding/decoding, format conversions, compression, encryption |
| **Examples** | TLS/SSL, UTF-8, JSON, XML, ASN.1 |

#### Layer 7 – Application

| Aspect | Description |
|--------|-------------|
| **Role** | Interface with the user or application |
| **Functions** | Application-specific services (web, email, files) |
| **Protocols** | HTTP, FTP, SMTP, DNS, SSH |

**Important distinction**: "Application" (Chrome browser) vs. "application protocol" (HTTP).

### Communication in the OSI Model

**Vertical communication**: between layers in the same system, through SAP interfaces.

**Horizontal (virtual) communication**: between peer layers on different systems. Each layer "believes" it is talking directly to its counterpart, although in reality data traverses the entire stack.

### The Encapsulation Process

During **transmission**:
1. Application generates data
2. Each layer adds its own header (and possibly trailer)
3. At physical level, bits are transmitted

During **reception**:
1. Physical layer receives bits
2. Each layer removes its own header and delivers payload to upper layer
3. Application receives original data

### Implementation Location

| Layers | Typical Implementation |
|--------|------------------------|
| 5-7 (Session, Presentation, Application) | Applications in user space |
| 4 (Transport) | Operating system kernel |
| 2-3 (Data Link, Network) | Kernel + Driver |
| 1 (Physical) | Hardware (NIC) |

---

## Part III: The TCP/IP Model (25 minutes)

### Introduction

The TCP/IP model is the actual model of the Internet, developed in the 1970s for ARPANET, before OSI. It is a pragmatic model, based on real protocols, not theoretical abstractions.

### The 4 TCP/IP Layers

#### Network Access Layer (Network Access / Link)
- Equivalent to: Physical + Data Link (OSI)
- Not standardised by TCP/IP – relies on existing technologies
- Examples: Ethernet, WiFi, PPP

#### Internet Layer
- Main protocol: IP (IPv4, IPv6)
- Characteristics: connectionless, no guarantees, best-effort routing
- Auxiliary protocols: ICMP (diagnostics), ARP (address resolution)

#### Transport Layer
| Protocol | Characteristics |
|----------|-----------------|
| **TCP** | Connection-oriented, acknowledgements (ACK), flow/error/congestion control, reordering |
| **UDP** | Connectionless, no guarantees, minimal overhead, low latency |

**When do we use UDP?** Video/audio streaming (Netflix, Zoom), online gaming, DNS queries, IoT with resource constraints.

#### Application Layer
- Combines functionalities of layers 5, 6, 7 from OSI
- Protocols: HTTP/HTTPS, DNS, SMTP, FTP, SSH, TLS

### OSI vs TCP/IP Comparison

| Criterion | OSI | TCP/IP |
|-----------|-----|--------|
| **Origin** | ISO (standard) | DARPA (practical) |
| **Layers** | 7 | 4 |
| **Approach** | Model-first | Implementation-first |
| **Separation** | Strict | Flexible |
| **Usage** | Reference, learning | Real Internet |

### Why Do We Use Both?

- **OSI for**: analysis, learning, conceptual troubleshooting, certifications (CCNA)
- **TCP/IP for**: real implementation, programmeming, configuration

When an administrator says "the problem is at L3", they refer either to IP (TCP/IP) or to the Network layer (OSI) – they are equivalent.

---

## Part IV: Link to Practice (15 minutes)

### Network Programming and Layers

As a programmemer, you interact with the protocol stack through the **Socket API**:
- **Applications** use sockets and ports (L7/L4)
- **The operating system** implements TCP/UDP and IP (L4/L3)
- **Hardware** manages network access (L2/L1)

### Socket API – Preview

A **socket** is an access point to the protocol stack, an abstraction provided by the OS for network communication.

**Main types**:
- `SOCK_STREAM` → TCP (byte stream, connection-oriented)
- `SOCK_DGRAM` → UDP (datagrams, connectionless)

In the seminar we will implement servers and clients using Python sockets.

### Preparation for Seminar

In the seminar we will:
1. Start a Mininet topology (network emulation)
2. Implement a concurrent TCP server
3. Capture traffic with tshark
4. Identify the TCP handshake in capture
5. Compare TCP vs UDP overhead

---

## Recap – What We Learned

1. **Role of architectural models**: complexity reduction, interoperability, independent development
2. **OSI Model**: 7 theoretical layers, from Physical (L1) to Application (L7)
3. **TCP/IP Model**: 4 practical layers, the real model of the Internet
4. **Differences and equivalences**: OSI for analysis, TCP/IP for implementation
5. **Encapsulation**: headers added during transmission, removed during reception
6. **Socket API**: the programmemer's interface to the protocol stack

### How It Helps Us

- **Troubleshooting**: identifying the level at which a problem occurs
- **Security**: understanding where various protection mechanisms operate
- **Programming**: correct use of sockets and protocols
- **Professional communication**: common vocabulary with other specialists

### Where It Fits in a Programmer's Education

Architectural models are the foundation upon which all subsequent networking knowledge is built. Without understanding layers and encapsulation, specific protocols (HTTP, DNS, TLS) remain "black boxes".

---

## Verification Questions

1. Which OSI layer is responsible for MAC addressing?
2. What PDU does the Transport layer have for TCP? And for UDP?
3. How many layers does the TCP/IP model have and what are they?
4. Name 3 protocols from the Application layer.
5. What is the fundamental difference between TCP and UDP?
6. Why do we need two types of addresses (MAC and IP)?

---

## Selected Bibliography

| Author(s) | Title | Details | DOI |
|-----------|-------|---------|-----|
| Kurose, Ross | Computer Networking: A Top-Down Approach | 7th Ed., Ch. 1-2 | 10.5555/2821234 |
| Tanenbaum, Wetherall | Computer Networks | 5th Ed., Ch. 1 | 10.5555/1972504 |
| Stevens, Fenner, Rudoff | Unix Network Programming | Vol. 1, Ch. 1-2 | 10.5555/510873 |

### Standards and Specifications

- ISO/IEC 7498-1: Information technology — Open Systems Interconnection — Basic Reference Model
- RFC 1122: Requirements for Internet Hosts — Communication Layers
- RFC 793: Transmission Control Protocol
- RFC 768: User Datagram Protocol

---

*Revolvix&Hypotheticalandrei*
