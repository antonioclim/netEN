# Starterkit Week 9 – Computer Networks

## Session Layer (L5), Presentation Layer (L6) & File Protocols

**Course:** Computer Networks  
**Faculty:** Cybernetics, Statistics and Economic Informatics (ASE Bucharest)  
**Programme of study:** Economic Informatics, Year 3, Semester 2  
**Week:** 9 of 14  
**Technologies:** Python 3.10+, Docker, Mininet (optional)

---

## What We Will Learn

This week explores two conceptual layers from the OSI model that no longer appear as distinct protocols on the Internet, but whose functions remain essential in any distributed system.

### Knowledge Objectives
- Explaining the role of session (L5) and presentation (L6) layers in the OSI model
- Differentiating the TCP connection (L4) from the logical session (L5)
- Identifying session and presentation functions in modern systems

### Application Objectives
- Implementing a binary protocol with framing (header + payload)
- Building a server/client with session management
- Using separate connections for control and data transfer

### Analysis and Evaluation Objectives
- Analysing network traffic using tcpdump/Wireshark
- Comparing active and passive modes for file transfer
- Evaluating the impact of latency on protocols

---

## Why It Matters

In the era of microservices and APIs, the conceptual understanding of session and presentation layers becomes critical for proper system design:

- **Authentication and authorisation** (JWT, OAuth) – L5 concepts
- **Data serialisation** (JSON, Protocol Buffers) – L6 concepts
- **Compression and encoding** (gzip, Base64) – L6 concepts
- **State management** (cookies, sessions) – L5 concepts

A programmer who does not understand these concepts will write code that works, but that does not scale and cannot be maintained.

---

## Kit Structure

```
starterkit_s9_final/
├── README.md                      # This file
├── Makefile                       # Main automations
├── requirements.txt               # Python dependencies
│
├── curs/                          # Lecture materials (C9)
│   └── c9_sesiune_prezentare.md   # Complete lecture content
│
├── seminar/                       # Seminar materials (S9)
│   ├── stage1_intro/              # Introduction to file protocols
│   ├── stage2_pseudo_ftp/         # Pseudo-FTP implementation
│   ├── stage3_multi_client/       # Multi-client Docker testing
│   └── stage4_mininet/            # Advanced Mininet scenarios
│
├── python/
│   ├── exercises/
│   │   ├── ex_9_01_endianness.py  # Exercise L6: binary framing
│   │   ├── ex_9_02_pseudo_ftp.py  # Complete pseudo-FTP server/client
│   │   ├── ftp_demo_server.py     # Real FTP server (pyftpdlib)
│   │   └── ftp_demo_client.py     # Real FTP client (ftplib)
│   └── utils/
│       └── net_utils.py           # Utilities: framing, hashing, compression
│
├── mininet/
│   ├── topologies/
│   │   ├── topo_base.py           # 1 server + 1 client
│   │   └── topo_extended.py       # 1 server + 3 clients
│   └── scenarios/
│       └── lab_tasks.md           # Guided tasks
│
├── docker/
│   └── docker-compose.yml         # Multi-client FTP testing
│
├── scripts/
│   ├── setup.sh                   # Dependency installation
│   ├── cleanup.sh                 # Resource cleanup
│   ├── run_demo.sh                # Complete automated demo
│   └── capture_traffic.sh         # tcpdump helper script
│
├── tests/
│   ├── smoke_test.sh              # Quick verification
│   └── verify.sh                  # Environment validation
│
├── docs/
│   ├── curs.md                    # Lecture source Markdown
│   ├── seminar.md                 # Seminar source Markdown
│   ├── lab.md                     # Lab source Markdown
│   ├── checklist.md               # Teaching staff checklist
│   └── rubrici.md                 # Evaluation criteria
│
├── slides/
│   ├── curs_outline.txt           # Lecture outline for export
│   └── seminar_outline.txt        # Seminar outline for export
│
├── html_prezentari/
│   ├── theory.html                # Interactive theory presentation
│   ├── seminar.html               # Super-interactive seminar
│   └── lab.html                   # Step-by-step lab
│
├── assets/
│   ├── images/                    # Generated images
│   └── puml/                      # PlantUML sources
│
├── pcap/                          # Example captures
├── server-files/                  # Server directory
└── client-files/                  # Client directory
```

---

## Requirements and Installation

### Minimum Requirements
- **OS:** Ubuntu 22.04+ / Debian 12+ (or WSL2 on Windows)
- **Python:** 3.10+ (verify with `python3 --version`)
- **Docker:** 24.0+ (optional, for multi-client)
- **Mininet:** 2.3.0+ (optional, for advanced lab)

### Quick Installation (single command)
```bash
make setup
```

### Manual Step-by-Step Installation
```bash
# 1. Install system packages
sudo apt update
sudo apt install -y python3-pip tcpdump net-tools

# 2. Python dependencies
python3 -m pip install --break-system-packages -r requirements.txt

# 3. (Optional) Docker
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER

# 4. (Optional) Mininet
sudo apt install -y mininet openvswitch-switch
```

---

## Quick Start

### Complete Automated Demo (no interactive input):
```bash
# Installation + demo + validation in a single command
./scripts/setup.sh && ./scripts/run_all.sh
```

This produces:
- `artifacts/demo.log` – complete log
- `artifacts/demo.pcap` – traffic capture
- `artifacts/validation.txt` – validation results

### Manual Demo in 3 Terminals:
```bash
# Terminal 1: Pseudo-FTP server (port 5900)
make server

# Terminal 2: Client
make client-list
make client-get FILE=hello.txt

# Terminal 3 (optional): Traffic capture
make capture
```

