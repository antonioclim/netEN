# Evaluation Rubrics – Week 2

**OSI/TCP-IP Architectural Models & Socket Programming**

---

## Formative Evaluation (during seminar)

### Criterion 1: Understanding Architectural Models

| Level | Description | Score |
|-------|-------------|-------|
| **Excellent** | Explains all 7 OSI layers and 4 TCP/IP layers, with protocol examples and PDU for each | 10 |
| **Good** | Knows main layers, makes correct OSI↔TCP/IP equivalences | 8 |
| **Satisfactory** | Can enumerate layers, knows a few protocols | 6 |
| **Insufficient** | Confusion between layers, doesn't connect to protocols | 4 |

### Criterion 2: TCP Socket Programming

| Level | Description | Score |
|-------|-------------|-------|
| **Excellent** | Functional concurrent server, correctly handles exceptions, complete logging | 10 |
| **Good** | Functional server, handles multiple connections, correct response | 8 |
| **Satisfactory** | Simple functional server, one client at a time | 6 |
| **Insufficient** | Incomplete code or doesn't compile | 4 |

### Criterion 3: UDP Socket Programming

| Level | Description | Score |
|-------|-------------|-------|
| **Excellent** | server with complete application protocol, timeout handling, statistics | 10 |
| **Good** | Functional server with basic protocol (ping/upper) | 8 |
| **Satisfactory** | Simple functional echo server | 6 |
| **Insufficient** | Incomplete code or errors | 4 |

### Criterion 4: Traffic Analysis

| Level | Description | Score |
|-------|-------------|-------|
| **Excellent** | Correctly identifies TCP handshake, correlates with code, explains TCP/UDP differences | 10 |
| **Good** | Identifies handshake and payload, understands overhead | 8 |
| **Satisfactory** | Can run capture and visualise with tshark | 6 |
| **Insufficient** | Cannot generate or interpret captures | 4 |

---

## Synthetic Grid for Seminar

| Activity | Maximum Score | Notes |
|----------|---------------|-------|
| Attendance and participation | 1 point | - |
| TCP exercises completed | 3 points | Functional template |
| UDP exercises completed | 3 points | Protocol implemented |
| Capture analysis | 2 points | Handshake identification |
| Optional extension | 1 bonus point | Router topology |
| **TOTAL** | **10 points** | |

---

## Contribution to Team Project

### Week 2 Deliverable Artefact

**TCP/UDP Communication Module for team application**

| Criterion | Requirement | Weight |
|-----------|-------------|--------|
| **Functionality** | server accepts multiple connections concurrently | 40% |
| **Protocol** | Defined application protocol (message format, commands) | 25% |
| **Documentation** | README with running instructions | 20% |
| **Clean code** | Structure, comments, naming | 15% |

### Integration with Project

The communication module developed this week will be used in:
- Week 8: HTTP server (extension to complex text protocol)
- Week 9: File transfer (custom FTP)
- Week 11: Load balancing and reverse proxy

---

## Summative Evaluation (exam)

### Multiple Choice Theoretical Questions

1. Which OSI layer is responsible for MAC addressing?
   - a) Physical
   - b) **Data Link** ✓
   - c) Network
   - d) Transport

2. What PDU does the Transport layer use for TCP protocol?
   - a) Packet
   - b) Frame
   - c) **Segment** ✓
   - d) Datagram

3. How many layers does the TCP/IP model have?
   - a) 7
   - b) 5
   - c) **4** ✓
   - d) 3

4. What is the correct sequence of the TCP handshake?
   - a) ACK → SYN → SYN-ACK
   - b) **SYN → SYN-ACK → ACK** ✓
   - c) SYN → ACK → SYN-ACK
   - d) ACK → ACK → SYN

5. Which protocol provides connectionless transfer?
   - a) TCP
   - b) **UDP** ✓
   - c) IP
   - d) ICMP

### Open Questions

1. **Explain the encapsulation process** for an HTTP message from browser to server. (5 points)
   - *Expected answer*: HTTP Data → TCP Segment (port 80) → IP Packet (IP addresses) → Ethernet Frame (MAC addresses) → Bits

2. **Compare TCP and UDP** from the perspective of: overhead, reliability, use cases. (5 points)
   - *Expected answer*: TCP has higher overhead (20+ bytes header, handshake, ACKs), offers reliability; UDP has low overhead (8 bytes), no guarantees. TCP for web/email, UDP for streaming/gaming.

3. **Implement in pseudocode** a TCP server that responds with uppercase to messages. (5 points)
   - *Expected answer*: socket() → bind() → listen() → accept() → recv() → upper() → send() → close()

---

## Correlation with Course Syllabus

### Competences Evaluated

| Competence from Syllabus | How it's Evaluated in W2 |
|--------------------------|--------------------------|
| C1: Using network concepts | Questions about OSI/TCP-IP layers |
| C2: Network programmeming | server/client socket implementation |
| C3: Traffic analysis | Capture and interpretation with tshark |
| C6: Systems update | Module integration in team project |

### Specific Objectives from Syllabus

- *"Using facilities for network workstations"* → Using Mininet, netcat
- *"Communication, information and accessing online applications"* → TCP/UDP server/client

---

## Feedback and Improvement

### After Each Seminar

Questions for students:
1. What was most useful?
2. What was most difficult?
3. What should be explained better?

### Success Indicators

- [ ] ≥80% students can run demo-all without errors
- [ ] ≥70% students correctly identify TCP handshake
- [ ] ≥60% students complete both templates
- [ ] Average completion time: ≤90 minutes

---

*Revolvix&Hypotheticalandrei*
