# Week 11 – Starter Kit: Application Protocols and Distributed Applications

## 📋 Contents

- [Overview](#overview)
- [Kit Structure](#kit-structure)
- [System Requirements](#system-requirements)
- [Quick Installation](#quick-installation)
- [Usage Guide](#usage-guide)
- [Troubleshooting](#troubleshooting)

---

## Overview

### What We Will Learn

**LECTURE 11 – Application Protocols: FTP, DNS, SSH**
- FTP architecture and operation (control vs data, active vs passive)
- DNS: hierarchical resolution, TTL, caching, DNSSEC
- SSH: authentication, channels, port forwarding, automation

**SEMINAR 11 – Distributed Applications with Load Balancing**
- Reverse proxy: concept and implementation with Nginx
- Load balancing algorithms: Round-Robin, Least Connections, IP Hash
- Container orchestration with Docker Compose
- Custom LB implementation in Python

### Why It Matters

The FTP, DNS and SSH protocols represent the operational foundations of the modern Internet. Load balancing and reverse proxies are essential for web application scalability. Understanding these concepts is critical for any programmer working with distributed systems.

---

## Kit Structure

```
starterkit/
├── README.md              # This file
├── Makefile               # Command automation (make help)
├── requirements.txt       # Python dependencies
│
├── scripts/               # Shell scripts for setup and demos
│   ├── setup.sh           # Dependency installation
│   ├── cleanup.sh         # Environment cleanup
│   ├── verify.sh          # Installation verification
│   └── capture.sh         # Traffic capture
│
├── python/
│   ├── utils/
│   │   └── net_utils.py   # Common network utilities
│   └── exercises/
│       ├── ex_11_01_backend.py       # Simple HTTP server
│       ├── ex_11_02_loadbalancer.py  # Custom LB with 3 algorithms
│       ├── ex_11_03_dns_client.py    # Educational DNS client
│       └── ex_11_04_ftp_client.py    # Demonstrative FTP client
│
├── mininet/
│   ├── topologies/
│   │   ├── topo_11_base.py      # LB topology with 3 backends
│   │   └── topo_11_extended.py  # Topology with failover
│   └── scenarios/
│       └── scenario_11_tasks.md # Mininet tasks
│
├── docker/
│   ├── nginx_compose/     # Nginx + 3 backends stack
│   ├── custom_lb_compose/ # Custom Python LB stack
│   ├── ftp_demo/          # Active/passive FTP demo
│   ├── dns_demo/          # DNS TTL/caching demo
│   └── ssh_demo/          # SSH provisioning demo
│
├── docs/
│   ├── curs.md            # Complete lecture material
│   ├── seminar.md         # Complete seminar material
│   ├── lab.md             # Laboratory guide
│   ├── rubrici.md         # Assessment criteria
│   ├── checklist.md       # Teaching framework checklist
│   └── slide_outlines/    # Presentation outlines
│
├── teoria/                # Detailed theoretical explanations
│   ├── 01_ftp_protocol.md
│   ├── 02_dns_protocol.md
│   ├── 03_ssh_protocol.md
│   ├── 04_reverse_proxy.md
│   └── 05_load_balancing.md
│
├── pcap/                  # Example captures
│   └── README.md
│
└── assets/                # Visual resources
    └── logo.svg
```

---

## System Requirements

### Recommended Environment
- **OS**: Ubuntu 22.04+ (CLI-only VirtualBox VM recommended)
- **RAM**: minimum 2GB (4GB for all demos simultaneously)
- **Disk**: 5GB free
- **Network**: Internet access for Docker image pulls

### Required Software

| Component | Version | Verification |
|-----------|---------|--------------|
| Python | 3.10+ | `python3 --version` |
| Docker | 24.0+ | `docker --version` |
| Docker Compose | 2.20+ | `docker compose version` |
| Mininet | 2.3+ | `mn --version` |
| Wireshark/tshark | 4.0+ | `tshark --version` |
| netcat | any | `nc -h` |
| curl | any | `curl --version` |

---

## Quick Installation

```bash
# 1. Clone / extract kit
cd /path/to/starterkit

# 2. Automatic setup (requires sudo)
make setup

# 3. Verify installation
make verify

# 4. View available commands
make help
```

### Manual Installation (if needed)

```bash
# Python deps
pip3 install --break-system-packages -r requirements.txt

# Mininet (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y mininet openvswitch-switch

# Docker (if not installed)
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
```

---

## Usage Guide

### Quick Demos

```bash
# Nginx Load Balancer demo
make demo-nginx

# Custom Python Load Balancer demo
make demo-custom-lb

# Mininet demo (requires sudo)
make demo-mininet

# Educational DNS demo
make demo-dns

# All demos sequentially
make demo-all
```

### Standalone Python Exercises

```bash
# Start 3 backends
make backends-start

# Start load balancer (round-robin)
make lb-start

# Testing
curl http://localhost:8080/
curl http://localhost:8080/
curl http://localhost:8080/

# Stop
make backends-stop
make lb-stop
```

### Traffic Capture

```bash
# Capture on port 8080
make capture-traffic

# Or manually with tshark
tshark -i any -f "tcp port 8080" -c 20
```

### Benchmark

```bash
# Apache Bench (1000 req, 10 concurrent)
make benchmark

# Heavy benchmark
make benchmark-heavy
```

---

## Troubleshooting

### Common Problems

#### "Permission denied" with Docker
```bash
sudo usermod -aG docker $USER
# Logout and login again
```

#### "Connection refused" to containers
```bash
# Check if containers are running
docker ps

# Restart stack
make clean
make demo-nginx
```

#### Mininet does not start
```bash
# Clean previous state
sudo mn -c

# Verify OVS
sudo service openvswitch-switch restart
```

#### Port already in use
```bash
# Identify process
sudo lsof -i :8080

# Or complete cleanup
make clean
```

### Environment Verification

```bash
# Run all verifications
make verify

# Expected output:
# [OK] Python 3.x
# [OK] Docker running
# [OK] Mininet available
# [OK] tshark available
```

---

## Connection to the Team Project

### Week 11 Incremental Artefact

Teams must deliver:
1. **LB Architecture**: Topology diagram with reverse proxy
2. **Nginx Configuration**: Working `nginx.conf` for the team project
3. **Deployment Script**: Docker Compose for starting the entire stack

### Project Integration

This week's components integrate as follows:
- The reverse proxy becomes the entry point into the team application
- Load balancing enables scaling of backend components
- DNS knowledge is useful for custom network configurations

---

## Additional Resources

### Official Documentation
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Mininet Walkthrough](http://mininet.org/walkthrough/)
- [RFC 959 - FTP](https://tools.ietf.org/html/rfc959)
- [RFC 1035 - DNS](https://tools.ietf.org/html/rfc1035)
- [RFC 4251 - SSH Architecture](https://tools.ietf.org/html/rfc4251)

### Course Bibliography
- Kurose & Ross, "Computer Networking: A Top-Down Approach", 8th Ed.
- Rhodes & Goetzen, "Foundations of Python Network Programming"

---

*Revolvix&Hypotheticalandrei*
