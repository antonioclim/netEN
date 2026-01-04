# Week 5 Starterkit – Network Layer: IP Addressing

## Complete Kit for Lecture + Seminar + Laboratory

**Course:** Computer Networks  
**Institution:** Bucharest University of Economic Studies – CSIE  
**Version:** 3.0 Ultimate (consolidated from all previous archives)  
**Updated:** December 2025

---


## 🚀 Quick Clone & Setup

To clone **only this week's content** directly into `~/WEEK5` and make all scripts executable, run the following commands:

### Option A: One-liner (recommended)

```bash
cd ~ && git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK5 && cd WEEK5 && git sparse-checkout set WEEK5 && shopt -s dotglob && mv WEEK5/* . && rmdir WEEK5 && find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

### Option B: Step-by-step (for understanding)

```bash
# 1. Navigate to home directory
cd ~

# 2. Clone repository with sparse checkout (downloads only metadata initially)
git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK5

# 3. Enter the cloned directory
cd WEEK5

# 4. Configure sparse checkout to fetch only WEEK5
git sparse-checkout set WEEK5

# 5. Move contents up one level (flatten structure)
shopt -s dotglob
mv WEEK5/* .
rmdir WEEK5

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
cd ~ && mkdir -p WEEK5 && cd WEEK5 && curl -L https://github.com/antonioclim/netEN/archive/refs/heads/main.tar.gz | tar -xz --strip-components=2 netEN-main/WEEK5 && find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

### Verify Installation

After cloning, verify that scripts are executable:

```bash
cd ~/WEEK5
ls -la scripts/*.sh      # Should show 'x' permission
file scripts/*.sh        # Should show "shell script"
./scripts/setup.sh --help 2>/dev/null || head -5 scripts/setup.sh
```

---


## What We Will Learn

By the end of this week, you will be able to:

1. **Identify** the role and functions of the network layer in OSI and TCP/IP models
2. **Explain** the fundamental differences between MAC addressing (L2) and IP (L3)
3. **Recognise** essential fields in IPv4 and IPv6 headers
4. **Calculate** manually and programmatically: network address, broadcast, host range
5. **Apply** FLSM and VLSM subnetting techniques for real-world scenarios
6. **Configure** a simulated multi-subnet infrastructure with static routing
7. **Validate** the correctness of an addressing scheme
8. **Design** optimised addressing schemes for organisations

## Why It Matters

The network layer (Layer 3) is the foundation of the modern Internet. Without a deep understanding of IP addressing and subnetting, configuring enterprise networks, troubleshooting connectivity issues and designing scalable infrastructures become impossible. These skills are essential for any network engineer, system administrator or distributed application developer.

---


## Kit Structure

```
starterkit_s5/
├── README.md                           # This file
├── CHANGELOG.md                        # Change history
├── Makefile                            # Complete automation
├── requirements.txt                    # Python dependencies (minimal)
│
├── artifacts/                          # Generated artefacts
│   ├── demo.log                        # Automatic demo log
│   ├── demo.pcap                       # Packet capture
│   └── validation.txt                  # Validation report
│
├── docs/
│   ├── cheatsheet.md                   # Quick CLI reference
│   ├── curs/
│   │   ├── curs.md                     # Complete lecture notes
│   │   └── checklist.md                # Teaching framework checklist
│   ├── seminar/
│   │   └── seminar.md                  # Seminar guide
│   └── lab/
│       └── lab.md                      # Mininet laboratory guide
│
├── python/
│   ├── apps/
│   │   ├── subnet_calc.py              # Subnetting calculator
│   │   └── udp_echo.py                 # UDP demo server
│   ├── exercises/
│   │   ├── ex_5_01_cidr_flsm.py        # CIDR + FLSM analysis
│   │   ├── ex_5_02_vlsm_ipv6.py        # VLSM + IPv6 utilities
│   │   └── ex_5_03_quiz_generator.py   # Interactive quiz generator
│   └── utils/
│       └── net_utils.py                # Reusable functions
│
├── mininet/
│   ├── topologies/
│   │   ├── topo_5_base.py              # 2 subnets + 1 router
│   │   └── topo_5_extended.py          # VLSM + optional IPv6
│   └── scenarios/
│       └── (practical scenarios)
│
├── scripts/
│   ├── setup.sh                        # Install dependencies
│   ├── run_all.sh                      # Complete automatic demo
│   ├── cleanup.sh                      # Environment cleanup
│   ├── capture.sh                      # Packet capture guide
│   └── verify.sh                       # Configuration verification
│
├── tests/
│   ├── smoke_test.sh                   # Quick validation tests
│   └── expected_outputs.md             # Expected outputs
│
├── slides/
│   ├── curs_slides_outline.txt         # PowerPoint outline
│   └── seminar_slides_outline.txt      # Seminar outline
│
└── solutions/
    └── exercitii_solutii.md            # Complete solutions
```

---


## System Requirements

### Minimum Hardware
- 2 vCPU, 2 GB RAM
- 5 GB disk space

### Required Software

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | >= 3.10 | Exercises, scripts |
| Mininet | >= 2.3.0 | Network simulation |
| Open vSwitch | >= 2.17 | Virtual switch |
| tcpdump/tshark | any | Packet capture |
| Make | >= 4.0 | Automation |

### Quick Verification
```bash
python3 --version          # >= 3.10
mn --version               # Mininet installed
sudo mn --test pingall     # Connectivity test
tshark --version           # Packet capture
make --version             # Automation
```

---


## Quick Installation

```bash
# 1. Navigate to the kit directory
cd starterkit_s5

# 2. Complete setup (with sudo for Mininet)
make setup

# 3. Verify installation
make test

# 4. Run automatic demo (generates artefacts)
make run-all

# 5. Or individual demos
make demo
```

### Automatic Demo with Artefacts

```bash
# Run complete demo and generate:
# - artifacts/demo.log
# - artifacts/demo.pcap  
# - artifacts/validation.txt
./scripts/run_all.sh

# Validate artefacts
make test-artifacts
```

---


## Usage Guide

### Quick Commands (Makefile)

```bash
# Help
make help

# Complete Python demo
make demo

# Individual demos
make demo-cidr          # CIDR analysis
make demo-flsm          # FLSM subnetting
make demo-vlsm          # VLSM allocation
make demo-ipv6          # IPv6 conversions

# Interactive quiz
make quiz

# Mininet laboratory (requires sudo)
sudo make mininet-base           # Simple topology
sudo make mininet-extended       # VLSM
sudo make mininet-extended-ipv6  # With dual-stack

# Cleanup
make clean
make reset              # Clean + mininet-clean
```

### Python Exercises

#### 1. CIDR Analysis

```bash
# Analyse an address with prefix
python3 python/exercises/ex_5_01_cidr_flsm.py analyze 192.168.10.14/26

# With detailed explanations
python3 python/exercises/ex_5_01_cidr_flsm.py analyze 192.168.10.14/26 --verbose

# JSON output
python3 python/exercises/ex_5_01_cidr_flsm.py analyze 192.168.10.14/26 --json
```

#### 2. FLSM Subnetting

```bash
# Split the network into 4 equal subnets
python3 python/exercises/ex_5_01_cidr_flsm.py flsm 192.168.100.0/24 4

# Split into 8 subnets
python3 python/exercises/ex_5_01_cidr_flsm.py flsm 10.0.0.0/24 8
```

#### 3. VLSM Allocation

```bash
# Allocate for 60, 20, 10, 2 hosts
python3 python/exercises/ex_5_02_vlsm_ipv6.py vlsm 172.16.0.0/24 60 20 10 2

# Complex scenario
python3 python/exercises/ex_5_02_vlsm_ipv6.py vlsm 10.10.0.0/22 200 100 50 25 10 2 2 2
```

#### 4. IPv6 Utilities

```bash
# Address compression
python3 python/exercises/ex_5_02_vlsm_ipv6.py ipv6 2001:0db8:0000:0000:0000:0000:0000:0001

# Generate /64 subnets
python3 python/exercises/ex_5_02_vlsm_ipv6.py ipv6-subnets 2001:db8:10::/48 64 10

# Type reference
python3 python/exercises/ex_5_02_vlsm_ipv6.py ipv6-types
```

### Mininet Laboratory

#### Base Topology (2 Subnets)

```bash
# Start with interactive CLI
sudo python3 mininet/topologies/topo_5_base.py --cli
```

Architecture (Week 5):
```
    10.0.5.0/25              10.0.5.128/25
        |                        |
       h1 -------- r1 -------- h2
    .11    .1          .129    .140
```

Useful CLI commands:
```text
mininet> nodes                    # List nodes
mininet> net                      # View topology
mininet> h1 ip addr               # h1 addresses
mininet> h1 ip route              # h1 routing table
mininet> h1 ping -c 3 10.0.5.140  # Connectivity test
mininet> r1 tcpdump -ni r1-eth0 icmp &  # ICMP capture
```

#### Extended Topology (VLSM + IPv6)

```bash
# IPv4 only
sudo python3 mininet/topologies/topo_5_extended.py --cli

# With IPv6 enabled
sudo python3 mininet/topologies/topo_5_extended.py --cli --ipv6
```

VLSM Architecture:
```
    10.0.5.0/26      10.0.5.64/27     10.0.5.96/30
    (62 hosts)       (30 hosts)       (2 hosts)
        |                |                |
       h1 ───────── r1 ─────────── h2 ─── h3
    .11   .1       .65   .70      .97   .98
```

---


## Troubleshooting

| # | Problem | Cause | Solution |
|---|---------|-------|----------|
| 1 | `sudo mn --test pingall` fails | Remaining Mininet processes | `sudo mn -c && sudo systemctl restart openvswitch-switch` |
| 2 | `RTNETLINK answers: File exists` | Remaining interfaces | `sudo mn -c` |
| 3 | Inter-subnet ping fails | Missing gateway or IP forward | Check `ip route` and `sysctl net.ipv4.ip_forward` |
| 4 | Complete timeout (no ARP) | Wrong prefix or duplicate IP | Check `ip addr` on all nodes |
| 5 | `tshark` without permissions | User not in wireshark group | `sudo usermod -aG wireshark $USER` or run with `sudo` |
| 6 | Only ARP in capture, no ICMP | Incorrect gateway | Check `defaultRoute` |
| 7 | IPv6 ping not working | IPv6 forwarding disabled | `sysctl -w net.ipv6.conf.all.forwarding=1` |
| 8 | `No module named mininet` | Mininet not installed | `sudo apt-get install mininet` |

### Complete Reset

```bash
make reset
# or manually:
sudo mn -c
sudo systemctl restart openvswitch-switch
rm -f /tmp/*.pcap
```

---


## Recommended Workflow

### For Lecture (2 hours)

| Time | Activity | Resources |
|------|----------|-----------|
| 0:00-0:45 | Theoretical presentation | `assets/html/theory.html` |
| 0:45-1:15 | Live Python demonstrations | `make demo` |
| 1:15-1:30 | Reflection questions | `docs/curs/intrebari_reflectie.md` |
| 1:30-1:45 | Interactive exercises | `make quiz` |
| 1:45-2:00 | Summary and seminar preview | - |

### For Seminar (2 hours)

| Time | Activity | Resources |
|------|----------|-----------|
| 0:00-0:15 | Theoretical recap | `assets/html/seminar.html` |
| 0:15-0:45 | Individual CIDR/VLSM exercises | `docs/seminar/exercises.md` |
| 0:45-1:30 | Guided Mininet laboratory | `assets/html/lab.html` |
| 1:30-1:50 | Traffic capture and analysis | tcpdump/tshark in Mininet |
| 1:50-2:00 | Validation and questions | `solutions/exercitii_solutii.md` |

---


## Bibliographic References

### Main Books
1. Kurose, J., Ross, K. (2021). *Computer Networking: A Top-Down Approach*, 8th Ed. Pearson.
2. Rhodes, B., Goetzen, J. (2014). *Foundations of Python Network Programming*. Apress.

### Relevant RFCs
- RFC 791 – Internet protocol (IPv4)
- RFC 8200 – Internet protocol, Version 6 (IPv6)
- RFC 1918 – Address Allocation for Private Internets
- RFC 4291 – IP Version 6 Addressing Architecture

### Online Resources
- Mininet Documentation: http://mininet.org/walkthrough/
- Subnet Calculator: https://www.subnet-calculator.com/

---


## Licence

Educational materials for academic use.  
© 2025 Bucharest University of Economic Studies – CSIE  
Department of Economic Informatics and Cybernetics

---


*Revolvix&Hypotheticalandrei*
