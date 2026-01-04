# Computer Networks – Laboratory Starter Kits (WEEK 1–14)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Mininet](https://img.shields.io/badge/Mininet-2.3.0-green?style=flat)](http://mininet.org)
[![Docker](https://img.shields.io/badge/Docker-24.0+-2496ED?style=flat&logo=docker&logoColor=white)](https://docker.com)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04_LTS-E95420?style=flat&logo=ubuntu&logoColor=white)](https://ubuntu.com)
[![Licence](https://img.shields.io/badge/Licence-MIT-yellow?style=flat)](LICENCE)

**Course:** Computer Networks (25.0205IF3.2-0003)  
**Programme:** Economic Informatics, Year III, Semester 2  
**Institution:** Bucharest University of Economic Studies (ASE), Faculty of Cybernetics, Statistics and Economic Informatics (CSIE)  
**Academic Year:** 2025–2026  

---

## 📋 Table of Contents

- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Weekly Topics](#weekly-topics)
- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Clone Individual Weeks](#clone-individual-weeks)
- [Clone Entire Repository](#clone-entire-repository)
- [Repository Statistics](#repository-statistics)
- [IP Addressing Plan](#ip-addressing-plan)
- [Technologies Used](#technologies-used)
- [Authors and Contributors](#authors-and-contributors)
- [Licence](#licence)
- [Appendix: Ubuntu Server Installation Guide](#appendix-ubuntu-server-2404-lts-installation-guide)

---

## Overview

This repository contains comprehensive starter kits for the **Computer Networks** course, covering all 14 weeks of the semester. Each weekly kit provides:

- **Theoretical content** in structured Markdown documents
- **Practical Python exercises** with solutions
- **Docker Compose environments** for reproducible demonstrations
- **Mininet network topologies** for network simulation
- **Automated testing scripts** for validation
- **Packet capture examples** (PCAP files)

The materials are designed for a **Linux CLI-only minimal VM** environment (Ubuntu Server 24.04 LTS) running in VirtualBox and follow a progressive learning approach from basic networking concepts to advanced distributed systems.

---

## Repository Structure

```
netEN/
├── PREREQ/                    # Prerequisites and environment setup
├── APPENDIX(week0)/           # Supplementary materials and references
│
├── WEEK1/                     # Network Fundamentals
├── WEEK2/                     # OSI/TCP-IP Models & Socket Programming
├── WEEK3/                     # UDP Broadcast/Multicast & TCP Tunnelling
├── WEEK4/                     # Physical Layer, Data Link & Custom Protocols
├── WEEK5/                     # Network Layer: IP Addressing & Subnetting
├── WEEK6/                     # NAT/PAT, ARP, DHCP, NDP, ICMP & SDN
├── WEEK7/                     # Packet Capture, Filtering & Defensive Probing
├── WEEK8/                     # Transport Layer, HTTP Server & Reverse Proxy
├── WEEK9/                     # Session/Presentation Layers & File Protocols
├── WEEK10/                    # HTTP/HTTPS, REST, SOAP & Network Services
├── WEEK11/                    # Application Protocols & Distributed Applications
├── WEEK12/                    # E-mail Protocols & Remote Procedure Call (RPC)
├── WEEK13/                    # IoT and Network Security
├── WEEK14/                    # Integrated Review & Project Evaluation
│
└── README.md                  # This file
```

### Standard Weekly Kit Structure

Each `WEEK<N>/` directory follows a consistent organisation:

```
WEEK<N>/
├── README.md              # Week overview and quick start guide
├── Makefile               # Build automation (make setup, make demo, make clean)
├── requirements.txt       # Python dependencies
│
├── docs/                  # Documentation
│   ├── seminar.md         # Seminar guide
│   ├── checklist.md       # Teaching framework checklist
│   └── cheatsheet.md      # Quick reference commands
│
├── python/                # Python source code
│   ├── exercises/         # Practical exercises
│   ├── apps/              # Complete applications
│   ├── utils/             # Utility modules
│   └── templates/         # Code templates for students
│
├── mininet/               # Network simulation
│   ├── topologies/        # Mininet topology definitions
│   └── scenarios/         # Lab scenario scripts
│
├── docker/                # Containerisation
│   ├── Dockerfile         # Container image definition
│   └── docker-compose.yml # Multi-container orchestration
│
├── scripts/               # Automation scripts
│   ├── setup.sh           # Environment setup
│   ├── run_all.sh         # Execute all demos
│   ├── cleanup.sh         # Clean generated files
│   └── capture_traffic.sh # Packet capture automation
│
├── tests/                 # Automated testing
│   ├── smoke_test.sh      # Quick validation
│   └── expected_outputs.md# Expected results reference
│
├── configs/               # Configuration files
├── artifacts/             # Generated outputs (logs, captures)
└── pcap/                  # Packet capture files
```

---

## Weekly Topics

| Week | Topic | Key Technologies |
|:----:|-------|------------------|
| **1** | Network Fundamentals: Concepts, Components and Classifications | `ping`, `traceroute`, `netstat`, `ss`, `tcpdump` |
| **2** | OSI/TCP-IP Architectural Models & Socket Programming | Python sockets, `scapy`, `dpkt`, concurrent servers |
| **3** | UDP Broadcast/Multicast & TCP Tunnelling | UDP sockets, multicast groups, port forwarding |
| **4** | Physical Layer, Data Link & Custom Protocols | Binary protocols, `struct`, CRC32, Ethernet frames |
| **5** | Network Layer: IP Addressing & Subnetting | CIDR, FLSM, VLSM, IPv6, subnet calculators |
| **6** | NAT/PAT, ARP, DHCP, NDP, ICMP & SDN | `iptables`, Open vSwitch, `os-ken` controller |
| **7** | Packet Capture, Filtering & Defensive Probing | `tcpdump`, `tshark`, Wireshark, `nmap`, `scapy` |
| **8** | Transport Layer, HTTP Server & Reverse Proxy | TCP handshake, HTTP/1.1, Nginx, load balancing |
| **9** | Session/Presentation Layers & File Protocols | FTP active/passive, `pyftpdlib`, binary framing |
| **10** | HTTP/HTTPS, REST, SOAP & Network Services | TLS, DNS, SSH (`paramiko`), REST API levels |
| **11** | Application Protocols & Distributed Applications | DNS caching, Nginx LB algorithms, health checks |
| **12** | E-mail Protocols & Remote Procedure Call (RPC) | SMTP, POP3, IMAP, JSON-RPC, XML-RPC, gRPC |
| **13** | IoT and Network Security | MQTT (`paho`), Mosquitto, vulnerability scanning |
| **14** | Integrated Review & Project Evaluation | Full-stack integration, troubleshooting methodology |

---

## System Requirements

### Minimum Hardware

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 4 GB | 8 GB |
| CPU Cores | 2 | 4 |
| Disk Space | 25 GB | 50 GB |
| Network | NAT + Host-Only | NAT + Host-Only |

### Software Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| **Ubuntu Server** | 24.04 LTS | Host operating system |
| **Python** | 3.10+ | Programming language |
| **Docker CE** | 24.0+ | Containerisation |
| **Mininet** | 2.3.0+ | Network simulation |
| **Open vSwitch** | 3.1+ | Software-defined networking |
| **Git** | 2.40+ | Version control |

### Recommended VirtualBox Settings

- **Type:** Linux / Ubuntu (64-bit)
- **RAM:** 4096–8192 MB
- **CPU:** 4 cores with PAE/NX and VT-x/AMD-V enabled
- **Disk:** 25–50 GB dynamically allocated VDI
- **Network Adapter 1:** NAT (Internet access)
- **Network Adapter 2:** Host-Only Adapter (SSH from host)

---

## Quick Start

### Option 1: Clone Entire Repository

```bash
# Clone the complete repository
git clone https://github.com/antonioclim/netEN.git

# Navigate to desired week
cd netEN/WEEK1

# Run setup and demo
make setup
make demo
```

### Option 2: Clone Specific Week (Sparse Checkout)

```bash
# Example: Clone only WEEK3
cd ~ && git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK3 \
  && cd WEEK3 && git sparse-checkout set WEEK3 \
  && shopt -s dotglob && mv WEEK3/* . && rmdir WEEK3 \
  && find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

### Option 3: Download ZIP Archive

Download individual weeks from the GitHub web interface or use:

```bash
# Download and extract specific week
wget https://github.com/antonioclim/netEN/archive/refs/heads/main.zip
unzip main.zip
mv netEN-main/WEEK5 ~/WEEK5
```

---

## Clone Individual Weeks

Each week can be cloned independently using Git sparse checkout. Replace `<N>` with the week number (1–14):

### One-Liner Command

```bash
cd ~ && git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK<N> \
  && cd WEEK<N> && git sparse-checkout set WEEK<N> \
  && shopt -s dotglob && mv WEEK<N>/* . && rmdir WEEK<N> \
  && find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

### Step-by-Step Commands

```bash
# 1. Navigate to home directory
cd ~

# 2. Clone repository with sparse checkout (downloads only metadata initially)
git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK<N>

# 3. Enter the cloned directory
cd WEEK<N>

# 4. Configure sparse checkout to fetch only the desired week
git sparse-checkout set WEEK<N>

# 5. Flatten directory structure
shopt -s dotglob
mv WEEK<N>/* .
rmdir WEEK<N>

# 6. Make scripts executable
find . -type f -name "*.sh" -exec chmod +x {} \;
find . -type f -name "*.py" -exec chmod +x {} \;

# 7. Verify setup
ls -la
./scripts/setup.sh
```

---

## Clone Entire Repository

```bash
# Full clone with complete history
git clone https://github.com/antonioclim/netEN.git
cd netEN

# Make all scripts executable
find . -type f -name "*.sh" -exec chmod +x {} \;
find . -type f -name "*.py" -exec chmod +x {} \;

# Navigate to specific week
cd WEEK1
make setup
make verify
make demo
```

---

## Repository Statistics

| Metric | Count |
|--------|-------|
| **Weekly Kits** | 14 |
| **Python Files** | 187 |
| **Shell Scripts** | 88 |
| **Markdown Documents** | 146 |
| **Docker Compose Files** | 21 |
| **Mininet Topologies** | 37 |
| **Dockerfiles** | 17 |
| **Total Size (uncompressed)** | ~5.2 MB |

### Language Distribution

- **Python:** 55.2%
- **Shell:** 22.3%
- **JavaScript:** 7.9%
- **Makefile:** 7.4%
- **HTML:** 5.3%
- **CSS:** 1.0%
- **Dockerfile:** 0.9%

---

## IP Addressing Plan

Each week uses a consistent IP addressing scheme derived from the week number to avoid conflicts:

| Week | Network | Gateway | Host Range | Ports |
|:----:|---------|---------|------------|-------|
| 1 | 10.0.1.0/24 | 10.0.1.1 | 10.0.1.2–254 | 5100–5199 |
| 2 | 10.0.2.0/24 | 10.0.2.1 | 10.0.2.2–254 | 5200–5299 |
| 3 | 10.0.3.0/24 | 10.0.3.1 | 10.0.3.2–254 | 5300–5399 |
| 4 | 10.0.4.0/24 | 10.0.4.1 | 10.0.4.2–254 | 5400–5499 |
| 5 | 10.0.5.0/24 | 10.0.5.1 | 10.0.5.2–254 | 5500–5599 |
| 6 | 10.0.6.0/24 | 10.0.6.1 | 10.0.6.2–254 | 5600–5699 |
| 7 | 10.0.7.0/24 | 10.0.7.1 | 10.0.7.2–254 | 5700–5799 |
| 8 | 10.0.8.0/24 | 10.0.8.1 | 10.0.8.2–254 | 8080, 9001–9003 |
| 9 | 10.0.9.0/24 | 10.0.9.1 | 10.0.9.2–254 | 2121, 60000–60100 |
| 10 | 10.0.10.0/24 | 10.0.10.1 | 10.0.10.2–254 | 5353, 2222 |
| 11 | 10.0.11.0/24 | 10.0.11.1 | 10.0.11.2–254 | 8080 |
| 12 | 10.0.12.0/24 | 10.0.12.1 | 10.0.12.2–254 | 1025, 8080, 50051 |
| 13 | 10.0.13.0/24 | 10.0.13.1 | 10.0.13.2–254 | 1883, 8080 |
| 14 | 172.20.0.0/24 | 172.20.0.1 | 172.20.0.2–254 | 8080, 9000 |

---

## Technologies Used

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.10+ | Primary programming language |
| **Mininet** | 2.3.0 | Network emulation and simulation |
| **Docker** | 24.0+ | Container orchestration |
| **Open vSwitch** | 3.1+ | Software-defined networking |
| **os-ken** | 2.4+ | SDN controller (Ryu fork) |

### Python Libraries

| Library | Purpose |
|---------|---------|
| `scapy` | Packet manipulation and analysis |
| `dpkt` | Low-level packet parsing |
| `flask` | HTTP server framework |
| `requests` | HTTP client library |
| `paramiko` | SSH client implementation |
| `pyftpdlib` | FTP server implementation |
| `dnslib` | DNS protocol implementation |
| `dnspython` | DNS toolkit |
| `paho-mqtt` | MQTT client for IoT |
| `grpcio` | gRPC framework |
| `protobuf` | Protocol Buffers serialisation |

### Network Tools

| Tool | Purpose |
|------|---------|
| `tcpdump` | Packet capture (CLI) |
| `tshark` | Wireshark CLI interface |
| `nmap` | Network scanning and enumeration |
| `netcat` | TCP/UDP utility |
| `iperf3` | Network performance testing |
| `curl` | HTTP client |
| `dig` | DNS lookup utility |

---

## Authors and Contributors

### Course Materials

- **Assoc. Prof. TOMA Andrei** – Course coordinator
- **Assoc. Prof. TIMOFTE Carmen Manuela** – Lecturer
- **Lecturer ILIE-NEMEDI Iulian** – Laboratory coordinator
- **Teaching Asst. CÎMPEANU Ionuț Alexandru** – Laboratory assistant

### Code Development

- **Revolvix** – Starter kit development and automation
- **Hypotheticalandrei** – Docker environments and testing

---

## Licence

This repository is licensed under the **MIT Licence** for code components. Educational materials remain the intellectual property of ASE-CSIE and the teaching staff.

```
MIT Licence

Copyright (c) 2025 ASE-CSIE Computer Networks Course

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Permission denied running scripts | `chmod +x scripts/*.sh` |
| Docker permission denied | `sudo usermod -aG docker $USER` then logout/login |
| Mininet not starting | `sudo mn -c` to clean up previous runs |
| Python module not found | `pip install -r requirements.txt --break-system-packages` |
| Port already in use | `sudo ss -tulpn | grep <port>` then kill process |
| TShark permission denied | `sudo usermod -aG wireshark $USER` |

### Useful Commands

```bash
# Clean Mininet state
sudo mn -c

# Remove all Docker containers and images
docker system prune -a --volumes

# Clear pip cache
pip cache purge

# Check open ports
sudo ss -tulpn

# View system logs
journalctl -xe --no-pager | tail -50

# Monitor network interfaces
watch -n 1 'ip -s link'
```

---

## Contact and Support

- **Repository Issues:** [https://github.com/antonioclim/netEN/issues](https://github.com/antonioclim/netEN/issues)
- **Course Platform:** ASE CSIE e-Learning
- **Teaching Staff:** Contact via university email

---

# Appendix: Ubuntu Server 24.04 LTS Installation Guide

## Complete Installation Guide for Computer Networks Laboratory

**Target Environment:** Ubuntu Server 24.04 LTS (CLI-only) as VirtualBox Guest  
**Purpose:** Preparing a fully functional networking laboratory for WEEK 1–14  
**Generated:** January 2026

---

## Table of Contents

1. [Initial VirtualBox Configuration](#1-initial-virtualbox-configuration)
2. [System Update and Essential Packages](#2-system-update-and-essential-packages)
3. [Network Tools](#3-network-tools)
4. [Python and Libraries](#4-python-and-libraries)
5. [Docker and Docker Compose](#5-docker-and-docker-compose)
6. [Mininet and Open vSwitch](#6-mininet-and-open-vswitch)
7. [Wireshark/TShark](#7-wiresharktshark)
8. [Additional Configuration](#8-additional-configuration)
9. [Transfer and Organise Materials](#9-transfer-and-organise-materials)
10. [Verification Script](#10-verification-script)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Initial VirtualBox Configuration

### 1.1 Virtual Machine Settings

Create a new VM with the following configuration:

| Setting | Value |
|---------|-------|
| **Name** | Ubuntu-Networks |
| **Type** | Linux |
| **Version** | Ubuntu (64-bit) |
| **RAM** | 4096–8192 MB |
| **CPU** | 4 cores |
| **Disk** | 25–50 GB (dynamically allocated) |

### 1.2 Network Adapters

Configure two network adapters:

**Adapter 1 (NAT):**
- Attached to: NAT
- Purpose: Internet access for package installation

**Adapter 2 (Host-Only):**
- Attached to: Host-Only Adapter
- Name: vboxnet0 (create if necessary)
- IP: 192.168.56.x range

### 1.3 Enable Nested Virtualisation (Optional)

Required for running nested VMs or advanced container scenarios:

```bash
# PowerShell (Windows host) - run as Administrator
# Replace "Ubuntu-Networks" with your VM name
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" modifyvm "Ubuntu-Networks" --nested-hw-virt on
```

```bash
# Linux/macOS host
VBoxManage modifyvm "Ubuntu-Networks" --nested-hw-virt on
```

### 1.4 Install Guest Additions

#### Method A: From VirtualBox CD Image

```bash
# Mount Guest Additions CD via VirtualBox menu: Devices → Insert Guest Additions CD
sudo mount /dev/cdrom /mnt
sudo /mnt/VBoxLinuxAdditions.run
sudo reboot
```

#### Method B: From Ubuntu Repositories (Recommended)

```bash
sudo apt update
sudo apt install -y virtualbox-guest-utils virtualbox-guest-dkms
sudo reboot
```

### 1.5 Configure SSH Port Forwarding

For SSH access via NAT adapter:

```bash
# PowerShell (Windows host)
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" modifyvm "Ubuntu-Networks" --natpf1 "SSH,tcp,,2222,,22"
```

Then connect from host:

```bash
ssh -p 2222 username@127.0.0.1
```

---

## 2. System Update and Essential Packages

### 2.1 Full System Update

```bash
sudo apt update && sudo apt upgrade -y && sudo apt dist-upgrade -y
sudo apt autoremove -y && sudo apt autoclean
```

### 2.2 Build Tools and Development Packages

```bash
sudo apt install -y \
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    pkg-config \
    dkms \
    linux-headers-$(uname -r) \
    git \
    curl \
    wget \
    vim \
    nano \
    htop \
    tree \
    unzip \
    jq \
    ca-certificates \
    gnupg \
    lsb-release \
    software-properties-common \
    apt-transport-https
```

### 2.3 Configure Timezone

```bash
sudo timedatectl set-timezone Europe/Bucharest
timedatectl
```

### 2.4 SSH Server

```bash
sudo apt install -y openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh
```

---

## 3. Network Tools

### 3.1 Network Diagnostics

```bash
sudo apt install -y \
    iputils-ping \
    iputils-tracepath \
    iproute2 \
    net-tools \
    dnsutils \
    bind9-dnsutils \
    traceroute \
    mtr-tiny \
    whois \
    host
```

### 3.2 Network Connectivity

```bash
sudo apt install -y \
    netcat-openbsd \
    socat \
    curl \
    wget \
    lftp \
    openssh-client \
    telnet
```

### 3.3 Traffic Monitoring

```bash
sudo apt install -y \
    tcpdump \
    iftop \
    nethogs \
    nload \
    bmon \
    iptraf-ng \
    vnstat
```

### 3.4 Security and Scanning

```bash
sudo apt install -y \
    nmap \
    hping3 \
    iperf3 \
    arping \
    fping
```

### 3.5 Firewall Tools

```bash
sudo apt install -y \
    iptables \
    iptables-persistent \
    conntrack \
    ufw
```

### 3.6 Bridging and VLAN

```bash
sudo apt install -y \
    bridge-utils \
    vlan \
    arptables \
    ebtables
```

### 3.7 Configure Packet Capture Permissions

```bash
# Allow non-root users to capture packets
sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/tcpdump
sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/dumpcap 2>/dev/null || true
```

---

## 4. Python and Libraries

### 4.1 Python Installation

Ubuntu 24.04 includes Python 3.12 by default:

```bash
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel
```

Verify installation:

```bash
python3 --version
pip3 --version
```

### 4.2 Python Libraries Installation

> **Important:** Ubuntu 24.04 uses PEP 668 (externally managed environment). Use `--break-system-packages` flag or create a virtual environment.

```bash
# Install all required libraries
pip3 install --break-system-packages --ignore-installed \
    scapy \
    dpkt \
    pyshark \
    netifaces \
    flask \
    requests \
    dnslib \
    dnspython \
    paramiko \
    pyftpdlib \
    paho-mqtt \
    grpcio \
    grpcio-tools \
    protobuf \
    os-ken \
    PyYAML \
    colorama \
    tabulate \
    psutil \
    pytest \
    python-docx
```

### 4.3 Libraries by Week

| Week | Required Libraries |
|:----:|-------------------|
| 1–2 | `scapy`, `dpkt`, `pyshark`, `netifaces` |
| 3–4 | `struct` (built-in), `socket` (built-in), `scapy` |
| 5 | `ipaddress` (built-in), subnet calculation libraries |
| 6–7 | `scapy`, `os-ken`, `netifaces` |
| 8 | `flask`, `requests`, HTTP libraries |
| 9 | `pyftpdlib`, `ftplib` (built-in) |
| 10 | `dnslib`, `dnspython`, `paramiko`, `requests` |
| 11 | `requests`, DNS libraries |
| 12 | `grpcio`, `grpcio-tools`, `protobuf` |
| 13 | `paho-mqtt`, `scapy` |
| 14 | All above |

### 4.4 Verify Python Installation

```bash
python3 -c "
import scapy.all
import flask
import requests
import paramiko
import dns.resolver
import paho.mqtt.client
print('All core libraries imported successfully!')
"
```

---

## 5. Docker and Docker Compose

### 5.1 Add Docker Official Repository

```bash
# Remove old versions
sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Add Docker GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### 5.2 Install Docker Engine

```bash
sudo apt update
sudo apt install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin
```

### 5.3 Configure Docker for Non-Root User

```bash
sudo usermod -aG docker $USER
newgrp docker

# Verify (after logout/login)
docker run hello-world
```

### 5.4 Enable Docker Service

```bash
sudo systemctl enable docker
sudo systemctl enable containerd
sudo systemctl start docker
```

### 5.5 Verify Docker Installation

```bash
docker --version
docker compose version
docker run --rm hello-world
```

---

## 6. Mininet and Open vSwitch

### 6.1 Install Mininet

```bash
sudo apt install -y mininet
```

### 6.2 Install Open vSwitch

```bash
sudo apt install -y \
    openvswitch-switch \
    openvswitch-common \
    openvswitch-testcontroller
```

### 6.3 Enable OVS Service

```bash
sudo systemctl enable openvswitch-switch
sudo systemctl start openvswitch-switch
```

### 6.4 Verify Installation

```bash
# Check OVS status
sudo ovs-vsctl show

# Test Mininet
sudo mn --test pingall

# Clean up
sudo mn -c
```

### 6.5 Install os-ken SDN Controller

```bash
pip3 install --break-system-packages os-ken
```

---

## 7. Wireshark/TShark

### 7.1 Install TShark (CLI)

```bash
sudo apt install -y tshark
```

During installation, select "Yes" to allow non-superusers to capture packets.

### 7.2 Configure Permissions

```bash
sudo usermod -aG wireshark $USER
sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/dumpcap
```

### 7.3 Verify Installation

```bash
tshark --version
# Test capture (brief)
sudo timeout 5 tshark -i any -c 10 2>/dev/null || echo "Capture test complete"
```

---

## 8. Additional Configuration

### 8.1 Enable IP Forwarding

Required for NAT and routing scenarios:

```bash
# Temporary (immediate effect)
sudo sysctl -w net.ipv4.ip_forward=1
sudo sysctl -w net.ipv6.conf.all.forwarding=1

# Permanent (survives reboot)
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
echo "net.ipv6.conf.all.forwarding=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 8.2 Disable systemd-resolved (Optional)

Required if port 53 conflicts occur:

```bash
sudo systemctl stop systemd-resolved
sudo systemctl disable systemd-resolved
sudo rm /etc/resolv.conf
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
echo "nameserver 8.8.4.4" | sudo tee -a /etc/resolv.conf
```

### 8.3 Configure UFW Firewall Rules

```bash
# Allow common ports used by lab exercises
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 8080/tcp    # HTTP demos
sudo ufw allow 3333/tcp    # Custom protocols
sudo ufw allow 4444/tcp    # Custom protocols
sudo ufw allow 5555/tcp    # Custom protocols
sudo ufw allow 1025/tcp    # SMTP demo
sudo ufw allow 2121/tcp    # FTP demo
sudo ufw allow 1883/tcp    # MQTT

# Enable firewall (optional)
# sudo ufw enable
```

### 8.4 Create Directory Structure

```bash
mkdir -p ~/networking/{seminars,pcap,logs,scripts,docs}
mkdir -p ~/networking/seminars/{WEEK{1..14}}
```

### 8.5 Configure Git

```bash
git config --global user.name "Student Name"
git config --global user.email "student@example.com"
git config --global init.defaultBranch main
```

### 8.6 Useful Bash Aliases

Add to `~/.bashrc`:

```bash
cat >> ~/.bashrc << 'EOF'

# Docker aliases
alias dps='docker ps'
alias dpsa='docker ps -a'
alias dimg='docker images'
alias dprune='docker system prune -af'
alias dc='docker compose'
alias dcup='docker compose up -d'
alias dcdown='docker compose down'
alias dclogs='docker compose logs -f'

# Mininet aliases
alias mnc='sudo mn -c'
alias mnt='sudo mn --test pingall'

# Network aliases
alias ports='sudo ss -tulpn'
alias myip='ip -4 addr show | grep inet'
alias pingg='ping -c 4 8.8.8.8'
alias routes='ip route show'

# Quick navigation
alias week='cd ~/networking/seminars'
EOF

source ~/.bashrc
```

---

## 9. Transfer and Organise Materials

### 9.1 Clone from Repository

```bash
cd ~/networking/seminars
git clone https://github.com/antonioclim/netEN.git
```

### 9.2 Alternative: SCP from Host

```bash
# From host machine
scp -P 2222 -r ./WEEK* username@127.0.0.1:~/networking/seminars/
```

### 9.3 Alternative: VirtualBox Shared Folders

```bash
# In VM
sudo mount -t vboxsf shared_folder_name /mnt/shared
cp -r /mnt/shared/WEEK* ~/networking/seminars/
```

### 9.4 Set Permissions

```bash
cd ~/networking/seminars
find . -name "*.sh" -exec chmod +x {} \;
find . -name "*.py" -exec chmod +x {} \;
```

---

## 10. Verification Script

Create and run this script to verify the complete installation:

```bash
#!/bin/bash
# verify_installation.sh - Check all components

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

check() {
    if eval "$2" &>/dev/null; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1"
        ((ERRORS++))
    fi
}

check_warn() {
    if eval "$2" &>/dev/null; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${YELLOW}○${NC} $1 (optional)"
    fi
}

echo "═══════════════════════════════════════════════════════════"
echo "   Ubuntu Server 24.04 LTS - Installation Verification"
echo "═══════════════════════════════════════════════════════════"
echo ""

echo "▶ System Information"
echo "  Hostname: $(hostname)"
echo "  Ubuntu: $(lsb_release -d | cut -f2)"
echo "  Kernel: $(uname -r)"
echo ""

echo "▶ Core Components"
check "Python 3.10+" "python3 --version | grep -E 'Python 3\.(1[0-9]|[2-9][0-9])'"
check "pip3" "pip3 --version"
check "Git" "git --version"
check "curl" "curl --version"
check "wget" "wget --version"
echo ""

echo "▶ Docker"
check "Docker Engine" "docker --version"
check "Docker Compose" "docker compose version"
check "Docker daemon" "docker info"
check_warn "Docker (non-root)" "docker ps"
echo ""

echo "▶ Network Simulation"
check "Mininet" "which mn"
check "Open vSwitch" "sudo ovs-vsctl show"
check_warn "os-ken" "python3 -c 'import os_ken'"
echo ""

echo "▶ Network Tools"
check "tcpdump" "which tcpdump"
check "tshark" "which tshark"
check "nmap" "which nmap"
check "iperf3" "which iperf3"
check "netcat" "which nc"
echo ""

echo "▶ Python Libraries"
check "scapy" "python3 -c 'import scapy.all'"
check "flask" "python3 -c 'import flask'"
check "requests" "python3 -c 'import requests'"
check "paramiko" "python3 -c 'import paramiko'"
check "pyftpdlib" "python3 -c 'import pyftpdlib'"
check "paho-mqtt" "python3 -c 'import paho.mqtt.client'"
check "dnspython" "python3 -c 'import dns.resolver'"
check "grpcio" "python3 -c 'import grpc'"
echo ""

echo "▶ Services"
check "SSH server" "systemctl is-active ssh"
check "Docker service" "systemctl is-active docker"
check "OVS service" "systemctl is-active openvswitch-switch"
echo ""

echo "▶ Permissions"
check_warn "User in docker group" "groups | grep -q docker"
check_warn "User in wireshark group" "groups | grep -q wireshark"
check_warn "IP forwarding enabled" "sysctl net.ipv4.ip_forward | grep -q '= 1'"
echo ""

echo "═══════════════════════════════════════════════════════════"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}All required components installed successfully!${NC}"
else
    echo -e "${RED}$ERRORS required component(s) missing or misconfigured.${NC}"
fi
echo "═══════════════════════════════════════════════════════════"

exit $ERRORS
```

Save and run:

```bash
chmod +x verify_installation.sh
./verify_installation.sh
```

---

## 11. Troubleshooting

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| **Docker permission denied** | `sudo usermod -aG docker $USER` then logout/login |
| **Mininet error: Exception** | `sudo mn -c` to clean up then retry |
| **TShark permission denied** | `sudo usermod -aG wireshark $USER` and `sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/dumpcap` |
| **Python externally-managed-environment** | Use `--break-system-packages` flag or create venv |
| **pip RECORD file error** | Use `--ignore-installed` flag |
| **Port 53 already in use** | Disable systemd-resolved (see section 8.2) |
| **Mininet processes not cleaned** | `sudo mn -c` followed by `sudo killall -9 ovs-testcontroller` |

### Diagnostic Commands

```bash
# Check open ports
sudo ss -tulpn

# Check Docker status
docker info
docker ps -a

# Check OVS status
sudo ovs-vsctl show

# View system logs
journalctl -xe --no-pager | tail -50

# Check disk space
df -h

# Check memory usage
free -h

# List network interfaces
ip link show

# Check routing table
ip route show
```

### Complete Installation Script

For automated installation, use this all-in-one script:

```bash
#!/bin/bash
# install_networking_lab.sh
# Complete installation script for Computer Networks laboratory

set -e

echo "Starting complete installation..."

# System update
sudo apt update && sudo apt upgrade -y

# Essential packages
sudo apt install -y build-essential git curl wget vim nano htop tree unzip jq \
    ca-certificates gnupg lsb-release software-properties-common apt-transport-https

# Network tools
sudo apt install -y iputils-ping iproute2 net-tools dnsutils traceroute mtr-tiny \
    whois netcat-openbsd socat tcpdump iftop nethogs nload nmap hping3 iperf3 \
    iptables iptables-persistent bridge-utils vlan tshark

# Python
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Python libraries
pip3 install --break-system-packages --ignore-installed \
    scapy dpkt flask requests dnslib dnspython paramiko pyftpdlib \
    paho-mqtt grpcio grpcio-tools protobuf os-ken PyYAML colorama psutil

# Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER

# Mininet and OVS
sudo apt install -y mininet openvswitch-switch openvswitch-common

# Enable services
sudo systemctl enable docker openvswitch-switch ssh
sudo systemctl start docker openvswitch-switch ssh

# Permissions
sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/tcpdump
sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/dumpcap 2>/dev/null || true
sudo usermod -aG wireshark $USER 2>/dev/null || true

# IP forwarding
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Directory structure
mkdir -p ~/networking/{seminars,pcap,logs,scripts,docs}

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Installation complete! Please logout and login again for"
echo "group membership changes to take effect."
echo "═══════════════════════════════════════════════════════════"
```

---

## Disk Space Requirements Summary

| Component | Size |
|-----------|------|
| Ubuntu Server 24.04 LTS (minimal) | ~3.5 GB |
| System packages and tools | ~2.0 GB |
| Python and libraries | ~0.4 GB |
| Docker images (all weeks) | ~3.8 GB |
| Course materials (WEEK 1–14) | ~10 MB |
| Working space for artefacts | ~0.7 GB |
| **Recommended Total** | **25 GB** |

---

*This guide was generated for the Computer Networks course at ASE-CSIE București. For updates and corrections, please refer to the course repository.*
