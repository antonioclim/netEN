# Starterkit Week 2: OSI/TCP-IP Architectural Models & Socket Programming

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Mininet](https://img.shields.io/badge/Mininet-2.3.0-green.svg)](http://mininet.org)
[![License](https://img.shields.io/badge/License-Educational-yellow.svg)]()

**Course:** Computer Networks  
**Week:** 2 of 14  
**Author:** Revolvix&Hypotheticalandrei

---


## 🚀 Quick Clone & Setup

To clone **only this week's content** directly into `~/WEEK2` and make all scripts executable, run the following commands:

### Option A: One-liner (recommended)

```bash
cd ~ && git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK2 && cd WEEK2 && git sparse-checkout set WEEK2 && shopt -s dotglob && mv WEEK2/* . && rmdir WEEK2 && find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

### Option B: Step-by-step (for understanding)

```bash
# 1. Navigate to home directory
cd ~

# 2. Clone repository with sparse checkout (downloads only metadata initially)
git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK2

# 3. Enter the cloned directory
cd WEEK2

# 4. Configure sparse checkout to fetch only WEEK2
git sparse-checkout set WEEK2

# 5. Move contents up one level (flatten structure)
shopt -s dotglob
mv WEEK2/* .
rmdir WEEK2

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
cd ~ && mkdir -p WEEK2 && cd WEEK2 && curl -L https://github.com/antonioclim/netEN/archive/refs/heads/main.tar.gz | tar -xz --strip-components=2 netEN-main/WEEK2 && find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

### Verify Installation

After cloning, verify that scripts are executable:

```bash
cd ~/WEEK2
ls -la scripts/*.sh      # Should show 'x' permission
file scripts/*.sh        # Should show "shell script"
./scripts/setup.sh --help 2>/dev/null || head -5 scripts/setup.sh
```

---


## What We Will Learn

This week introduces the **architectural fundamentals** of network communications and lays the groundwork for **network programmeming** using sockets.

### Learning Objectives

| Level | Objective |
|-------|-----------|
| **Understanding** | Explaining the role of layers in OSI and TCP/IP models |
| **Application** | Implementing a concurrent TCP/UDP server in Python |
| **Analysis** | Capturing and interpreting traffic with Wireshark/tshark |
| **Evaluation** | Comparing TCP vs UDP in practical scenarios |

### Why It Matters

As a future programmemer in the economic/IT field, you will constantly encounter:
- **Network debugging**: "The application is not responding" — is it at L7 (code) or L3 (connectivity)?
- **Security**: Firewalls operate at L3/L4, WAF at L7
- **Architecture**: Choosing TCP (reliability) vs UDP (speed) for financial applications

---


## Kit Structure

```
starterkit_s2/
├── README.md                      # This file
├── Makefile                       # Automation (setup, demo, clean)
├── requirements.txt               # Python dependencies
├── curs/
│   ├── c2-modele-arhitecturale.md # Lecture theoretical content
│   └── assets/
│       ├── images/                # PNG diagrams
│       └── puml/                  # PlantUML sources
├── seminar/
│   ├── python/
│   │   ├── exercises/             # Complete exercises
│   │   │   ├── ex_2_01_tcp.py     # Concurrent TCP server/client
│   │   │   └── ex_2_02_udp.py     # UDP server/client with custom protocol
│   │   └── templates/             # Templates to complete
│   ├── mininet/
│   │   ├── topologies/            # Mininet topologies
│   │   └── scenarios/             # Working scenarios
│   └── captures/                  # pcap output (generated)
├── docs/
│   ├── curs.md                    # Detailed lecture outline
│   ├── seminar.md                 # Detailed seminar outline
│   ├── lab.md                     # Laboratory guide
│   ├── checklist.md               # Teaching staff checklist
│   └── rubrici.md                 # Evaluation criteria
├── scripts/
│   ├── setup.sh                   # Dependency installation
│   ├── capture.sh                 # Start/stop capture
│   ├── clean.sh                   # Environment cleanup
│   └── verify.sh                  # Configuration verification
├── docker/
│   ├── Dockerfile                 # Container for isolated execution
│   └── docker-compose.yml         # Service orchestration
├── slides/
│   ├── curs_slides_outline.txt    # Lecture presentation outline
│   └── seminar_slides_outline.txt # Seminar presentation outline
├── tests/
│   ├── smoke_test.sh              # Quick environment test
│   └── expected_outputs.md        # Reference outputs
└── assets/
    └── style.css                  # Common HTML style
```

---


## System Requirements

### Recommended Environment
- **OS**: Ubuntu 22.04+ / Debian 11+ (CLI-only in VirtualBox)
- **RAM**: Minimum 2 GB (recommended 4 GB)
- **Disk**: 5 GB free
- **Python**: 3.8+

### Dependencies
```
python3, python3-pip
mininet (2.3.0+)
openvswitch-switch
tcpdump, tshark (Wireshark CLI)
netcat-openbsd
```

---


## Quick Start

### 1. Environment Setup
```bash
# Clone/extract kit
cd starterkit_s2

# Automatic dependency installation
make setup

# Verify environment
make verify
```

### 2. Complete TCP Demo
```bash
# In one terminal - start server
make tcp-server

# In another terminal - send message
make tcp-client MSG="Hello World"
```

### 3. Mininet Demo
```bash
# Base topology (3 hosts, 1 switch)
make mininet-cli

# In Mininet prompt:
mininet> pingall
mininet> h1 python3 /path/to/ex_2_01_tcp.py server --port 9090 &
mininet> h2 python3 /path/to/ex_2_01_tcp.py client --host 10.0.2.100 --port 9090 -m "test"
```

### 4. Capture and Analysis
```bash
# Start capture + demo + analysis
make demo-all

# View results
make analyze-tcp
make analyze-udp
```

---


## Makefile Targets

| Command | Description |
|---------|-------------|
| `make help` | Display full help |
| `make setup` | Install system dependencies |
| `make verify` | Verify working environment |
| `make demo-all` | Complete TCP+UDP demo with captures |
| `make demo-tcp` | TCP demo only |
| `make demo-udp` | UDP demo only |
| `make mininet-cli` | Mininet CLI base topology |
| `make mininet-extended` | CLI with router (2 subnets) |
| `make tcp-server` | TCP server on localhost:9090 |
| `make tcp-client MSG=x` | TCP client with message |
| `make capture-tcp` | Start TCP traffic capture |
| `make capture-stop` | Stop active captures |
| `make analyze-tcp` | Analysis with tshark |
| `make clean` | Clean processes |
| `make clean-all` | Complete cleanup (+ pcap, logs) |

---


## Weekly Content

### Lecture (2h) — Architectural Models

1. **Why architectural models?** (15 min)
   - Reducing complexity
   - Interoperability
   - Analogy with building architecture

2. **The OSI Model** (35 min)
   - The 7 layers: Physical → Application
   - PDU at each level
   - Encapsulation/Decapsulation

3. **The TCP/IP Model** (25 min)
   - The 4 practical layers
   - Comparison with OSI
   - Real protocols

4. **Link to programmeming** (15 min)
   - Socket API as interface
   - Preview: socket seminar

### Seminar (2h) — Socket Programming

1. **Mininet Warm-up** (15 min)
   - Starting topology
   - Connectivity verification

2. **TCP Lab** (35 min)
   - Concurrent server (threading)
   - Handshake SYN-SYN/ACK-ACK
   - Capture and analysis

3. **UDP Lab** (25 min)
   - Datagram server
   - Custom application protocol
   - Overhead comparison

4. **Templates** (25 min)
   - Guided code completion
   - Functionality testing

---


## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Address already in use` | `pkill -f ex_2_01` or change port |
| `Connection refused` | Check if server is running: `jobs` |
| Empty capture | Check interface and tcpdump filter |
| Mininet won't start | `sudo mn -c` for cleanup |
| `mn: command not found` | `sudo apt-get install mininet` |

---


## Additional Resources

### Required Bibliography
- Kurose, Ross — *Computer Networking: A Top-Down Approach*, Ch. 1-2
- Rhodes, Goetzen — *Foundations of Python Network Programming*, Ch. 1-3

### Technical Specifications
- RFC 793: TCP
- RFC 768: UDP
- IEEE 802.3: Ethernet

### Interactive Materials
- `theory.html` — Interactive theory (25+ slides)
- `seminar.html` — Seminar dashboard (8 tabs)
- `lab.html` — Step-by-step laboratory guide

---


## Contribution to Team Project

This week brings the following **incremental artefact**:

> **TCP/UDP Communication Module** for the team application
> - server that accepts connections from multiple clients
> - Basic application protocol (request-response)
> - Structured logging for debugging

---


## Licence

Educational material for internal use — ASE Bucharest, CSIE.

*Revolvix&Hypotheticalandrei*

---


## Standardisation (v2.1.0)

This kit follows the **Cross-cutting Standard** for networking educational materials.

### Automatic Demo

```bash
# Run complete demo (produces artefacts)
./scripts/run_all.sh

# Verify generated artefacts
./tests/smoke_test.sh

# Cleanup
./scripts/cleanup.sh
```

### Generated Artefacts

After `run_all.sh`, in `artifacts/`:
- `demo.log` - Complete demo log
- `demo.pcap` - TCP+UDP traffic capture
- `validation.txt` - Validation report

### Standard IP Plan (WEEK 2)

| Entity | IP |
|--------|-----|
| Network | 10.0.2.0/24 |
| Gateway | 10.0.2.1 |
| server | 10.0.2.100 |

### Standard port Plan

| Service | port |
|---------|------|
| TCP App | 9090 |
| UDP App | 9091 |
| Week Base | 5200-5299 |

---