### Verify Results:
```bash
./tests/smoke_test.sh
```

### Cleanup:
```bash
./scripts/cleanup.sh      # Keeps artefacts
./scripts/cleanup.sh --all # Deletes everything
```

---

## Recommended Workflow

### For Lecture (90 minutes):
1. Slides presentation (`slides/curs_outline.txt` → PowerPoint)
2. Live demo: `make demo-encoding` (demonstrates L6)
3. Discussion: connection vs session
4. Teaser for seminar

### For Seminar (100 minutes):

| Stage | Duration | Activity | Command |
|-------|----------|----------|---------|
| 1 | 15 min | Intro + setup | `make setup` |
| 2 | 20 min | L6 exercise (endianness) | `make ex1` |
| 3 | 35 min | Local Pseudo-FTP | `make server` + `make client` |
| 4 | 20 min | Docker multi-client | `make docker-up` |
| 5 | 10 min | Recap | Discussion |

### For Advanced Lab (optional, 60 min extra):
```bash
sudo make mininet-test
```

---

## Detailed Content

### Session Layer (L5) – Key Concepts

**What does L5 solve?**
- Identifying a logical conversation (not just a TCP connection)
- Maintaining state between multiple messages
- Dialogue control (who speaks when)
- Timeout, expiry, resumption

**Difference between connection and session:**

| Aspect | Connection (L4) | Session (L5) |
|--------|-----------------|--------------|
| What it is | Open TCP/UDP socket | Logical context of interaction |
| Duration | While socket is open | Can survive multiple connections |
| Example | `connect()` → `close()` | Login → multiple requests → logout |
| State | TCP sequence numbers | User, CWD, permissions |

**Modern implementations:**
- HTTP Cookies (session maintenance in stateless protocol)
- JWT / OAuth tokens
- TLS session resumption
- WebSocket connections
- Database sessions (Redis, PostgreSQL)

### Presentation Layer (L6) – Key Concepts

**What does L6 solve?**
- Data representation (encoding)
- Serialisation/deserialisation
- Compression
- (Historically) encryption

**Modern implementations:**
- **Data formats:** JSON, XML, Protocol Buffers
- **Character encodings:** UTF-8, ASCII
- **Compression:** gzip, brotli, zstd
- **Content types:** MIME types (`text/html`, `application/json`)
- **Binary encoding:** Base64 (binary → text)

### File Protocols – Control + Data

**Classic FTP:**
```
client ──control (port 21)──→ server   (commands: USER, PASS, LIST, RETR)
client ←──data (port 20/*)──→ server   (actual file transfer)
```

**Active vs passive mode:**

| Aspect | Active mode | Passive mode |
|--------|-------------|--------------|
| Who listens for data | Client | Server |
| Who initiates data connection | Server | Client |
| Works through NAT/firewall | ❌ Rarely | ✅ Yes |
| Modern usage | Deprecated | Standard |

---

## Available Automations

### Main Makefile targets:
```bash
make help           # List all available targets
make setup          # Complete installation
make clean          # Clean temporary files
make reset          # Reset to initial state

# Exercises
make ex1            # Endianness exercise (L6)
make ex1-demo       # Endianness demo with verbose output

# Pseudo-FTP
make server         # Start the pseudo-FTP server
make client-list    # List files on server
make client-get FILE=hello.txt  # Download a file

# Docker
make docker-up      # Start the Docker stack
make docker-test    # Run multi-client test
make docker-down    # Stop and clean

# Mininet (requires sudo)
make mininet-base   # Minimal topology
make mininet-test   # Automated test with 3 clients

# Traffic capture
make capture        # tcpdump on port 3333
make capture-save   # Save to .pcap file

# Verification
make verify         # Verify environment is OK
make test           # Run all tests
```

---

## Troubleshooting

### Common Problems:

**1. `Address already in use` (port 3333 occupied)**
```bash
ss -lntp | grep 3333
kill <PID>
# or use a different port:
make server PORT=4444
```

**2. `ModuleNotFoundError: pyftpdlib`**
```bash
python3 -m pip install pyftpdlib --break-system-packages
```

**3. `Permission denied` for tcpdump**
```bash
sudo tcpdump -i any "tcp port 3333" -nn
```

**4. Docker: `Cannot connect to Docker daemon`**
```bash
sudo systemctl start docker
sudo usermod -aG docker $USER
```

**5. Mininet: `Cannot find device s1`**
```bash
sudo systemctl restart openvswitch-switch
sudo mn -c
```

---

## Deliverables for Evaluation

1. **Traffic capture** (mandatory): A `.pcap` file demonstrating control/data separation
2. **Successful transfer**: A successfully transferred file + SHA256 hash
3. **Reflective note** (10-15 lines): "Where did I implement L5? Where did I implement L6?"

---

## Bibliography

1. J. Kurose, K. Ross – *Computer Networking: A Top-Down Approach*, 7th Ed., Pearson, 2016
2. B. Rhodes, J. Goerzen – *Foundations of Python Network Programming*, Apress, 2014
3. C. Timofte, R. Constantinescu, I. Nemedi – *Computer Networks – seminar workbook*, ASE, 2004

### Relevant RFCs:
- RFC 959 – File Transfer Protocol (FTP)
- RFC 2616 – HTTP/1.1 (headers Content-Type, Content-Encoding)
- RFC 4627 – JSON Media Type
- RFC 6455 – WebSocket Protocol

---

*Revolvix&Hypotheticalandrei*  
*Last updated: December 2025*
