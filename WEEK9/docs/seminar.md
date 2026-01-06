# Seminar 9 – File Protocols: Custom FTP Server and Multi-Client Testing

## What We Will Learn

This seminar session introduces you to the world of file transfer over networks, starting from the fundamental concepts of session (L5) and presentation (L6) layers in the OSI model and reaching the practical implementation of a fully functional pseudo-FTP server. You will discover how raw data transforms into structured messages, how sessions persist beyond individual connections and how Docker containerisation facilitates concurrent server testing.

### Specific Objectives

1. **Understanding FTP architecture**: The distinction between the control channel (port 21) and data channel (port 20 or ephemeral ports), active and passive modes, as well as the lifecycle of an authenticated FTP session.

2. **Implementing a custom binary protocol**: Designing and coding a pseudo-FTP protocol with binary headers (magic bytes, length, CRC-32 checksum), demonstrating presentation layer principles.

3. **Session management**: Maintaining user state (authenticated/unauthenticated, current directory, permissions) across multiple commands, exemplifying session layer functions.

4. **Testing with Docker containers**: Orchestrating a server and multiple clients in isolated containers for validating concurrent behaviour and verifying transfer integrity.

5. **Traffic analysis with Wireshark/tshark**: Capturing and interpreting packets to visualise the handshake, commands and responses of the custom protocol.

---

## Why It Matters

File transfer represents one of the oldest and most widely used network application types. Although modern protocols such as SFTP, SCP or transfer via HTTPS have largely replaced classic FTP in production, understanding the fundamental mechanisms remains essential:

- **Debugging distributed applications**: When a microservice cannot download configurations or when a CI/CD pipeline fails at artefact transfer, knowledge of the underlying protocol dramatically accelerates problem identification.

- **Designing binary APIs**: Many industrial protocols (Modbus, MQTT with binary payload, custom IoT protocols) use the same principles: magic bytes for identification, explicit lengths, checksums for integrity.

- **Security and auditing**: Network traffic analysis for detecting data exfiltration or unauthorised communications requires understanding protocol structure at the byte level.

- **Transferable skills**: The abilities to read protocol specifications, implement binary parsers and test distributed systems are valuable regardless of the language or platform used.

---

## Prerequisites

### Required Knowledge

- **Week 8**: Transport layer (TCP/UDP), socket concept, client-server model
- **Week 4**: Socket programming in Python (connections, send/recv)
- **Week 6**: SDN concepts and simulated topologies (Mininet)

### Technical Configuration

| Component | Minimum Requirement | Recommendation |
|-----------|---------------------|----------------|
| Python | 3.8+ | 3.10+ |
| Docker | 20.10+ | 24.0+ with Compose v2 |
| Wireshark/tshark | 3.x | 4.x |
| Available RAM | 2 GB | 4 GB |
| Disk Space | 500 MB | 1 GB |

### Required Files from Starterkit

```
starterkit_s9/
├── python/
│   ├── demos/
│   │   └── ex_9_02_pseudo_ftp.py
│   └── exercises/
│       └── ex_9_01_endianness.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── server-files/           # Files for transfer
└── client-files/           # Transfer destination
```

---

## Part I: Fundamental Concepts

### 1.1 Session Layer (L5) in the Context of FTP

The session layer manages dialogue between applications, providing mechanisms for:

**Session establishment and termination**
- In FTP, a session begins with the `USER` command and ends with `QUIT`
- The session persists even if data transfer uses separate TCP connections
- The server maintains a context (user, current directory, transfer mode)

**Synchronisation and checkpoints**
- FTP supports resuming interrupted transfers (`REST` command)
- The server confirms each command, allowing the client to synchronise state

**Exception handling**
- Timeouts for inactive sessions
- Recovery mechanisms after network errors

### 1.2 Presentation Layer (L6) in the Context of Custom Protocol

The presentation layer handles data representation:

**Data encoding**
- Our pseudo-FTP protocol uses Big Endian for header numbers
- Filenames are encoded in UTF-8
- Binary content is transmitted as-is

