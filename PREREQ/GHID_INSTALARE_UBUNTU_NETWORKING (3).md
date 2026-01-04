# Ghid Complet de Instalare și Configurare
## Ubuntu Server 24.04 LTS pentru Seminariile de Rețele de Calculatoare

**Document generat:** Ianuarie 2026  
**Platformă țintă:** Ubuntu Server 24.04 LTS (VirtualBox VM)  
**Scop:** Configurare completă pentru WEEK1–WEEK14 din cursul de Computer Networks

---

## Cuprins

1. [Configurare Inițială VirtualBox](#1-configurare-inițială-virtualbox)
   - [1.1 Setări Recomandate pentru VM](#11-setări-recomandate-pentru-vm)
   - [1.2 Configurare Adaptoare de Rețea](#12-configurare-adaptoare-de-rețea-în-virtualbox)
   - [1.3 Activare Nested Virtualization](#13-activare-nested-virtualization-opțional-pentru-mininet-avansat)
   - [1.4 Instalare VirtualBox Guest Additions](#14-instalare-virtualbox-guest-additions-cli)
   - [1.5 Configurare Port Forwarding pentru SSH](#15-configurare-port-forwarding-pentru-ssh-cu-nat)
2. [Actualizare Sistem și Pachete Esențiale](#2-actualizare-sistem-și-pachete-esențiale)
3. [Instrumente de Rețea](#3-instrumente-de-rețea)
4. [Python și Biblioteci](#4-python-și-biblioteci)
5. [Docker și Docker Compose](#5-docker-și-docker-compose)
6. [Mininet și Open vSwitch](#6-mininet-și-open-vswitch)
7. [Wireshark/TShark](#7-wiresharktshark)
8. [Configurări Suplimentare](#8-configurări-suplimentare)
9. [Transfer și Organizare Materiale](#9-transfer-și-organizare-materiale)
10. [Script de Verificare](#10-script-de-verificare)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Configurare Inițială VirtualBox

### 1.1 Setări Recomandate pentru VM

Înainte de instalarea Ubuntu, asigură-te că VM-ul are configurația corespunzătoare:

| Parametru | Valoare Minimă | Valoare Recomandată |
|-----------|----------------|---------------------|
| RAM | 2 GB | 4–8 GB |
| CPU | 2 cores | 4 cores |
| Disk | 25 GB | 50 GB |
| Network Adapter 1 | NAT | NAT (pentru acces internet) |
| Network Adapter 2 | — | Host-Only (pentru acces din host) |

### 1.2 Configurare Adaptoare de Rețea în VirtualBox

```
Settings → Network:

Adapter 1:
  ☑ Enable Network Adapter
  Attached to: NAT
  (Pentru acces la internet din VM)

Adapter 2:
  ☑ Enable Network Adapter  
  Attached to: Host-only Adapter
  Name: vboxnet0 (sau crează unul nou)
  (Pentru SSH și acces de pe mașina gazdă)
```

**Crearea unui Host-Only Network (dacă nu există):**
```
VirtualBox → File → Host Network Manager → Create
  - IPv4 Address: 192.168.56.1
  - IPv4 Network Mask: 255.255.255.0
  - ☑ Enable DHCP Server
```

### 1.3 Activare Nested Virtualization (Opțional, pentru Mininet avansat)

> **⚠️ NOTĂ IMPORTANTĂ:**
> - Nested virtualization este **opțională** — seminariile funcționează și fără ea
> - VM-ul trebuie să fie **oprit** când rulezi comanda
> - Necesită CPU cu suport hardware VT-x (Intel) sau AMD-V (AMD)

#### Pe Windows (PowerShell ca Administrator)

**Pas 1: Află numele exact al VM-ului**

Deschide PowerShell ca Administrator și rulează:
```powershell
# Listează toate VM-urile existente
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" list vms
```

Vei vedea output de forma:
```
"Ubuntu-Server-24" {a1b2c3d4-e5f6-...}
"Windows10-Test" {f7g8h9i0-j1k2-...}
```

**Pas 2: Activează nested virtualization**

Folosește numele exact din lista de mai sus:
```powershell
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" modifyvm "Ubuntu-Server-24" --nested-hw-virt on
```

> **💡 De ce trebuie calea completă?**
> Pe Windows, `VBoxManage.exe` nu este adăugat automat în variabila de mediu PATH.
> Trebuie să folosești calea completă: `"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"`
> Caracterul `&` din PowerShell permite executarea unui program cu spații în cale.

**Alternativă — Adăugare VirtualBox în PATH (permanentă):**
```powershell
# Rulează o singură dată pentru a adăuga permanent în PATH
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\Oracle\VirtualBox", "User")
# Repornește PowerShell, apoi poți folosi direct:
VBoxManage list vms
```

#### Pe Linux/macOS

```bash
# Listează VM-urile
VBoxManage list vms

# Activează nested virtualization
VBoxManage modifyvm "NumeVM" --nested-hw-virt on
```

#### Verificare Activare

După pornirea VM-ului, verifică din interiorul Ubuntu:
```bash
# Verifică suport virtualizare
egrep -c '(vmx|svm)' /proc/cpuinfo
# Rezultat > 0 înseamnă că nested virt funcționează
```

### 1.4 Instalare VirtualBox Guest Additions (CLI)

Guest Additions oferă funcționalități importante: shared folders, clipboard partajat, rezoluție dinamică și performanță îmbunătățită.

#### Metoda 1: De pe CD-ul VirtualBox (Recomandată — versiune actuală)

**Pas 1: Instalează dependențele necesare**
```bash
sudo apt update
sudo apt install build-essential dkms linux-headers-$(uname -r) -y
```

**Pas 2: Montează CD-ul Guest Additions**

În fereastra VirtualBox a VM-ului:
```
Devices → Insert Guest Additions CD image...
```

**Pas 3: Montează și rulează installer-ul**
```bash
# Montează CD-ul
sudo mount /dev/cdrom /mnt

# Rulează installer-ul
sudo /mnt/VBoxLinuxAdditions.run
```

**Pas 4: Demontează și repornește**
```bash
sudo umount /mnt
sudo reboot
```

**Pas 5: Verifică instalarea**
```bash
lsmod | grep vbox
# Trebuie să vezi: vboxguest, vboxsf, vboxvideo
```

#### Metoda 2: Din Repository-uri Ubuntu (Mai simplă, posibil versiune mai veche)

```bash
sudo apt install virtualbox-guest-utils virtualbox-guest-dkms -y
sudo reboot
```

#### Troubleshooting Guest Additions

**Eroare kernel headers:**
```bash
sudo apt install linux-headers-generic -y
```

**Dacă `/dev/cdrom` nu există:**
```bash
# Verifică device-ul disponibil
lsblk
# De obicei e /dev/sr0
sudo mount /dev/sr0 /mnt
```

**Verificare finală:**
```bash
# Verifică modulele încărcate
lsmod | grep vbox

# Verifică versiunea Guest Additions
VBoxControl --version
```

### 1.5 Configurare Port Forwarding pentru SSH (cu NAT)

Când folosești **NAT** ca adaptor de rețea, guest-ul nu este accesibil direct din host. Trebuie să configurezi **Port Forwarding** pentru a accesa SSH-ul.

#### Configurare în VirtualBox

**Pas 1:** Cu VM-ul oprit sau în execuție, deschide:
```
VM Settings → Network → Adapter 1 (NAT) → Advanced → Port Forwarding
```

**Pas 2:** Click pe iconița **+** (Add new rule) și completează:

| Name | Protocol | Host IP     | Host Port | Guest IP  | Guest Port |
|------|----------|-------------|-----------|-----------|------------|
| SSH  | TCP      | 127.0.0.1   | 2222      | 10.0.2.15 | 22         |

> **💡 Notă:** Poți lăsa **Guest IP** gol — VirtualBox va forwarda către orice IP din guest.

**Pas 3:** Click **OK** pentru a salva.

#### Configurare SSH în Ubuntu Guest

Asigură-te că SSH-ul rulează în VM:
```bash
sudo systemctl enable ssh
sudo systemctl start ssh
sudo systemctl status ssh
```

#### Conectare din Windows

**Opțiunea A: PowerShell / Command Prompt**
```powershell
ssh utilizator@127.0.0.1 -p 2222
```

**Opțiunea B: PuTTY**
- **Host Name:** `127.0.0.1`
- **Port:** `2222`
- **Connection type:** SSH

**Opțiunea C: Windows Terminal**
```powershell
ssh utilizator@localhost -p 2222
```

#### Conectare din Linux/macOS (de pe host)
```bash
ssh utilizator@127.0.0.1 -p 2222
```

#### Port Forwarding Suplimentar (Opțional)

Pentru a accesa și alte servicii din VM, adaugă reguli suplimentare:

| Name      | Protocol | Host Port | Guest Port | Utilizare                    |
|-----------|----------|-----------|------------|------------------------------|
| HTTP      | TCP      | 8080      | 80         | Web server                   |
| HTTPS     | TCP      | 8443      | 443        | Web server securizat         |
| Flask     | TCP      | 5000      | 5000       | Aplicații Python Flask       |
| Custom    | TCP      | 3333      | 3333       | Protocoale custom (WEEK4)    |

> **⚠️ Alternativă:** Dacă ai configurat **Adapter 2 ca Host-Only** (secțiunea 1.2), poți accesa VM-ul direct pe IP-ul din rețeaua 192.168.56.x fără port forwarding.

---

## 2. Actualizare Sistem și Pachete Esențiale

### 2.1 Prima Conectare și Actualizare

După instalarea Ubuntu Server și prima autentificare:

```bash
# Actualizare completă a sistemului
sudo apt update && sudo apt upgrade -y

# Instalare pachete esențiale de bază
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

### 2.2 Configurare Localizare și Timezone

```bash
# Setare timezone București
sudo timedatectl set-timezone Europe/Bucharest

# Verificare
timedatectl

# Configurare locales (opțional)
sudo locale-gen en_GB.UTF-8
sudo update-locale LANG=en_GB.UTF-8
```

### 2.3 Configurare SSH pentru Acces Remote

```bash
# Instalare OpenSSH Server (dacă nu e instalat)
sudo apt install -y openssh-server

# Pornire și activare la boot
sudo systemctl enable --now ssh

# Verificare status
sudo systemctl status ssh

# Afișare IP pentru conectare
ip addr show
```

---

## 3. Instrumente de Rețea

### 3.1 Pachete Esențiale de Networking

```bash
# Diagnosticare de bază
sudo apt install -y iputils-ping iproute2 net-tools dnsutils traceroute mtr-tiny whois

# Conectivitate și transfer
sudo apt install -y netcat-openbsd socat curl wget lftp openssh-client

# Monitorizare trafic
sudo apt install -y tcpdump iftop nethogs nload bmon

# Scanare și securitate
sudo apt install -y nmap hping3 iperf3 arping

# Firewall
sudo apt install -y iptables conntrack
sudo apt install -y iptables-persistent  # Va cere confirmare pentru salvare reguli

# Ethernet bridging și VLAN
sudo apt install -y bridge-utils vlan arptables
```

Sau toate într-o singură comandă (fără comentarii):

```bash
sudo apt install -y \
    iputils-ping iproute2 net-tools dnsutils traceroute mtr-tiny whois \
    netcat-openbsd socat curl wget lftp openssh-client \
    tcpdump iftop nethogs nload bmon \
    nmap hping3 iperf3 arping \
    iptables iptables-persistent conntrack \
    bridge-utils vlan arptables
```

### 3.2 Configurare Permisiuni pentru Captura de Pachete

```bash
# Permite tcpdump fără sudo
sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/tcpdump

# Verificare
getcap /usr/bin/tcpdump
```

---

## 4. Python și Biblioteci

### 4.1 Instalare Python 3 și Pip

Ubuntu 24.04 vine cu Python 3.12. Instalăm și componentele suplimentare:

```bash
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel
```

### 4.2 Biblioteci Python pentru Seminariile WEEK1–WEEK14

```bash
# Flag-urile necesare în Ubuntu 24.04:
#   --break-system-packages  = permite instalarea în mediul sistem
#   --ignore-installed       = evită conflicte cu pachetele instalate de apt/debian
#
# Warning-ul despre "Running pip as root" poate fi ignorat în contextul unui VM de laborator

# Manipulare pachete și sniffing (WEEK1, WEEK3, WEEK6, WEEK7, WEEK13)
sudo pip3 install --break-system-packages --ignore-installed scapy

# Parsare pcap (WEEK1, WEEK2)
sudo pip3 install --break-system-packages --ignore-installed dpkt pyshark

# Informații interfețe rețea (WEEK2)
sudo pip3 install --break-system-packages --ignore-installed netifaces

# HTTP și REST API (WEEK8, WEEK10)
sudo pip3 install --break-system-packages --ignore-installed flask requests

# DNS (WEEK10, WEEK11, WEEK12)
sudo pip3 install --break-system-packages --ignore-installed dnslib dnspython

# SSH și SFTP (WEEK10, WEEK11)
sudo pip3 install --break-system-packages --ignore-installed paramiko

# FTP Server (WEEK9, WEEK10, WEEK11)
sudo pip3 install --break-system-packages --ignore-installed pyftpdlib

# MQTT pentru IoT (WEEK13)
sudo pip3 install --break-system-packages --ignore-installed paho-mqtt

# gRPC pentru RPC avansat (WEEK12)
sudo pip3 install --break-system-packages --ignore-installed grpcio grpcio-tools protobuf

# Utilitare
sudo pip3 install --break-system-packages --ignore-installed pyyaml colorama colorlog tabulate psutil

# SDN Controller (WEEK6)
sudo pip3 install --break-system-packages --ignore-installed os-ken

# Documentație (opțional)
sudo pip3 install --break-system-packages --ignore-installed python-docx
```

Sau toate într-o singură comandă:

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

> **💡 Notă:** Flag-ul `--ignore-installed` rezolvă erorile de tipul `Cannot uninstall X, RECORD file not found` care apar când pip încearcă să actualizeze pachete instalate de sistemul de operare (apt/debian).

### 4.3 Verificare Instalare Python

```bash
# Verificare versiuni
python3 --version
pip3 --version

# Testare import biblioteci esențiale
python3 -c "
import scapy.all
import socket
import ipaddress
import struct
import threading
import scapy
print('✓ Toate modulele standard funcționează')
print(f'  Scapy version: {scapy.VERSION}')
"
```

Verificare rapidă pentru toate bibliotecile instalate:
```bash
python3 -c "
libs = ['scapy', 'dpkt', 'flask', 'requests', 'dns', 'paramiko', 'pyftpdlib', 'paho', 'grpc', 'colorama']
for lib in libs:
    try:
        __import__(lib)
        print(f'✓ {lib}')
    except ImportError:
        print(f'✗ {lib} - LIPSEȘTE')
"
```

---

## 5. Docker și Docker Compose

### 5.1 Instalare Docker Engine

```bash
# Eliminare versiuni vechi (dacă există)
sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Adăugare repository oficial Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalare Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verificare instalare
sudo docker --version
sudo docker compose version
```

### 5.2 Configurare Docker pentru Utilizator Non-Root

```bash
# Adăugare utilizator curent în grupul docker
sudo usermod -aG docker $USER

# Activare modificări (sau relogin)
newgrp docker

# Verificare (trebuie să funcționeze fără sudo)
docker run hello-world
```

### 5.3 Configurare Docker pentru Pornire Automată

```bash
# Activare la boot
sudo systemctl enable docker
sudo systemctl enable containerd

# Verificare status
sudo systemctl status docker
```

---

## 6. Mininet și Open vSwitch

### 6.1 Instalare Mininet

```bash
# Instalare Mininet din repository oficial Ubuntu
sudo apt install -y mininet

# Instalare Open vSwitch (necesar pentru Mininet)
sudo apt install -y \
    openvswitch-switch \
    openvswitch-common \
    openvswitch-testcontroller
```

### 6.2 Configurare și Pornire Open vSwitch

```bash
# Pornire serviciu OVS
sudo systemctl enable --now openvswitch-switch

# Verificare status
sudo systemctl status openvswitch-switch

# Verificare versiune OVS
sudo ovs-vsctl --version
```

### 6.3 Testare Mininet

```bash
# Test rapid (necesită sudo)
sudo mn --test pingall

# Test extins cu topologie personalizată
sudo mn --topo tree,depth=2,fanout=2 --test pingall

# Curățare după teste
sudo mn -c
```

### 6.4 Instalare Controler SDN Suplimentar (Opțional)

```bash
# Os-ken (fork modern al Ryu) - deja instalat via pip
# Verificare
python3 -c "import os_ken; print(f'OS-Ken version: {os_ken.__version__}')"
```

---

## 7. Wireshark/TShark

### 7.1 Instalare Wireshark și TShark

```bash
# Instalare (TShark pentru CLI, Wireshark pentru GUI dacă ai X11)
sudo apt install -y tshark wireshark-common

# În timpul instalării, selectează "Yes" pentru a permite
# utilizatorilor non-root să captureze pachete
```

### 7.2 Configurare Permisiuni Wireshark

```bash
# Adăugare utilizator în grupul wireshark
sudo usermod -aG wireshark $USER

# Configurare capabilities pentru dumpcap
sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/dumpcap

# Verificare
getcap /usr/bin/dumpcap

# Relogin sau:
newgrp wireshark
```

### 7.3 Verificare TShark

```bash
# Verificare versiune
tshark --version | head -3

# Test captură (oprește cu Ctrl+C)
sudo tshark -i any -c 10
```

---

## 8. Configurări Suplimentare

### 8.1 Configurare IP Forwarding (pentru NAT/Routing)

```bash
# Activare temporară
sudo sysctl -w net.ipv4.ip_forward=1
sudo sysctl -w net.ipv6.conf.all.forwarding=1

# Activare permanentă
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.d/99-networking.conf
echo "net.ipv6.conf.all.forwarding=1" | sudo tee -a /etc/sysctl.d/99-networking.conf
sudo sysctl --system
```

### 8.2 Dezactivare Systemd-Resolved (Opțional, pentru DNS custom)

```bash
# Doar dacă ai conflicte cu serverul DNS local (port 53)
# sudo systemctl disable systemd-resolved
# sudo systemctl stop systemd-resolved
# sudo rm /etc/resolv.conf
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
```

### 8.3 Configurare Firewall UFW

```bash
# Instalare și configurare de bază
sudo apt install -y ufw

# Permitere SSH (important!)
sudo ufw allow ssh

# Permitere porturi comune pentru laboratoare
sudo ufw allow 8080/tcp  # HTTP alternativ
sudo ufw allow 3333/tcp  # Protocoale custom
sudo ufw allow 4444/tcp  # Protocoale custom
sudo ufw allow 5555/udp  # UDP sensors
sudo ufw allow 1025/tcp  # SMTP educational
sudo ufw allow 2121/tcp  # FTP alternativ

# Activare (atenție - asigură-te că SSH e permis!)
# sudo ufw enable
```

### 8.4 Creare Structură Directoare

```bash
# Creare directoare de lucru
mkdir -p ~/networking/{seminars,pcap,logs,scripts,docs}

# Setare permisiuni
chmod 755 ~/networking
```

### 8.5 Configurare Git (Opțional)

```bash
git config --global user.name "Numele Tău"
git config --global user.email "email@example.com"
git config --global init.defaultBranch main
```

### 8.6 Alias-uri Utile (Opțional)

```bash
# Adăugare în ~/.bashrc
cat >> ~/.bashrc << 'EOF'

# === Alias-uri Networking Lab ===
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

# Aplicare
source ~/.bashrc
```

---

## 9. Transfer și Organizare Materiale

### 9.1 Opțiuni de Transfer al Arhivei WEEK1-14.zip

**Opțiunea A: SCP din mașina gazdă**
```bash
# Din terminalul mașinii gazdă (Windows/Linux/macOS)
scp WEEK1-14.zip utilizator@IP_VM:~/networking/seminars/
```

**Opțiunea B: Shared Folder VirtualBox**
```bash
# 1. În VirtualBox: Settings → Shared Folders → Add
#    - Folder Path: calea către folderul cu arhiva
#    - Folder Name: shared
#    - ☑ Auto-mount

# 2. În VM:
sudo apt install -y virtualbox-guest-utils virtualbox-guest-additions-iso
sudo usermod -aG vboxsf $USER
# Reboot necesar

# 3. Copiază fișierul
cp /media/sf_shared/WEEK1-14.zip ~/networking/seminars/
```

**Opțiunea C: wget/curl (dacă ai URL)**
```bash
cd ~/networking/seminars
wget "URL_ARHIVĂ" -O WEEK1-14.zip
# sau
curl -L "URL_ARHIVĂ" -o WEEK1-14.zip
```

### 9.2 Dezarhivare și Organizare

```bash
cd ~/networking/seminars

# Dezarhivare
unzip WEEK1-14.zip

# Verificare structură
tree -L 2 WEEK*

# Setare permisiuni pentru scripturi
find . -name "*.sh" -exec chmod +x {} \;
find . -name "*.py" -exec chmod +x {} \;
```

---

## 10. Script de Verificare

Creează un script pentru verificarea instalării complete:

```bash
cat > ~/networking/scripts/verify_installation.sh << 'SCRIPT'
#!/bin/bash
# =============================================================================
# Script de Verificare Instalare - Networking Lab Ubuntu 24.04
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     VERIFICARE INSTALARE - NETWORKING LAB UBUNTU 24.04       ║"
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

echo "═══ SISTEM ═══"
check_version "cat /etc/os-release | grep PRETTY_NAME | cut -d'\"' -f2" "OS"
check_version "uname -r" "Kernel"

echo ""
echo "═══ PYTHON ═══"
check "python3 --version" "Python3" || ((ERRORS++))
check "pip3 --version" "Pip3" || ((ERRORS++))

echo ""
echo "═══ BIBLIOTECI PYTHON ═══"
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
echo "═══ INSTRUMENTE REȚEA ═══"
for tool in tcpdump tshark nmap hping3 iperf3 netcat curl wget traceroute; do
    check "which $tool" "$tool" || ((ERRORS++))
done

echo ""
echo "═══ PERMISIUNI ═══"
check "groups | grep -q docker" "User in docker group" || ((ERRORS++))
check "groups | grep -q wireshark" "User in wireshark group" || ((ERRORS++))

echo ""
echo "═══ SERVICII ═══"
check "systemctl is-active ssh" "SSH" || ((ERRORS++))
check "systemctl is-active docker" "Docker" || ((ERRORS++))
check "systemctl is-active openvswitch-switch" "OVS" || ((ERRORS++))

echo ""
echo "═══ REȚEA ═══"
echo "Interfețe de rețea:"
ip -br addr show

echo ""
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  TOATE VERIFICĂRILE AU TRECUT CU SUCCES!                     ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  $ERRORS ERORI DETECTATE - VERIFICĂ INSTALAREA!                 ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
fi

exit $ERRORS
SCRIPT

chmod +x ~/networking/scripts/verify_installation.sh
```

**Rulare verificare:**
```bash
~/networking/scripts/verify_installation.sh
```

---

## 11. Troubleshooting

### 11.1 Probleme Comune și Soluții

#### Docker: "permission denied"
```bash
# Cauză: Utilizatorul nu e în grupul docker
sudo usermod -aG docker $USER
# Apoi logout/login sau:
newgrp docker
```

#### Mininet: "Cannot find required executable..."
```bash
# Cauză: OVS nu rulează
sudo systemctl start openvswitch-switch
sudo mn -c  # Cleanup
```

#### TShark: "permission denied"
```bash
# Cauză: Permisiuni insuficiente
sudo usermod -aG wireshark $USER
sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/dumpcap
newgrp wireshark
```

#### Python: "externally-managed-environment"
```bash
# Cauză: Ubuntu 24.04 protejează pachetele sistem
# Soluție 1: Folosește --break-system-packages
pip3 install package --break-system-packages

# Soluție 2: Folosește venv (recomandat pentru proiecte de producție)
python3 -m venv ~/venv
source ~/venv/bin/activate
pip install package
```

#### Python: "Cannot uninstall X, RECORD file not found"
```bash
# Cauză: Conflict între pachete instalate de apt și pip
# Soluție: Adaugă --ignore-installed
sudo pip3 install --break-system-packages --ignore-installed flask

# Pentru mai multe pachete:
sudo pip3 install --break-system-packages --ignore-installed package1 package2
```

#### Port 53 ocupat (DNS)
```bash
# Cauză: systemd-resolved ocupă portul
sudo systemctl stop systemd-resolved
# Sau folosește alt port pentru DNS custom (ex: 5353)
```

#### Mininet cleanup
```bash
# După crash sau erori, curăță cu:
sudo mn -c
sudo ovs-vsctl --if-exists del-br ovs-br0
sudo killall controller 2>/dev/null
```

### 11.2 Comenzi Utile de Diagnostic

```bash
# Verificare porturi în uz
sudo ss -tulpn
sudo netstat -tulpn

# Verificare procese de rețea
ps aux | grep -E "(python|docker|mn|ovs)"

# Verificare log-uri sistem
sudo journalctl -xe
sudo journalctl -u docker
sudo journalctl -u openvswitch-switch

# Verificare spațiu disk
df -h

# Verificare memorie
free -h

# Verificare conectivitate
ping -c 3 8.8.8.8
ping -c 3 google.com
```

---

## Rezumat Comenzi Complete (Script All-in-One)

Pentru comoditate, toate comenzile de instalare într-un singur bloc:

```bash
#!/bin/bash
# RULEAZĂ CU: sudo bash install_networking_lab.sh

set -e

echo "=== Actualizare sistem ==="
apt update && apt upgrade -y

echo "=== Pachete esențiale ==="
apt install -y build-essential software-properties-common apt-transport-https \
    ca-certificates gnupg lsb-release curl wget git vim nano htop tree unzip zip jq make gcc g++

echo "=== Instrumente rețea ==="
apt install -y iputils-ping iproute2 net-tools dnsutils traceroute mtr-tiny whois \
    netcat-openbsd socat curl wget lftp openssh-client tcpdump iftop nethogs nload bmon \
    nmap hping3 iperf3 arping iptables iptables-persistent conntrack bridge-utils vlan arptables

echo "=== Python ==="
apt install -y python3 python3-pip python3-venv python3-dev python3-setuptools python3-wheel

echo "=== Biblioteci Python ==="
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

echo "=== Configurări finale ==="
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.d/99-networking.conf
echo "net.ipv6.conf.all.forwarding=1" >> /etc/sysctl.d/99-networking.conf
sysctl --system

echo "=== INSTALARE COMPLETĂ ==="
echo "Rulează următoarele comenzi manual ca utilizator normal:"
echo "  sudo usermod -aG docker \$USER"
echo "  sudo usermod -aG wireshark \$USER"
echo "  newgrp docker"
echo "  newgrp wireshark"
```

---

**Document generat pentru cursul de Rețele de Calculatoare, ASE-CSIE București**
