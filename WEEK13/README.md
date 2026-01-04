# Week 13 Starterkit — IoT and Security in Computer Networks

> **Course**: Computer Networks  
> **Academic Year**: 2025-2026  
> **Semester**: 2  
> **Teaching Staff**: Assoc. Prof. TOMA Andrei, Assoc. Prof. TIMOFTE Carmen Manuela, Lecturer ILIE-NEMEDI Iulian, Teaching Asst. CIMPEANU IONUT ALEXANDRU

> **Version**: 1.1.0 | **Plan IP**: 10.0.13.0/24 | Licence: MIT

---

## Pedagogical Vision

This kit integrates **two complementary perspectives on security**:

1. **Offensive perspective** — understanding how attackers think and operate
2. **Defensive perspective** — implementing protection measures and hardening

This dual approach aims to form a holistic understanding: *you cannot defend what you do not understand how it can be attacked*.

---

## Kit Structure

```
starterkit_s13/
├── README.md                           # Acest document
├── Makefile                            # Automations one-command
├── docker-compose.yml                  # Infrastructure container
├── requirements.txt                    # Dependencies Python
│
├── docs/
│   ├── teoria/
│   │   ├── 00_introducere_securitate.md
│   │   ├── 01_iot_fundamentals.md
│   │   ├── 02_attack_vectors.md
│   │   ├── 03_defensive_measures.md
│   │   └── 04_practical_workflow.md
│   └── slides/
│       ├── CURS_13_outline.md          # Course presentation outline
│       └── SEMINAR_13_outline.md       # Seminar presentation outline
│
├── scripts/
│   ├── setup.sh                        # Installation completa
│   ├── cleanup.sh                      # Cleanup procese
│   ├── run_demo_offensive.sh           # Demo complet ofensiv
│   ├── run_demo_defensive.sh           # Demo complet defensiv
│   └── capture_traffic.sh              # Captura automata trafic
│
├── python/
│   ├── exercises/
│   │   ├── ex_01_port_scanner.py       # Scanner TCP avansat
│   │   ├── ex_02_mqtt_client.py        # Client MQTT (pub/sub)
│   │   ├── ex_03_packet_sniffer.py     # Analiza pachete (scapy)
│   │   └── ex_04_vuln_checker.py       # Verificator vulnerabilitati
│   ├── exploits/
│   │   ├── ftp_backdoor_vsftpd.py      # Exploit CVE-2011-2523
│   │   └── banner_grabber.py           # Enumerare servicii
│   └── utils/
│       ├── net_utils.py                # Utilitare retea
│       └── report_generator.py         # Generator rapoarte
│
├── docker/
│   ├── Dockerfile.vulnerable           # Container tinte vulnerabile
│   └── docker-compose.pentest.yml      # Stack complet pentest
│
├── mininet/
│   ├── topologies/
│   │   ├── topo_base.py                # Topologie simpla
│   │   └── topo_segmented.py           # Topologie cu segmentare
│   └── scenarios/
│       └── lab_scenario.md             # Scenarii de laborator
│
├── configs/
│   ├── mosquitto/
│   │   ├── mosquitto_plain.conf
│   │   ├── mosquitto_tls.conf
│   │   └── mosquitto_acl.acl
│   └── certs/                          # Generate de setup.sh
│
├── tests/
│   ├── smoke_test.sh                   # Verificare rapida
│   └── expected_outputs.md             # Rezultate asteptate
│
└── html/
    ├── presentation_curs.html          # Prezentare interactiva curs
    └── presentation_seminar.html       # Prezentare interactiva seminar
```

---

## Quickstart (3 minute)

### Option A: Automatic demo (recommended for quick verification)

```bash
# 1. Verificare mediu
./scripts/verify.sh

# 2. Demo automat (genereaza artefacte)
./scripts/run_all.sh --quick

# 3. Verificare artefacte
ls -la artifacts/
# Asteptat: demo.log, demo.pcap, validation.txt

# 4. Smoke test complet
./tests/smoke_test.sh
```

### Option B: Docker (recommended for pentest)

```bash
# 1. Setup si pornire
make setup
make docker-up

# 2. Verificare
make test

# 3. Demo complet ofensiv
make demo-offensive

# 4. Cleanup
make docker-down
```

### Option B: Mininet (recommended for IoT/SDN)

```bash
# 1. Setup complet
sudo make setup-mininet

# 2. Running topologie
sudo make mininet-base

# 3. In CLI mininet: pingall, apoi scenarii
```

---

## Detailed Content

### Part I: IoT and Protocols (60 min)

| Activity | Duration | Files |
|------------|--------|---------|
| IoT Fundamentals | 15 min | `docs/teoria/01_iot_fundamentals.md` |
| MQTT in Practice | 20 min | `python/exercises/ex_02_mqtt_client.py` |
| Traffic Capture and Analysis | 15 min | `scripts/capture_traffic.sh` |
| TLS and Authentication | 10 min | `configs/mosquitto/` |

### Part II: Security Offensive (50 min)

| Activity | Duration | Files |
|------------|--------|---------|
| Port Scanning | 15 min | `python/exercises/ex_01_port_scanner.py` |
| Vulnerability Enumeration | 15 min | `python/exploits/banner_grabber.py` |
| Controlled Exploitation | 20 min | `python/exploits/ftp_backdoor_vsftpd.py` |