**Compression**
- Optionally, data can be compressed with zlib before transfer
- The header indicates whether the payload is compressed

**Integrity**
- CRC-32 for verifying the integrity of each message
- Magic bytes for identifying protocol type

### 1.3 Pseudo-FTP Protocol Structure

```
┌──────────────────────────────────────────────────────────────┐
│                    HEADER (16 bytes)                         │
├──────────────┬──────────────┬──────────────┬────────────────┤
│ Magic (4B)   │ Length (4B)  │ CRC-32 (4B)  │ Flags (4B)     │
│ 0x46545043   │ Big Endian   │ Big Endian   │ Bit 0: Compr.  │
└──────────────┴──────────────┴──────────────┴────────────────┘
┌──────────────────────────────────────────────────────────────┐
│                    PAYLOAD (variable)                        │
│   Command/Response + Data (if present)                       │
└──────────────────────────────────────────────────────────────┘
```

**Header fields:**

| Field | Offset | Size | Description |
|-------|--------|------|-------------|
| Magic | 0 | 4 bytes | `0x46545043` ("FTPC" in ASCII) |
| Length | 4 | 4 bytes | Payload length in bytes |
| CRC-32 | 8 | 4 bytes | Payload checksum |
| Flags | 12 | 4 bytes | Bit 0: 1=compressed, 0=uncompressed |

---

## Part II: Practical Demonstrations

### Demo 1: Exploring Endianness

**Purpose**: Understanding the difference between Big Endian and Little Endian and the impact on network protocols.

**Execution**:
```bash
cd starterkit_s9/python/exercises
python ex_9_01_endianness.py
```

**Expected result**:
```
=== Endianness Demonstration ===
Number: 0x12345678

Big Endian (Network Byte Order):
  Bytes: 12 34 56 78
  Order: MSB first (most significant byte)

Little Endian (x86/x64):
  Bytes: 78 56 34 12
  Order: LSB first (least significant byte)

Conversion with struct:
  pack('>I', 0x12345678) = b'\x12\x34\x56\x78'
  pack('<I', 0x12345678) = b'\x78\x56\x34\x12'
```

**Interpretation**: Network protocols conventionally use Big Endian (network byte order) to ensure interoperability between different architectures.

### Demo 2: Pseudo-FTP Server

**Purpose**: Starting the server and exploring available commands.

**Terminal 1 - Server**:
```bash
cd starterkit_s9/python/demos
python ex_9_02_pseudo_ftp.py --mode server --port 9021
```

**Terminal 2 - Client**:
```bash
python ex_9_02_pseudo_ftp.py --mode client --host localhost --port 9021
```

**Command sequence**:
```
> AUTH admin:password123
[OK] Authentication successful
> PWD
[OK] /
> LIST
[OK] Files: document.txt (1024 bytes), image.png (2048 bytes)
> GET document.txt
[OK] Transfer complete: 1024 bytes, CRC: 0xA1B2C3D4
> PUT test.txt
[OK] File uploaded: test.txt (512 bytes)
> QUIT
[OK] Session closed
```

### Demo 3: Multi-Client Testing with Docker

**Purpose**: Verifying server behaviour under concurrent load.

**Execution**:
```bash
cd starterkit_s9/docker
docker compose up -d
docker compose logs -f
```

**Expected result**:
```
ftp-server  | [INFO] Server started on 0.0.0.0:9021
client-1    | [INFO] Connecting to ftp-server:9021
client-2    | [INFO] Connecting to ftp-server:9021
client-3    | [INFO] Connecting to ftp-server:9021
client-1    | [OK] AUTH successful
client-2    | [OK] AUTH successful
client-3    | [OK] AUTH successful
client-1    | [OK] GET test1.txt completed
client-2    | [OK] GET test2.txt completed
client-3    | [OK] PUT upload.txt completed
```

**Cleanup**:
```bash
docker compose down -v
```

---

## Part III: Wireshark Capture and Analysis

