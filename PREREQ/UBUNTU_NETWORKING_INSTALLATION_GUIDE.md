# Complete Installation and Configuration Guide
## Ubuntu Server 24.04 LTS for Computer Networks Seminars

**Document generated:** January 2026  
**Target platform:** Ubuntu Server 24.04 LTS (VirtualBox VM)  
**Purpose:** Complete setup for WEEK1–WEEK14 of the Computer Networks course

---

## Table of Contents

1. [Initial VirtualBox Configuration](#1-initial-virtualbox-configuration)
   - [1.1 Recommended VM Settings](#11-recommended-vm-settings)
   - [1.2 Network Adapter Configuration](#12-network-adapter-configuration-in-virtualbox)
   - [1.3 Enable Nested Virtualization](#13-enable-nested-virtualization-optional-for-advanced-mininet)
   - [1.4 Install VirtualBox Guest Additions](#14-install-virtualbox-guest-additions-cli)
   - [1.5 Configure Port Forwarding for SSH](#15-configure-port-forwarding-for-ssh-with-nat)
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

### 1.1 Recommended VM Settings

Before installing Ubuntu, ensure the VM has the appropriate configuration:

| Parameter | Minimum Value | Recommended Value |
|-----------|---------------|-------------------|
| RAM | 2 GB | 4–8 GB |
| CPU | 2 cores | 4 cores |
| Disk | 25 GB | 50 GB |
| Network Adapter 1 | NAT | NAT (for internet access) |
| Network Adapter 2 | — | Host-Only (for access from host) |

### 1.2 Network Adapter Configuration in VirtualBox

```
Settings → Network:

Adapter 1:
  ☑ Enable Network Adapter
  Attached to: NAT
  (For internet access from VM)

Adapter 2:
  ☑ Enable Network Adapter  
  Attached to: Host-only Adapter
  Name: vboxnet0 (or create a new one)
  (For SSH and access from the host machine)
```

**Creating a Host-Only Network (if it doesn't exist):**
```
VirtualBox → File → Host Network Manager → Create
  - IPv4 Address: 192.168.56.1
  - IPv4 Network Mask: 255.255.255.0
  - ☑ Enable DHCP Server
```

### 1.3 Enable Nested Virtualization (Optional, for advanced Mininet)

> **⚠️ IMPORTANT NOTE:**
> - Nested virtualization is **optional** — the seminars work without it
> - The VM must be **powered off** when running the command
> - Requires CPU with hardware support VT-x (Intel) or AMD-V (AMD)

#### On Windows (PowerShell as Administrator)

**Step 1: Find the exact VM name**

Open PowerShell as Administrator and run:
```powershell
# List all existing VMs
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" list vms
```

You will see output like:
```
"Ubuntu-Server-24" {a1b2c3d4-e5f6-...}
"Windows10-Test" {f7g8h9i0-j1k2-...}
```

**Step 2: Enable nested virtualization**

Use the exact name from the list above:
```powershell
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" modifyvm "Ubuntu-Server-24" --nested-hw-virt on
```

> **💡 Why is the full path required?**
> On Windows, `VBoxManage.exe` is not automatically added to the PATH environment variable.
> You must use the full path: `"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"`
> The `&` character in PowerShell allows execution of a program with spaces in the path.

**Alternative — Add VirtualBox to PATH (permanent):**
```powershell
# Run once to permanently add to PATH
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\Oracle\VirtualBox", "User")
# Restart PowerShell, then you can use directly:
VBoxManage list vms
```

#### On Linux/macOS

```bash
# List VMs
VBoxManage list vms

# Enable nested virtualization
VBoxManage modifyvm "VMName" --nested-hw-virt on
```

#### Verify Activation

After starting the VM, verify from inside Ubuntu:
```bash
# Check virtualization support
egrep -c '(vmx|svm)' /proc/cpuinfo
# Result > 0 means nested virt is working
```

### 1.4 Install VirtualBox Guest Additions (CLI)

Guest Additions provide important functionality: shared folders, shared clipboard, dynamic resolution, and improved performance.

#### Method 1: From VirtualBox CD (Recommended — current version)

**Step 1: Install required dependencies**
```bash
sudo apt update
sudo apt install build-essential dkms linux-headers-$(uname -r) -y
```

**Step 2: Mount the Guest Additions CD**

In the VirtualBox VM window:
```
Devices → Insert Guest Additions CD image...
```

**Step 3: Mount and run the installer**
```bash
# Mount the CD
sudo mount /dev/cdrom /mnt

# Run the installer
sudo /mnt/VBoxLinuxAdditions.run
```

**Step 4: Unmount and reboot**
```bash
sudo umount /mnt
sudo reboot
```

**Step 5: Verify installation**
```bash
lsmod | grep vbox
# You should see: vboxguest, vboxsf, vboxvideo
```

#### Method 2: From Ubuntu Repositories (Simpler, possibly older version)

```bash
sudo apt install virtualbox-guest-utils virtualbox-guest-dkms -y
sudo reboot
```

#### Troubleshooting Guest Additions

**Kernel headers error:**
```bash
sudo apt install linux-headers-generic -y
```

**If `/dev/cdrom` doesn't exist:**
```bash
# Check available device
lsblk
# Usually it's /dev/sr0
sudo mount /dev/sr0 /mnt
```

**Final verification:**
```bash
# Check loaded modules
lsmod | grep vbox

# Check Guest Additions version
VBoxControl --version
```

### 1.5 Configure Port Forwarding for SSH (with NAT)

When using **NAT** as the network adapter, the guest is not directly accessible from the host. You need to configure **Port Forwarding** to access SSH.

#### Configuration in VirtualBox

**Step 1:** With the VM stopped or running, open:
```
VM Settings → Network → Adapter 1 (NAT) → Advanced → Port Forwarding
```

**Step 2:** Click the **+** icon (Add new rule) and fill in:

| Name | Protocol | Host IP     | Host Port | Guest IP  | Guest Port |
|------|----------|-------------|-----------|-----------|------------|
| SSH  | TCP      | 127.0.0.1   | 2222      | 10.0.2.15 | 22         |

> **💡 Note:** You can leave **Guest IP** empty — VirtualBox will forward to any IP in the guest.

**Step 3:** Click **OK** to save.

#### Configure SSH in Ubuntu Guest

Ensure SSH is running in the VM:
```bash
sudo systemctl enable ssh
sudo systemctl start ssh
sudo systemctl status ssh
```

#### Connect from Windows

**Option A: PowerShell / Command Prompt**
```powershell
ssh username@127.0.0.1 -p 2222
```

**Option B: PuTTY**
- **Host Name:** `127.0.0.1`
- **Port:** `2222`
- **Connection type:** SSH

**Option C: Windows Terminal**
```powershell
ssh username@localhost -p 2222
```

#### Connect from Linux/macOS (from host)
```bash
ssh username@127.0.0.1 -p 2222
```

#### Additional Port Forwarding (Optional)

To access other services from the VM, add additional rules:

| Name      | Protocol | Host Port | Guest Port | Usage                        |
|-----------|----------|-----------|------------|------------------------------|
| HTTP      | TCP      | 8080      | 80         | Web server                   |
| HTTPS     | TCP      | 8443      | 443        | Secure web server            |
| Flask     | TCP      | 5000      | 5000       | Python Flask applications    |
| Custom    | TCP      | 3333      | 3333       | Custom protocols (WEEK4)     |

> **⚠️ Alternative:** If you configured **Adapter 2 as Host-Only** (section 1.2), you can access the VM directly on the 192.168.56.x network IP without port forwarding.

---

## 2. System Update and Essential Packages

### 2.1 First Connection and Update

After installing Ubuntu Server and first login:

```bash
# Full system update
sudo apt update && sudo apt upgrade -y

# Install essential base packages
sudo apt install -y \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    curl \
    wget \
    git \
    vim \
    nano \
    htop \
    tree \
    unzip \
    zip \
    jq \
    make \
    gcc \
    g++
```

### 2.2 Configure Localisation and Timezone

```bash
# Set timezone to Bucharest
sudo timedatectl set-timezone Europe/Bucharest

# Verify
timedatectl

# Configure locales (optional)
sudo locale-gen en_GB.UTF-8
sudo update-locale LANG=en_GB.UTF-8
```

### 2.3 Configure SSH for Remote Access

```bash
# Install OpenSSH Server (if not installed)
sudo apt install -y openssh-server

# Start and enable at boot
sudo systemctl enable --now ssh

# Check status
sudo systemctl status ssh

# Display IP for connection
ip addr show
```

---

## 3. Network Tools

### 3.1 Essential Networking Packages

```bash
# Basic diagnostics
sudo apt install -y iputils-ping iproute2 net-tools dnsutils traceroute mtr-tiny whois

# Connectivity and transfer
sudo apt install -y netcat-openbsd socat curl wget lftp openssh-client

# Traffic monitoring
sudo apt install -y tcpdump iftop nethogs nload bmon

# Scanning and security
sudo apt install -y nmap hping3 iperf3 arping

# Firewall
sudo apt install -y iptables conntrack
sudo apt install -y iptables-persistent  # Will prompt for saving rules

# Ethernet bridging and VLAN
sudo apt install -y bridge-utils vlan arptables
```

Or all in a single command (without comments):

```bash
sudo apt install -y \
    iputils-ping iproute2 net-tools dnsutils traceroute mtr-tiny whois \
    netcat-openbsd socat curl wget lftp openssh-client \
    tcpdump iftop nethogs nload bmon \
    nmap hping3 iperf3 arping \
    iptables iptables-persistent conntrack \
    bridge-utils vlan arptables
```

### 3.2 Configure Permissions for Packet Capture

```bash
# Allow tcpdump without sudo
sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/tcpdump

# Verify
getcap /usr/bin/tcpdump
```

---

## 4. Python and Libraries

### 4.1 Install Python 3 and Pip

Ubuntu 24.04 comes with Python 3.12. We also install additional components:

```bash
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel
```

### 4.2 Python Libraries for WEEK1–WEEK14 Seminars

```bash
# Required flags in Ubuntu 24.04:
#   --break-system-packages  = allows installation in the system environment
#   --ignore-installed       = avoids conflicts with packages installed by apt/debian
#
# The warning about "Running pip as root" can be ignored in the context of a lab VM

# Packet manipulation and sniffing (WEEK1, WEEK3, WEEK6, WEEK7, WEEK13)
sudo pip3 install --break-system-packages --ignore-installed scapy

# Pcap parsing (WEEK1, WEEK2)
sudo pip3 install --break-system-packages --ignore-installed dpkt pyshark

# Network interface information (WEEK2)
sudo pip3 install --break-system-packages --ignore-installed netifaces

# HTTP and REST API (WEEK8, WEEK10)
sudo pip3 install --break-system-packages --ignore-installed flask requests

# DNS (WEEK10, WEEK11, WEEK12)
sudo pip3 install --break-system-packages --ignore-installed dnslib dnspython

# SSH and SFTP (WEEK10, WEEK11)
sudo pip3 install --break-system-packages --ignore-installed paramiko

# FTP Server (WEEK9, WEEK10, WEEK11)
sudo pip3 install --break-system-packages --ignore-installed pyftpdlib

# MQTT for IoT (WEEK13)
sudo pip3 install --break-system-packages --ignore-installed paho-mqtt

# gRPC for advanced RPC (WEEK12)
sudo pip3 install --break-system-packages --ignore-installed grpcio grpcio-tools protobuf

# Utilities
sudo pip3 install --break-system-packages --ignore-installed pyyaml colorama colorlog tabulate psutil

# SDN Controller (WEEK6)
sudo pip3 install --break-system-packages --ignore-installed os-ken

# Documentation (optional)
sudo pip3 install --break-system-packages --ignore-installed python-docx
```

Or all in a single command:

```bash
sudo pip3 install --break-system-packages --ignore-installed \
    scapy dpkt pyshark netifaces \
    flask requests \
    dnslib dnspython \
    paramiko pyftpdlib \
    paho-mqtt \
    grpcio grpcio-tools protobuf \
    pyyaml colorama colorlog tabulate psutil \
    os-ken python-docx
```

> **💡 Note:** The `--ignore-installed` flag resolves errors like `Cannot uninstall X, RECORD file not found` that occur when pip tries to update packages installed by the operating system (apt/debian).

### 4.3 Verify Python Installation

```bash
# Check versions
python3 --version
pip3 --version

# Test import of essential libraries
python3 -c "
import scapy.all
import socket
import ipaddress
import struct
import threading
import scapy
print('✓ All standard modules are working')
print(f'  Scapy version: {scapy.VERSION}')
"
```

Quick verification for all installed libraries:
```bash
python3 -c "
libs = ['scapy', 'dpkt', 'flask', 'requests', 'dns', 'paramiko', 'pyftpdlib', 'paho', 'grpc', 'colorama']
for lib in libs:
    try:
        __import__(lib)
        print(f'✓ {lib}')
    except ImportError:
        print(f'✗ {lib} - MISSING')
"
```

---

## 5. Docker and Docker Compose

### 5.1 Install Docker Engine

```bash
# Remove old versions (if they exist)
sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Add official Docker repository
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify installation
sudo docker --version
sudo docker compose version
```

### 5.2 Configure Docker for Non-Root User

```bash
# Add current user to docker group
sudo usermod -aG docker $USER

# Apply changes (or re-login)
newgrp docker

# Verify (should work without sudo)
docker run hello-world
```

### 5.3 Configure Docker for Automatic Startup

```bash
# Enable at boot
sudo systemctl enable docker
sudo systemctl enable containerd

# Check status
sudo systemctl status docker
```

---

## 6. Mininet and Open vSwitch

### 6.1 Install Mininet

```bash
# Install Mininet from official Ubuntu repository
sudo apt install -y mininet

# Install Open vSwitch (required for Mininet)
sudo apt install -y \
    openvswitch-switch \
    openvswitch-common \
    openvswitch-testcontroller
```

### 6.2 Configure and Start Open vSwitch

```bash
# Start OVS service
sudo systemctl enable --now openvswitch-switch

# Check status
sudo systemctl status openvswitch-switch

# Check OVS version
sudo ovs-vsctl --version
```

### 6.3 Test Mininet

```bash
# Quick test (requires sudo)
sudo mn --test pingall

# Extended test with custom topology
sudo mn --topo tree,depth=2,fanout=2 --test pingall

# Cleanup after tests
sudo mn -c
```

### 6.4 Install Additional SDN Controller (Optional)

```bash
# Os-ken (modern fork of Ryu) - already installed via pip
# Verify
python3 -c "import os_ken; print(f'OS-Ken version: {os_ken.__version__}')"
```

---

## 7. Wireshark/TShark

### 7.1 Install Wireshark and TShark

```bash
# Install (TShark for CLI, Wireshark for GUI if you have X11)
sudo apt install -y tshark wireshark-common

# During installation, select "Yes" to allow
# non-root users to capture packets
```

### 7.2 Configure Wireshark Permissions

```bash
# Add user to wireshark group
sudo usermod -aG wireshark $USER

# Configure capabilities for dumpcap
sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/dumpcap

# Verify
getcap /usr/bin/dumpcap

# Re-login or:
newgrp wireshark
```

### 7.3 Verify TShark

```bash
# Check version
tshark --version | head -3

# Test capture (stop with Ctrl+C)
sudo tshark -i any -c 10
```

---

## 8. Additional Configuration

### 8.1 Configure IP Forwarding (for NAT/Routing)

```bash
# Temporary activation
sudo sysctl -w net.ipv4.ip_forward=1
sudo sysctl -w net.ipv6.conf.all.forwarding=1

# Permanent activation
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.d/99-networking.conf
echo "net.ipv6.conf.all.forwarding=1" | sudo tee -a /etc/sysctl.d/99-networking.conf
sudo sysctl --system
```

### 8.2 Disable Systemd-Resolved (Optional, for custom DNS)

```bash
# Only if you have conflicts with local DNS server (port 53)
# sudo systemctl disable systemd-resolved
# sudo systemctl stop systemd-resolved
# sudo rm /etc/resolv.conf
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
```

### 8.3 Configure UFW Firewall

```bash
# Install and basic configuration
sudo apt install -y ufw

# Allow SSH (important!)
sudo ufw allow ssh

# Allow common ports for labs
sudo ufw allow 8080/tcp  # Alternative HTTP
sudo ufw allow 3333/tcp  # Custom protocols
sudo ufw allow 4444/tcp  # Custom protocols
sudo ufw allow 5555/udp  # UDP sensors
sudo ufw allow 1025/tcp  # Educational SMTP
sudo ufw allow 2121/tcp  # Alternative FTP

# Enable (caution - make sure SSH is allowed!)
# sudo ufw enable
```

### 8.4 Create Directory Structure

```bash
# Create working directories
mkdir -p ~/networking/{seminars,pcap,logs,scripts,docs}

# Set permissions
chmod 755 ~/networking
```

### 8.5 Configure Git (Optional)

```bash
git config --global user.name "Your Name"
git config --global user.email "email@example.com"
git config --global init.defaultBranch main
```

### 8.6 Useful Aliases (Optional)

```bash
# Add to ~/.bashrc
cat >> ~/.bashrc << 'EOF'

# === Networking Lab Aliases ===
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

# Docker
alias dc='docker compose'
alias dps='docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'
alias dlog='docker logs -f'

# Mininet
alias mnc='sudo mn -c'  # Cleanup
alias mnt='sudo mn --test pingall'

# Network
alias ports='sudo netstat -tulpn'
alias myip='ip -4 addr show | grep -oP "(?<=inet\s)\d+(\.\d+){3}" | grep -v 127.0.0.1'

# Python
alias py='python3'
alias pip='pip3'

# Capture
alias tcap='sudo tcpdump -i any -nn'
alias tcapw='sudo tcpdump -i any -w'
EOF

# Apply
source ~/.bashrc
```

---

## 9. Transfer and Organise Materials

### 9.1 Options for Transferring WEEK1-14.zip Archive

**Option A: SCP from host machine**
```bash
# From the host machine terminal (Windows/Linux/macOS)
scp WEEK1-14.zip username@VM_IP:~/networking/seminars/
```

**Option B: VirtualBox Shared Folder**
```bash
# 1. In VirtualBox: Settings → Shared Folders → Add
#    - Folder Path: path to folder with archive
#    - Folder Name: shared
#    - ☑ Auto-mount

# 2. In VM:
sudo apt install -y virtualbox-guest-utils virtualbox-guest-additions-iso
sudo usermod -aG vboxsf $USER
# Reboot required

# 3. Copy the file
cp /media/sf_shared/WEEK1-14.zip ~/networking/seminars/
```

**Option C: wget/curl (if you have a URL)**
```bash
cd ~/networking/seminars
wget "ARCHIVE_URL" -O WEEK1-14.zip
# or
curl -L "ARCHIVE_URL" -o WEEK1-14.zip
```

### 9.2 Extract and Organise

```bash
cd ~/networking/seminars

# Extract
unzip WEEK1-14.zip

# Check structure
tree -L 2 WEEK*

# Set permissions for scripts
find . -name "*.sh" -exec chmod +x {} \;
find . -name "*.py" -exec chmod +x {} \;
```

---

## 10. Verification Script

Create a script to verify the complete installation:

```bash
cat > ~/networking/scripts/verify_installation.sh << 'SCRIPT'
#!/bin/bash
# =============================================================================
# Installation Verification Script - Networking Lab Ubuntu 24.04
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     INSTALLATION VERIFICATION - NETWORKING LAB UBUNTU 24.04  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

check() {
    if $1 &>/dev/null; then
        echo -e "${GREEN}✓${NC} $2"
        return 0
    else
        echo -e "${RED}✗${NC} $2"
        return 1
    fi
}

check_version() {
    version=$($1 2>&1 | head -1)
    echo -e "${GREEN}✓${NC} $2: ${YELLOW}$version${NC}"
}

ERRORS=0

echo "═══ SYSTEM ═══"
check_version "cat /etc/os-release | grep PRETTY_NAME | cut -d'\"' -f2" "OS"
check_version "uname -r" "Kernel"

echo ""
echo "═══ PYTHON ═══"
check "python3 --version" "Python3" || ((ERRORS++))
check "pip3 --version" "Pip3" || ((ERRORS++))

echo ""
echo "═══ PYTHON LIBRARIES ═══"
for lib in scapy dpkt flask requests dnslib dnspython paramiko pyftpdlib paho grpc colorama; do
    check "python3 -c 'import $lib'" "$lib" || ((ERRORS++))
done

echo ""
echo "═══ DOCKER ═══"
check "docker --version" "Docker Engine" || ((ERRORS++))
check "docker compose version" "Docker Compose" || ((ERRORS++))
check "docker ps" "Docker daemon running" || ((ERRORS++))

echo ""
echo "═══ MININET & OVS ═══"
check "which mn" "Mininet" || ((ERRORS++))
check "sudo ovs-vsctl --version" "Open vSwitch" || ((ERRORS++))
check "systemctl is-active openvswitch-switch" "OVS Service" || ((ERRORS++))

echo ""
echo "═══ NETWORK TOOLS ═══"
for tool in tcpdump tshark nmap hping3 iperf3 netcat curl wget traceroute; do
    check "which $tool" "$tool" || ((ERRORS++))
done

echo ""
echo "═══ PERMISSIONS ═══"
check "groups | grep -q docker" "User in docker group" || ((ERRORS++))
check "groups | grep -q wireshark" "User in wireshark group" || ((ERRORS++))

echo ""
echo "═══ SERVICES ═══"
check "systemctl is-active ssh" "SSH" || ((ERRORS++))
check "systemctl is-active docker" "Docker" || ((ERRORS++))
check "systemctl is-active openvswitch-switch" "OVS" || ((ERRORS++))

echo ""
echo "═══ NETWORK ═══"
echo "Network interfaces:"
ip -br addr show

echo ""
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ALL VERIFICATIONS PASSED SUCCESSFULLY!                      ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  $ERRORS ERRORS DETECTED - CHECK INSTALLATION!                  ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
fi

exit $ERRORS
SCRIPT

chmod +x ~/networking/scripts/verify_installation.sh
```

**Run verification:**
```bash
~/networking/scripts/verify_installation.sh
```

---

## 11. Troubleshooting

### 11.1 Common Problems and Solutions

#### Docker: "permission denied"
```bash
# Cause: User is not in the docker group
sudo usermod -aG docker $USER
# Then logout/login or:
newgrp docker
```

#### Mininet: "Cannot find required executable..."
```bash
# Cause: OVS is not running
sudo systemctl start openvswitch-switch
sudo mn -c  # Cleanup
```

#### TShark: "permission denied"
```bash
# Cause: Insufficient permissions
sudo usermod -aG wireshark $USER
sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/dumpcap
newgrp wireshark
```

#### Python: "externally-managed-environment"
```bash
# Cause: Ubuntu 24.04 protects system packages
# Solution 1: Use --break-system-packages
pip3 install package --break-system-packages

# Solution 2: Use venv (recommended for production projects)
python3 -m venv ~/venv
source ~/venv/bin/activate
pip install package
```

#### Python: "Cannot uninstall X, RECORD file not found"
```bash
# Cause: Conflict between packages installed by apt and pip
# Solution: Add --ignore-installed
sudo pip3 install --break-system-packages --ignore-installed flask

# For multiple packages:
sudo pip3 install --break-system-packages --ignore-installed package1 package2
```

#### Port 53 occupied (DNS)
```bash
# Cause: systemd-resolved is using the port
sudo systemctl stop systemd-resolved
# Or use a different port for custom DNS (e.g.: 5353)
```

#### Mininet cleanup
```bash
# After crash or errors, clean up with:
sudo mn -c
sudo ovs-vsctl --if-exists del-br ovs-br0
sudo killall controller 2>/dev/null
```

### 11.2 Useful Diagnostic Commands

```bash
# Check ports in use
sudo ss -tulpn
sudo netstat -tulpn

# Check network processes
ps aux | grep -E "(python|docker|mn|ovs)"

# Check system logs
sudo journalctl -xe
sudo journalctl -u docker
sudo journalctl -u openvswitch-switch

# Check disk space
df -h

# Check memory
free -h

# Check connectivity
ping -c 3 8.8.8.8
ping -c 3 google.com
```

---

## Complete Commands Summary (All-in-One Script)

For convenience, all installation commands in a single block:

```bash
#!/bin/bash
# RUN WITH: sudo bash install_networking_lab.sh

set -e

echo "=== System update ==="
apt update && apt upgrade -y

echo "=== Essential packages ==="
apt install -y build-essential software-properties-common apt-transport-https \
    ca-certificates gnupg lsb-release curl wget git vim nano htop tree unzip zip jq make gcc g++

echo "=== Network tools ==="
apt install -y iputils-ping iproute2 net-tools dnsutils traceroute mtr-tiny whois \
    netcat-openbsd socat curl wget lftp openssh-client tcpdump iftop nethogs nload bmon \
    nmap hping3 iperf3 arping iptables iptables-persistent conntrack bridge-utils vlan arptables

echo "=== Python ==="
apt install -y python3 python3-pip python3-venv python3-dev python3-setuptools python3-wheel

echo "=== Python libraries ==="
pip3 install --break-system-packages --ignore-installed scapy dpkt pyshark netifaces flask requests dnslib \
    dnspython paramiko pyftpdlib paho-mqtt grpcio grpcio-tools protobuf pyyaml colorama \
    colorlog tabulate psutil os-ken python-docx

echo "=== Docker ==="
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable docker containerd

echo "=== Mininet & OVS ==="
apt install -y mininet openvswitch-switch openvswitch-common openvswitch-testcontroller
systemctl enable --now openvswitch-switch

echo "=== Wireshark/TShark ==="
DEBIAN_FRONTEND=noninteractive apt install -y tshark wireshark-common
setcap cap_net_raw,cap_net_admin+eip /usr/bin/dumpcap
setcap cap_net_raw,cap_net_admin+eip /usr/bin/tcpdump

echo "=== Final configuration ==="
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.d/99-networking.conf
echo "net.ipv6.conf.all.forwarding=1" >> /etc/sysctl.d/99-networking.conf
sysctl --system

echo "=== INSTALLATION COMPLETE ==="
echo "Run the following commands manually as normal user:"
echo "  sudo usermod -aG docker \$USER"
echo "  sudo usermod -aG wireshark \$USER"
echo "  newgrp docker"
echo "  newgrp wireshark"
```

---

**Document generated for the Computer Networks course, ASE-CSIE Bucharest**