### Part III: Security Defensiva (30 min)

| Activity | Duration | Files |
|------------|--------|---------|
| Network Segmentation | 15 min | `mininet/topologies/topo_segmented.py` |
| Hardening Measures | 15 min | `docs/teoria/03_defensive_measures.md` |

---

## Available Makefile Commands

```bash
# === SETUP ===
make setup              # Installation dependente + certificate
make setup-mininet      # Complete setup for Mininet (sudo)

# === DOCKER ===
make docker-up          # Pornire containere vulnerabile
make docker-down        # Oprire si curatare containere
make docker-logs        # Vizualizare loguri containere

# === DEMONSTRATII ===
make demo-offensive     # Secventa completa: scan → enum → exploit
make demo-defensive     # Secventa: TLS → ACL → segmentare
make demo-mqtt-plain    # MQTT fara criptare (captura vizibila)
make demo-mqtt-tls      # MQTT cu TLS (captura criptata)

# === EXERCITII ===
make scan TARGET=10.0.13.11        # Scanare porturi
make mqtt-pub TOPIC=home/temp      # Publicare MQTT
make mqtt-sub TOPIC=home/temp      # Abonare MQTT
make exploit-ftp                   # Exploit vsftpd

# === MININET ===
make mininet-base       # Topologie baza (sudo)
make mininet-extended   # Topologie segmentata (sudo)
make mininet-clean      # Cleanup Mininet (sudo)

# === TESTE ===
make test               # Smoke test complet
make lint               # Verificare sintaxa Python

# === CURATARE ===
make clean              # Cleanup fisiere temporare
make clean-all          # Reset complet
```

---

## Recommended Workflow for Students

### Pas 1: Environment Preparation (10 min)

```bash
git clone <repo> && cd starterkit_s13
make setup
make test
```

### Pas 2: Conceptual Understanding (15 min)

1. Read `docs/teoria/00_introducere_security.md`
2. Identify differences between offensive and defensive approaches
3. Note 3 questions for the laboratory

### Pas 3: Offensive Practice (30 min)

```bash
make docker-up
make demo-offensive
# Observa output-ul fiecarei etape
```

### Pas 4: Defensive Practice (30 min)

```bash
make demo-defensive
# Compara mqtt_plain.pcap cu mqtt_tls.pcap
```

### Pas 5: Documentation and Reflection (15 min)

Complete the file `REZULTATE_S13.txt` with:
- Relevant screenshots
- Answers to the questions from each exercise
- 3 applied security measures

---

## System Requirements

### Minimum

- Linux (Ubuntu 22.04+ / Debian 12+)
- Python 3.10+
- Docker 24+ and Docker Compose v2
- 4 GB RAM
- 10 GB disk space

### Recommended

- 8 GB RAM (for Mininet + Docker simultaneously)
- Root access (for Mininet)
- VS Code with Python and Docker extensions

---

## Troubleshooting

| Symptom | Probable Cause | Solution |
|---------|-----------------|---------|
| `docker: command not found` | Docker not installed | `sudo apt install docker.io docker-compose-v2` |
| `Allowedsion denied` at Docker | User not in docker group | `sudo usermod -aG docker $USER && newgrp docker` |
| Port 8888 ocupat | Another service running | `sudo lsof -i :8888` and stop the service |
| `mn: command not found` | Mininet not installed | `sudo apt install mininet` |
| OVS crash | Service stopped | `sudo service openvswitch-switch restart` |
| Certificateses expired | Old certificateses | `rm -rf configs/certs && make setup` |
| `paho-mqtt` import error | Missing dependency | `pip install -r requirements.txt` |
| Mininet stale state | Old processes | `sudo make mininet-clean` |

---

## Bibliographic References

1. Kurose, J., Ross, K. (2016). *Computer Networking: A Top-Down Approach*, 7th Edition. Pearson.
2. Rhodes, B., Goetzen, J. (2014). *Foundations of Python Network Programming*. Apress.
3. Timofte, C., Constantinescu, R., Nemedi, I. (2004). *Networks of calculatoare – caiet of seminar*. ASE.
4. OWASP IoT Security Verification Standard (ISVS). [https://owasp.org/www-project-iot-security-verification-standard/](https://owasp.org/www-project-iot-security-verification-standard/)
5. Eclipse Mosquitto Documentation. [https://mosquitto.org/documentation/](https://mosquitto.org/documentation/)

---

## Assessment and Submission

According to the course syllabus, by the end of the semester the following must be submitted:

1. **Team Project** (15% of final grade):
   - Functional client-server application
   - Technical documentation
   - Demonstration presentation

2. **Seminar Tests** (15% of final grade):
   - 3 short tests throughout the course
   - Theoretical and practical knowledge

3. **Written Examination** (70% of final grade):
   - Computer-based
   - Fundamental networking concepts

---

## Support and Contact

- **Course Platform**: online.ase.ro
- **Team Email**: retele-calc@ie.ase.ro
- **Consultations**: according to the schedule posted on the platform

---

*Last updated: Decembrie 2025*