### 3.1 Preparing the Capture

**Starting capture with tshark**:
```bash
# Separate terminal
tshark -i lo -f "tcp port 9021" -w capture_s9.pcap
```

### 3.2 Generating Traffic

Run demo 2 (server + client) while tshark captures.

### 3.3 Analysing the Capture

**General view**:
```bash
tshark -r capture_s9.pcap -Y "tcp.port == 9021" | head -20
```

**Example output**:
```
  1   0.000000    127.0.0.1 → 127.0.0.1    TCP 74 52486 → 9021 [SYN]
  2   0.000015    127.0.0.1 → 127.0.0.1    TCP 74 9021 → 52486 [SYN, ACK]
  ...
  5   0.000201    127.0.0.1 → 127.0.0.1    TCP 82 9021 → 52486 [PSH, ACK] Len=16
```

**Extracting binary payload**:
```bash
tshark -r capture_s9.pcap -Y "tcp.port == 9021 && tcp.len > 0" \
    -T fields -e data
```

**Interpreting the header** (for first data packet):
```
46545043 00000010 a1b2c3d4 00000000
│        │        │        │
│        │        │        └── Flags: 0 (uncompressed)
│        │        └── CRC-32: 0xA1B2C3D4
│        └── Length: 16 bytes
└── Magic: "FTPC"
```

### 3.4 Useful Wireshark Filters

| Filter | Purpose |
|--------|---------|
| `tcp.port == 9021` | All traffic on server port |
| `tcp.flags.syn == 1` | Only SYN packets (new connections) |
| `tcp.len > 0` | Packets with payload (excludes empty ACKs) |
| `frame contains "FTPC"` | Packets containing magic bytes |

---

## Part IV: Graded Exercises

### Exercise 1: INFO Command (⭐)

**Requirement**: Add the `INFO` command that returns server information: version, uptime, number of active sessions.

**Starting points**:
- The `handle_command()` function in server
- Dictionary with global statistics

**Expected result**:
```
> INFO
[OK] Version: 1.0.0, Uptime: 125s, Sessions: 3
```

### Exercise 2: LIST with Wildcard (⭐⭐)

**Requirement**: Modify the `LIST` command to accept glob patterns (e.g.: `LIST *.txt`).

**Hints**:
- The `fnmatch` module from Python
- The command parser needs to extract the optional argument

**Expected result**:
```
> LIST *.txt
[OK] document.txt (1024), notes.txt (512)
> LIST *.png
[OK] image.png (2048)
```

### Exercise 3: MKDIR Command (⭐⭐)

**Requirement**: Implement `MKDIR <dirname>` to create directories on the server.

**Considerations**:
- Name validation (no special characters)
- Permission checking (authenticated user)
- Error handling (existing directory)

### Exercise 4: Transfer Resumption (⭐⭐⭐)

**Requirement**: Implement `REST <offset>` and `RETR <filename>` commands to resume interrupted transfers.

**Algorithm**:
1. Client sends `REST <bytes_already_downloaded>`
2. Server remembers offset for current session
3. On `RETR`, server starts reading from offset

### Exercise 5: Rate Limiting (⭐⭐⭐)

**Requirement**: Add speed limiting for transfers (e.g.: 100 KB/s per client).

**Techniques**:
- Token bucket algorithm
- Sleep between data chunks
- Configuration via parameter at server startup

### CHALLENGE Exercise: Multi-File Transfer (🏆)

**Requirement**: Implement `MGET <pattern>` and `MPUT <pattern>` for multiple transfers.

**Components**:
1. Pattern expansion on server/client
2. Sequential transfer with progress reporting
3. Rollback on error (optional)
4. Final report: successful/failed files

---

## Part V: Debugging and Common Problems

### Problem 1: Connection Refused

**Symptoms**: Client cannot connect to server.

**Possible causes**:
- Server not running
- Wrong port
- Firewall blocking connection

**Diagnostic**:
```bash
# Check if server is listening
netstat -tlnp | grep 9021
# or
ss -tlnp | grep 9021
```

