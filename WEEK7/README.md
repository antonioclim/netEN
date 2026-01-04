# Starterkit Week 6 – Computer Networks

## NAT/PAT, ARP, DHCP, NDP, ICMP & SDN (Software-Defined Networking)

**Course:** Computer Networks  
**Programme:** Business Informatics, ASE-CSIE  
**Week:** 6 (Semester 2, Year III)  
**Academic Year:** 2025-2026

---

## Overview

This kit integrates theoretical and practical materials for **Lecture 6** (NAT/PAT, ARP, DHCP, NDP, ICMP) and **Seminar 6** (SDN, simulated topologies, traffic analysis). The progressive structure allows students to build solid knowledge before applying it in practical exercises simulated with Mininet and OpenFlow controllers.

### Learning Objectives

After completing this module, students will be able to:

**Fundamental Knowledge:**
1. Recognise and define network layer support mechanisms (NAT, ARP, DHCP, NDP, ICMP)
2. Explain why IPv4 exhaustion led to NAT/PAT adoption and the trade-offs involved

**Conceptual Understanding:**
3. Distinguish between static NAT, dynamic NAT and PAT (NAT overload) – purpose, mechanism, use cases
4. Understand control plane/data plane separation in SDN architecture and implications for flexibility

**Practical Application:**
5. Apply static routing configurations in a simulated topology with three routers
6. Configure NAT/MASQUERADE using iptables on a Linux router

**Analysis:**
7. Analyse network traffic using CLI tools (tcpdump, tshark, ovs-ofctl)
8. Compare traffic behaviour before and after applying SDN policies

**Evaluation:**
9. Evaluate the impact of SDN policies on connectivity (allow/block per protocol/port)
10. Assess the advantages and limitations of NAT/PAT in real-world contexts

**Synthesis:**
11. Create TCP/UDP client-server applications for traffic generation
12. Implement custom OpenFlow policies in an SDN controller

---

## Kit Structure

```
starterkit_s6/
├── README.md                    # This file
├── CHANGELOG.md                 # Change history
├── Makefile                     # Main automation
├── requirements.txt             # Python dependencies
│
├── artifacts/                   # Generated artefacts (demo.log, demo.pcap, validation.txt)
│
├── python/                      # Common Python utilities
│   └── utils/                   # Shared utilities module
│       ├── __init__.py
│       └── network_utils.py     # IP/port constants, helpers
│
├── seminar/                     # Practical materials for seminar
│   ├── mininet/topologies/      # Mininet topology files
│   │   ├── topo_nat.py          # Private network + NAT router
│   │   └── topo_sdn.py          # SDN topology with OpenFlow switch
│   └── python/                  # Python code
│       ├── apps/                # TCP/UDP applications for traffic
│       │   ├── nat_observer.py  # NAT translation observation
│       │   ├── tcp_echo.py      # TCP echo server/client (port 9090)
│       │   └── udp_echo.py      # UDP echo server/client (port 9091)
│       ├── controllers/         # SDN controller (OS-Ken)
│       │   └── sdn_policy_controller.py
│       └── exercises/           # Student exercise templates
│
├── scripts/                     # Automation scripts
│   ├── setup.sh                 # Complete dependency installation
│   ├── cleanup.sh               # Artefact and process cleanup
│   ├── run_all.sh               # Automated demo → artifacts/
│   ├── run_nat_demo.sh          # Launch NAT demo
│   └── run_sdn_demo.sh          # Launch SDN demo
│
├── docker/                      # Docker support
│   └── Dockerfile               # Container with all dependencies
│
├── pcap/                        # Packet captures
│
├── docs/                        # Documentation and markdown source
│   ├── curs.md                  # Complete theoretical content
│   ├── seminar.md               # Seminar guide
│   ├── lab.md                   # Step-by-step laboratory
│   ├── checklist.md             # Teaching framework checklist
│   └── rubrici.md               # Assessment criteria
│
├── slides/                      # Presentations (outlines)
│
└── tests/                       # Automated verification
    ├── smoke_test.sh            # Basic functionality test
    └── expected_outputs.md      # Reference for correct output
```

---

## Technical Requirements

### Recommended Working Environment
- **OS:** Linux (Ubuntu 22.04+ or Debian 12+)
- **Alternatives:** VirtualBox VM, WSL2 with Ubuntu, Docker container
- **Python:** 3.10+ (compatible with 3.8+ for OS-Ken)
- **Privileges:** sudo required for Mininet and packet capture

### Required System Packages
```bash
# One-time installation
sudo apt-get update && sudo apt-get install -y \
  python3 python3-pip python3-venv \
  mininet openvswitch-switch \
  iproute2 iputils-ping traceroute \
  tcpdump tshark iptables \
  netcat-openbsd arping bridge-utils
```

### Python Packages
```bash
pip install --break-system-packages os-ken scapy
```

---

## Quick Installation

### Quickstart (10 commands)

