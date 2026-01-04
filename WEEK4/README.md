# 🌐 Week 4 Starterkit: Physical Layer, Data Link & Custom Protocols

> **Course:** Computer Networks  
> **Programme:** Business Informatics, Year III, Semester 2  
> **Institution:** Bucharest University of Economic Studies - CSIE  
> **Week:** 4 of 14

---


## 🚀 Quick Clone & Setup

To clone **only this week's content** directly into `~/WEEK4` and make all scripts executable, run the following commands:

### Option A: One-liner (recommended)

```bash
cd ~ && git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK4 && cd WEEK4 && git sparse-checkout set WEEK4 && shopt -s dotglob && mv WEEK4/* . && rmdir WEEK4 && find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

### Option B: Step-by-step (for understanding)

```bash
# 1. Navigate to home directory
cd ~

# 2. Clone repository with sparse checkout (downloads only metadata initially)
git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK4

# 3. Enter the cloned directory
cd WEEK4

# 4. Configure sparse checkout to fetch only WEEK4
git sparse-checkout set WEEK4

# 5. Move contents up one level (flatten structure)
shopt -s dotglob
mv WEEK4/* .
rmdir WEEK4

# 6. Make all shell scripts and Python files executable
find . -type f -name "*.sh" -exec chmod +x {} \;
find . -type f -name "*.py" -exec chmod +x {} \;

# 7. Verify the setup
ls -la
ls -la scripts/
```

### Option C: Without Git history (lightweight)

If you don't need Git history and want the smallest possible download:

```bash
cd ~ && mkdir -p WEEK4 && cd WEEK4 && curl -L https://github.com/antonioclim/netEN/archive/refs/heads/main.tar.gz | tar -xz --strip-components=2 netEN-main/WEEK4 && find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

### Verify Installation

After cloning, verify that scripts are executable:

```bash
cd ~/WEEK4
ls -la scripts/*.sh      # Should show 'x' permission
file scripts/*.sh        # Should show "shell script"
./scripts/setup.sh --help 2>/dev/null || head -5 scripts/setup.sh
```

---


## 📋 Table of Contents

1. [Learning Objectives](#-learning-objectives)
2. [Starterkit Structure](#-starterkit-structure)
3. [System Requirements](#-system-requirements)
4. [Quick Installation](#-quick-installation)
5. [Usage Guide](#-usage-guide)
6. [Implemented Protocols](#-implemented-protocols)
7. [Practical Exercises](#-practical-exercises)
8. [Troubleshooting](#-troubleshooting)
9. [Resources and References](#-resources-and-references)

---


## 🎯 Learning Objectives

By the end of this laboratory, students will be able to:

### Cognitive Level - Understanding
- Describe the role of the physical layer and its limitations
- Explain the difference between TEXT and BINARY protocols
- Understand the concept of framing in TCP (stream vs messages)
- Identify the advantages of CRC32 for error detection

### Application Level - Implementation
- Implement concurrent TCP servers (multi-threading)
- Build custom protocols over TCP and UDP
- Use `struct` for binary serialisation
- Calculate and verify CRC32 for integrity

### Analytical Level - Investigation
- Capture and analyse traffic with tcpdump/tshark
- Identify the overhead of different protocol formats
- Diagnose communication issues at byte level

---


## 📁 Starterkit Structure

```
starterkit_s4/
│
├── 📄 README.md                    # This file
├── 📄 Makefile                     # Automation (make help)
│
├── 📂 python/
│   ├── apps/                       # Complete applications
│   │   ├── text_proto_server.py    # TCP text protocol server
│   │   ├── text_proto_client.py    # TCP text protocol client
│   │   ├── binary_proto_server.py  # TCP binary protocol server
│   │   ├── binary_proto_client.py  # TCP binary protocol client
│   │   ├── udp_sensor_server.py    # UDP sensor server
│   │   └── udp_sensor_client.py    # Sensor client/simulator
│   ├── utils/                      # Shared utilities
│   │   ├── io_utils.py             # recv_exact, recv_until
│   │   └── proto_common.py         # Protocol definitions, CRC32
│   ├── templates/                  # Templates for exercises
│   │   └── text_server_template.py # TODO: implement COUNT
│   └── solutions/                  # Solutions (for teaching staff)
│
├── 📂 scripts/
│   ├── setup.sh                    # Dependency installation
│   └── run_all.sh                  # Complete demo
│
├── 📂 tests/
│   └── smoke_test.sh               # Quick verification
│
├── 📂 docs/                        # Markdown documentation
├── 📂 assets/images/               # PNG diagrams
├── 📂 results/                     # Generated logs (gitignore)
└── 📂 pcap/                        # Network captures (gitignore)
```

---


## 💻 System Requirements

### Mandatory
| Component | Minimum Version | Verification |
|-----------|-----------------|--------------|
| Python | 3.8+ | `python3 --version` |

### Recommended (for captures and analysis)
| Component | Purpose | Installation |
|-----------|---------|--------------|
| tcpdump | Packet capture | `sudo apt install tcpdump` |
| tshark | Advanced analysis | `sudo apt install tshark` |
| netcat | Manual testing | `sudo apt install netcat` |

**Note:** All required Python modules are from the standard library (socket, struct, zlib, threading).

---


## 🚀 Quick Installation

```bash
# 1. Extract archive
unzip starterkit_s4.zip
cd starterkit_s4

# 2. Setup
chmod +x scripts/*.sh tests/*.sh
./scripts/setup.sh

# 3. Verify
make verify

# 4. Quick demo
make run-demo
```

---


## 📖 Usage Guide

### Main Make Commands

```bash
make help           # Display all options
make verify         # Verify environment (Python, ports)
make check          # Verify Python syntax
make test           # Run smoke test

make server-text    # Start TEXT server (port 5400)
make server-binary  # Start BINARY server (port 5401)
make server-udp     # Start UDP server (port 5402)

make run-demo       # Complete demo (all protocols)
make capture        # Capture traffic on loopback
make clean          # Clean temporary files
make reset          # Complete reset (stop servers + clean)
```

### Manual TEXT Protocol Testing

```bash
# Terminal 1: start server
make server-text

# Terminal 2: interactive client
python3 python/apps/text_proto_client.py --host localhost --port 5400

# Or batch commands:
python3 python/apps/text_proto_client.py --host localhost --port 5400 \
    -c "SET name Alice" -c "GET name" -c "COUNT"
```

### Manual BINARY Protocol Testing

```bash
# Terminal 1: start server
make server-binary

# Terminal 2: interactive client
python3 python/apps/binary_proto_client.py --host localhost --port 5401

# Available commands: echo, put, get, count, keys, quit
```

### UDP Sensor Testing

```bash
# Terminal 1: start server
make server-udp

# Terminal 2: simulate sensors
python3 python/apps/udp_sensor_client.py --host localhost --port 5402 \
    --sensor-id 1 --temp 23.5 --location "Lab1"

# Continuous mode (one packet per second)
python3 python/apps/udp_sensor_client.py --host localhost --port 5402 \
    --sensor-id 1 --location "Lab1" --continuous --interval 1.0

# Error detection testing (corrupted packet)
python3 python/apps/udp_sensor_client.py --host localhost --port 5402 \
    --sensor-id 99 --temp 0.0 --location "Test" --corrupt
```

---


## 📡 Implemented Protocols

### 1. TEXT Protocol over TCP (Port 5400)

**Framing:** Length-prefix
```
<LEN> <PAYLOAD>

Example: "11 SET name Alice"
         ^^  ^^^^^^^^^^^^^^
         |   payload (11 bytes)
         payload length
```

**Commands:**
| Command | Description | Example |
|---------|-------------|---------|
| PING | Connectivity test | `PING` → `OK pong` |
| SET | Store value | `SET key value` → `OK stored key` |
| GET | Read value | `GET key` → `OK key value` |
| DEL | Delete key | `DEL key` → `OK deleted` |
| COUNT | Key count | `COUNT` → `OK 3 keys` |
| KEYS | List keys | `KEYS` → `OK key1 key2 key3` |
| QUIT | Disconnect | `QUIT` → `OK bye` |

### 2. BINARY Protocol over TCP (Port 5401)

**Fixed header (14 bytes):**
```
+--------+--------+--------+------------+--------+--------+
| magic  |version | type   |payload_len |  seq   | crc32  |
| 2B     | 1B     | 1B     | 2B         |  4B    | 4B     |
+--------+--------+--------+------------+--------+--------+
  "NP"      1     1-255     0-65535     uint32   uint32
```

**Message types:**
- ECHO_REQ (1) / ECHO_RESP (2)
- PUT_REQ (3) / PUT_RESP (4)
- GET_REQ (5) / GET_RESP (6)
- COUNT_REQ (9) / COUNT_RESP (10)
- KEYS_REQ (7) / KEYS_RESP (8)
- ERROR (255)

### 3. UDP Sensor Protocol (Port 5402)

**Fixed datagram (23 bytes):**
```
+--------+-----------+--------+----------+--------+
|version | sensor_id |  temp  | location | crc32  |
| 1B     | 4B        | 4B(f)  | 10B      | 4B     |
+--------+-----------+--------+----------+--------+
```

---


## 📝 Practical Exercises

### Exercise 1: Implement COUNT (Template)

**File:** `python/templates/text_server_template.py`

**Objective:** Complete the COUNT command implementation.

```bash
# Edit the file
nano python/templates/text_server_template.py

# Find the TODO and implement COUNT
# Hint: len(state) returns the number of keys

# Testing
python3 python/templates/text_server_template.py
# In another terminal:
python3 python/apps/text_proto_client.py -c "SET a 1" -c "SET b 2" -c "COUNT"
# Expected: OK 2 keys
```

### Exercise 2: Traffic Capture and Analysis

```bash
# Terminal 1: start server
make server-text

# Terminal 2: start capture
sudo tcpdump -i lo -w capture.pcap port 5400

# Terminal 3: generate traffic
python3 python/apps/text_proto_client.py -c "SET name Alice" -c "GET name"

# Stop capture (Ctrl+C in Terminal 2)

# Analysis
tcpdump -r capture.pcap -X | head -50
# or with tshark:
tshark -r capture.pcap -V
```

### Exercise 3: TEXT vs BINARY Overhead Comparison

Calculate the overhead for storing the same value:

```python
# TEXT: "11 SET name Alice"
# = 2 (length) + 1 (space) + 3 (SET) + 1 (space) + 4 (name) + 1 (space) + 5 (Alice)
# = 17 bytes

# BINARY: header(14) + payload
# payload = key_len(1) + key(4) + value(5) = 10 bytes
# Total = 14 + 10 = 24 bytes

# But for larger messages, binary becomes more efficient!
```

---


## 🛠️ Troubleshooting

### Port already in use
```bash
# Find process
sudo lsof -i :5400
# Terminate
sudo kill -9 <PID>
# Or complete reset
make reset
```

### Connection refused
```bash
# Verify server is running
pgrep -a python | grep proto

# Manual start with verbose
python3 python/apps/text_proto_server.py --verbose
```

### Module not found
```bash
# Verify structure
ls -la python/utils/

# Run from correct directory
cd starterkit_s4
python3 python/apps/text_proto_server.py
```

---


## 📚 Resources and References

### Bibliography
1. Kurose, J. & Ross, K. (2016). *Computer Networking: A Top-Down Approach*, 7th Ed.
2. Rhodes, B. & Goerzen, J. (2014). *Foundations of Python Network Programming*

### Python Documentation
- [socket — Low-level networking interface](https://docs.python.org/3/library/socket.html)
- [struct — Interpret bytes as packed binary data](https://docs.python.org/3/library/struct.html)
- [zlib — Compression compatible with gzip](https://docs.python.org/3/library/zlib.html)

### Relevant RFCs
- [RFC 826 - ARP](https://tools.ietf.org/html/rfc826)
- [RFC 793 - TCP](https://tools.ietf.org/html/rfc793)
- [RFC 768 - UDP](https://tools.ietf.org/html/rfc768)

---


## 📄 Licence

Educational material for the use of ASE-CSIE students.  
© 2025 Department of Economic Informatics and Cybernetics

---


*Last updated: December 2025*  
*Revolvix&Hypotheticalandrei*