### Problem 2: Invalid Magic Bytes

**Symptoms**: Server returns "Invalid protocol magic".

**Possible causes**:
- Old/incompatible client
- Data corruption in transit
- Wrong byte order when packing

**Diagnostic**:
```bash
# Inspect first bytes sent
tshark -r capture.pcap -Y "tcp.port == 9021" -x | head -20
```

### Problem 3: CRC Mismatch

**Symptoms**: Transfer apparently successful but file is corrupted.

**Possible causes**:
- CRC calculated on compressed vs. uncompressed data
- Truncation at reception
- Incomplete buffer

**Diagnostic**:
```python
import zlib
data = open('file.bin', 'rb').read()
print(f"CRC-32: {zlib.crc32(data) & 0xffffffff:08X}")
```

### Problem 4: Authentication Failed

**Symptoms**: "Authentication failed" although credentials seem correct.

**Possible causes**:
- Spaces in username/password
- Wrong encoding (UTF-8 vs. ASCII)
- Session timeout expired

### Problem 5: Transfer Blocked

**Symptoms**: GET/PUT starts but does not complete.

**Possible causes**:
- Deadlock (both sides waiting to read)
- TCP buffer full
- Very large file without streaming

**Diagnostic**:
```bash
# Check connection state
ss -tnp | grep 9021
```

### Problem 6: Docker Port Conflict

**Symptoms**: `docker compose up` fails with "port already in use".

**Solution**:
```bash
# Find process using the port
sudo lsof -i :9021
# Stop old containers
docker compose down
# Or change port in docker-compose.yml
```

---

## What We Learned

After completing this seminar, you have acquired:

1. **Theoretical knowledge**: Understanding the role of L5 and L6 layers in the OSI stack, the difference between connection and session, binary encoding principles for protocols.

2. **Practical skills**: Implementing a binary protocol server, managing stateful sessions, validating integrity with CRC-32.

3. **Debugging competencies**: Capturing and analysing traffic with tshark, interpreting binary headers, identifying common causes of errors.

4. **Containerisation experience**: Service orchestration with Docker Compose, concurrency testing, execution environment isolation.

---

## How It Helps Us

The competencies developed in this session apply directly to:

- **Microservices development**: Designing communication between services, choosing serialisation formats (Protocol Buffers, MessagePack)
- **Embedded systems and IoT**: Implementing lightweight protocols for resource-constrained devices
- **Application security**: Network traffic auditing, protocol anomaly detection
- **DevOps and SRE**: Production debugging, network performance analysis

---

## Where It Fits in a Programmer's Education

```
Week 9: File Protocols
         │
    ┌────┴────┐
    ▼         ▼
L5/L6      Implementation
Theory     Practice
    │         │
    └────┬────┘
         │
         ▼
   Competency:
   Designing and implementing
   application protocols
```

This week makes the transition from lower stack layers (physical, link, network, transport) to application-oriented layers. It is the point where theoretical network knowledge transforms into the concrete ability to build functional network services.

---

## Bibliography

| No. | Authors | Title | Publisher | Year | DOI |
|-----|---------|-------|-----------|------|-----|
| 1 | Kurose, J., Ross, K. | Computer Networking: A Top-Down Approach | Pearson | 2021 | 10.5555/3312050 |
| 2 | Rhodes, B., Goerzen, J. | Foundations of Python Network Programming | Apress | 2014 | 10.1007/978-1-4302-5855-1 |
| 3 | Stevens, W.R. | TCP/IP Illustrated, Volume 1 | Addison-Wesley | 2011 | 10.5555/2070741 |
| 4 | Beaulieu, M. | Learning Docker | Packt | 2022 | 10.5555/3485829 |

### Standards and Specifications (without DOI)

- RFC 959: File Transfer Protocol (FTP)
- RFC 2228: FTP Security Extensions
- RFC 3659: Extensions to FTP
- IEEE 802.3: Ethernet Standard (for network byte order context)