```bash
# 1. Extract and navigate
cd starterkit_s6

# 2. Setup (first time)
make setup

# 3. Verify tools
make check

# 4. Automated demo (produces artifacts/)
sudo make run-all

# 5. Verify artefacts
ls -la artifacts/
cat artifacts/validation.txt

# 6. Interactive NAT demo
make nat-demo

# 7. Interactive SDN demo
make sdn-demo

# 8. Run smoke test
make smoke-test

# 9. Cleanup
make clean

# 10. Complete reset
make reset
```

### Week 6 IP Plan

| Resource | Address |
|----------|---------|
| SDN Subnet | 10.0.6.0/24 |
| Gateway | 10.0.6.1 |
| h1 | 10.0.6.11 |
| h2 | 10.0.6.12 |
| h3 | 10.0.6.13 |
| Server | 10.0.6.100 |

### Port Plan

| Port | Usage |
|------|-------|
| 9090 | TCP App (echo server/client) |
| 9091 | UDP App (echo server/client) |
| 6633 | SDN Controller (OpenFlow) |
| 5600-5699 | Week 6 custom ports |

### Option 1: Makefile (recommended)
```bash
# Extract the kit and enter the directory
cd starterkit_s6

# Run complete setup
make setup

# Verification
make check
```

### Option 2: Manual
```bash
cd starterkit_s6

# Install system packages
sudo apt-get install -y python3 python3-pip mininet openvswitch-switch tcpdump tshark

# Install Python packages
pip3 install --break-system-packages os-ken scapy

# Verification
make check
```

---

## Recommended Workflow

### For Lecture (100 minutes)

| Segment | Duration | Content |
|---------|----------|---------|
| Context & IPv4 | 15 min | Address exhaustion, RFC1918, global problem |
| NAT/PAT | 30 min | Static vs. dynamic vs. PAT, tables, trade-offs |
| ARP / Proxy ARP | 15 min | IP→MAC resolution, broadcast vs. unicast |
| DHCP | 15 min | DORA steps, lease, relay |
| NDP (IPv6) | 15 min | Neighbor/Router Discovery, SLAAC |
| ICMP | 10 min | Ping, traceroute, error messages |

### For Seminar (100 minutes)

| Segment | Duration | Content |
|---------|----------|---------|
| Warm-up verification | 15 min | Environment check, basic routing |
| NAT/PAT | 40 min | NAT topology, MASQUERADE observation |
| SDN & OpenFlow | 35 min | Controller, policies, flow tables |
| Reflection | 10 min | Deliverables, questions |

### Quick Demo Commands

```bash
# NAT demo
make nat-demo

# SDN demo (starts controller automatically)
make sdn-demo

# Check controller status
make controller-status

# Cleanup
make clean
```

---

## Student Deliverables

| Deliverable | Weight | Description |
|-------------|--------|-------------|
| `nat_output.txt` | 30% | Command output + PAT observations |
| `sdn_output.txt` | 40% | Flow table dumps + control/data plane analysis |
| `reflectie.txt` | 20% | End-to-end principles, SDN vs. traditional comparison |
| `routing_output.txt` | 10% bonus | Traceroute before/after route modification |

---

## Quick Troubleshooting

| Problem | Probable Cause | Solution |
|---------|----------------|----------|
| `mn: command not found` | Mininet not installed | `sudo apt install mininet` |
| OVS not starting | Service stopped | `sudo systemctl restart openvswitch-switch` |
| Controller not connecting | Port blocked/other process | Check port 6633: `ss -ltn \| grep 6633` |
| SDN ping very slow | Missing flow rules | Check with `ovs-ofctl dump-flows` |
| NAT not working | IP forwarding disabled | `sysctl -w net.ipv4.ip_forward=1` |
| Permission denied tcpdump | Missing privileges | Use `sudo` |
| Artefacts from previous runs | Remaining interfaces/processes | `make clean` or `sudo mn -c` |
| `os_ken` import fail | Module not installed | `pip install os-ken` |

---

## References

1. **Kurose, J., Ross, K.** (2016). *Computer Networking: A Top-Down Approach*, 7th Edition. Pearson.
2. **Rhodes, B., Goetzen, J.** (2014). *Foundations of Python Network Programming*. Apress.
3. **RFC 1918** – Address Allocation for Private Internets
4. **RFC 5737** – IPv4 Address Blocks Reserved for Documentation
5. **RFC 4861** – Neighbor Discovery for IP version 6 (IPv6)
6. **OpenFlow Specification 1.3** – Open Networking Foundation

---

## Useful Links

- [Mininet Walkthrough](http://mininet.org/walkthrough/)
- [OS-Ken Documentation](https://osrg.github.io/os-ken/)
- [Open vSwitch Manual](https://docs.openvswitch.org/)
- [Wireshark Display Filter Reference](https://www.wireshark.org/docs/dfref/)

---

## Licence and Usage

Teaching material for internal ASE-CSIE use.  
Material authors: **Revolvix&Hypotheticalandrei**

---

*Generated for academic year 2025-2026 – Week 6*
