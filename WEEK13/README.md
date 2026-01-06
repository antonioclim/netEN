# Week 13 Starter Kit — IoT and Security in Computer Networks

Computer Networks — ASE-CSIE (2025–2026, Semester 2)

**Version:** 1.2.0  \
**Suggested lab IP plan:** 10.0.13.0/24  \
**Licence:** MIT

This starter kit provides a reproducible laboratory sandbox for exploring **IoT traffic patterns and security basics**.

The practical focus is:
- MQTT messaging (publish and subscribe)
- plaintext vs TLS transport
- basic reconnaissance outputs (open ports and banners)
- defensive interpretation and light-weight reporting

The kit is intentionally opinionated:
- a small, canonical set of `make` targets
- a local Python virtual environment (`./.venv`) to avoid PEP 668 issues
- a Docker lab stack for intentionally vulnerable services
- deterministic artefacts written under `./artifacts/`

---

## Safety and ethical use

This kit includes security-oriented demonstrations (port scanning, banner checks and intentionally vulnerable services). Use it **only**:
- on systems you own or have explicit authorisation to test
- inside the course laboratory environment
- with defensive intent and for learning

Do not run the tooling against public networks or third-party infrastructure.

---

## Contents

- [1. Quick start](#1-quick-start)
- [2. Requirements](#2-requirements)
- [3. Concept primer](#3-concept-primer)
- [4. What this kit provides](#4-what-this-kit-provides)
- [5. Directory layout](#5-directory-layout)
- [6. Setup and verification](#6-setup-and-verification)
- [7. Docker lab stack](#7-docker-lab-stack)
- [8. Demos](#8-demos)
  - [Demo A: Full automated run](#demo-a-full-automated-run)
  - [Demo B: Reconnaissance and safe service checks](#demo-b-reconnaissance-and-safe-service-checks)
  - [Demo C: MQTT plaintext publish and subscribe](#demo-c-mqtt-plaintext-publish-and-subscribe)
  - [Demo D: MQTT over TLS](#demo-d-mqtt-over-tls)
  - [Demo E: Observing plaintext vs TLS on the wire](#demo-e-observing-plaintext-vs-tls-on-the-wire)
  - [Demo F: Optional Mininet topologies](#demo-f-optional-mininet-topologies)
- [9. Laboratory exercises](#9-laboratory-exercises)
- [10. Artefacts and submission](#10-artefacts-and-submission)
- [11. Troubleshooting](#11-troubleshooting)
- [Further reading](#further-reading)

---

## 1. Quick start

### 1.1 Clone only Week 13 from the monorepo

This repository is a monorepo (Weeks 1–14). You can download only Week 13 using sparse checkout.

Option A — one-liner (recommended for students)

```bash
cd ~ && \
  git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK13 && \
  cd WEEK13 && \
  git sparse-checkout set WEEK13 && \
  shopt -s dotglob && mv WEEK13/* . && rmdir WEEK13 && \
  find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

Option B — step by step

```bash
cd ~

git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK13
cd ./WEEK13

git sparse-checkout set WEEK13

shopt -s dotglob
mv WEEK13/* .
rmdir WEEK13

find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

### 1.2 Canonical workflow

Minimal workflow:

```bash
make setup
make verify
make docker-up
make demo-offensive
```

If you want an end-to-end automated run that produces artefacts:

```bash
make run-all
```

Expected output (abridged):
- `make setup` ends with **“Setup complete”**
- `make verify` ends with **“Verification complete”**
- `make docker-up` shows containers in **Up** state
- `make run-all` writes `artifacts/demo.log` and `artifacts/validation.txt`

---

## 2. Requirements

### 2.1 Operating system

Tested on **Ubuntu 24.04 LTS**.

### 2.2 System packages

Required:
- Python 3 and `python3-venv`
- GNU Make
- OpenSSL
- Docker Engine and the Docker Compose plugin (`docker compose`)

Helpful (optional but recommended):
- `curl` and `nc` (netcat)
- `tcpdump` and `tshark` for captures
- Mininet and Open vSwitch for the optional topology demos

Suggested installation:

```bash
sudo apt-get update
sudo apt-get install -y \
  python3 python3-venv python3-pip \
  make openssl curl netcat-openbsd \
  tcpdump tshark
```

Optional Mininet tooling:

```bash
sudo apt-get install -y mininet openvswitch-switch
```

---

## 3. Concept primer

This section is short by design. It tells you what you should be able to explain after completing the lab.

### 3.1 MQTT in one minute

MQTT is a lightweight publish and subscribe protocol commonly used in IoT.
- a **broker** accepts client connections and routes messages
- publishers send messages to a **topic** (a string such as `iot/sensors/temperature`)
- subscribers receive messages for topics they subscribe to (topics can use wildcards such as `iot/sensors/#`)

In this kit:
- plaintext broker listens on port **1883**
- TLS broker listens on port **8883**

### 3.2 What TLS changes

TLS encrypts application payloads, but it does not hide everything.

What becomes hard to observe in a capture:
- MQTT payload content
- topic strings and application-level headers

What remains observable (metadata):
- endpoints (IP addresses and ports)
- timing patterns (when flows start and how often they send)
- approximate message sizes (record sizes)

This is why “encrypting transport” does not automatically equal “hiding behaviour”.

### 3.3 Port scanning and states

The port scanner in this kit uses a TCP connect approach. For each port it tries to complete the TCP handshake:
- **open**: connection succeeds
- **closed**: connection refused
- **filtered**: connection times out (often due to a firewall drop)

A port scan alone does not prove vulnerability. It is only a first indicator of exposure.

---

## 4. What this kit provides

### 4.1 Docker services

The Docker lab stack starts three services:
- **Mosquitto** MQTT broker (plaintext and TLS)
- **DVWA** (Damn Vulnerable Web Application) as an intentionally vulnerable web target
- **vsftpd** with a safe educational stub port used for detection exercises

Ports are configurable via `.env` which is generated by `make setup`.

### 4.2 Python tools

Implemented under `python/`:
- `exercises/ex_01_port_scanner.py` — TCP connect scanner with JSON export
- `exercises/ex_02_mqtt_client.py` — MQTT publish and subscribe (plaintext and TLS)
- `exercises/ex_03_packet_sniffer.py` — simple sniffer skeleton (Scapy)
- `exercises/ex_04_vuln_checker.py` — defensive checks (no exploitation)
- `exploits/ftp_backdoor_vsftpd.py` — safe backdoor port reachability check (educational)

### 4.3 Canonical Makefile targets

Use `make help` to see all targets.

The main targets you will use:
- `make setup`, `make verify`
- `make docker-up`, `make docker-down`
- `make demo-offensive`, `make demo-defensive`
- `make demo-mqtt-plain`, `make demo-mqtt-tls`
- `make scan`, `make exploit-ftp`
- `make run-all` (fully automated, produces artefacts)

---

## 5. Directory layout

```text
WEEK13/
  Makefile
  README.md
  requirements.txt

  artifacts/               # generated logs, JSON reports and captures
  configs/
    certs/                 # generated MQTT TLS certificates
    mosquitto/             # broker configuration
  docker/
    docker-compose.yml     # lab services (Mosquitto, DVWA and vsftpd)
  docs/                    # lecture, seminar and laboratory notes
  mininet/                 # optional topologies
  python/                  # exercises and utilities
  scripts/                 # helper scripts used by the Makefile
  tests/                   # smoke tests and expected outputs
```

---

## 6. Setup and verification

### 6.1 `make setup`

What it does:
1. Creates `./.venv` (Python virtual environment)
2. Installs Python dependencies from `requirements.txt`
3. Generates MQTT TLS certificates under `configs/certs/`
4. Generates `.env` for Docker port mappings
5. Ensures `./artifacts/` exists

Run:

```bash
make setup
```

Expected output (abridged):
- “Creating Python virtual environment”
- “Installing Python dependencies”
- “Generating MQTT TLS certificates”
- “Preparing Docker environment file”
- “Setup complete”

### 6.2 `make verify`

Run:

```bash
make verify
```

Expected output (abridged):
- “Week 13 - Environment verification”
- “Python modules (venv): ✓ paho.mqtt.client”
- “Result: ✓ Verification complete”

---

## 7. Docker lab stack

### 7.1 Start services

```bash
make docker-up
```

Expected output (abridged):
- a `docker compose ps` table where Mosquitto, DVWA and vsftpd are **Up**
- an informational note suggesting `sudo make docker-up` if needed

Quick health checks (optional):

```bash
docker compose -f docker/docker-compose.yml ps
ss -lntp | egrep ':(1883|8883|8080|2121|6200)\b' || true
```

### 7.2 Stop services

```bash
make docker-down
```

### 7.3 Where to connect

After `make docker-up`, endpoints are:
- DVWA: `http://127.0.0.1:${DVWA_HOST_PORT}/` (default 8080)
- vsftpd: `127.0.0.1:${VSFTPD_HOST_PORT}` (default 2121)
- MQTT plaintext: `127.0.0.1:${MQTT_PLAIN_PORT}` (default 1883)
- MQTT TLS: `127.0.0.1:${MQTT_TLS_PORT}` (default 8883)

The actual values are stored in `.env`.

---

## 8. Demos

All demos below assume you have run:

```bash
make setup
make verify
make docker-up
```

### Demo A: Full automated run

This is the quickest way to validate the kit end to end.

```bash
make run-all
```

Expected output (abridged):
- “Week 13 automated run started” in `artifacts/demo.log`
- `artifacts/validation.txt` includes lines such as `MQTT_PLAIN: PASS`

Expected artefacts:
- `artifacts/demo.log`
- `artifacts/validation.txt`
- `artifacts/scan_results.json`

### Demo B: Reconnaissance and safe service checks

Goal: detect exposed services, interpret open ports and run a safe educational backdoor check.

```bash
make scan
make exploit-ftp
make demo-defensive
```

Expected output (abridged):
- `make scan` prints: “✓ Results: artifacts/scan_results.json”
- `make exploit-ftp` prints: “Result: backdoor port is reachable (for the Week 13 lab this is a simulated stub).”
- `make demo-defensive` prints a brief report and writes JSON under `artifacts/`

What you should observe:
- open ports corresponding to the Docker services (DVWA, MQTT and vsftpd)
- optional banners depending on what the service returns
- JSON reports you can reference in a write-up

### Demo C: MQTT plaintext publish and subscribe

Goal: observe cleartext MQTT messaging, then confirm that subscribers receive the payload.

Terminal 1 — subscribe

```bash
make mqtt-sub TOPIC='iot/sensors/#'
```

Terminal 2 — publish three messages

```bash
make demo-mqtt-plain TOPIC='iot/sensors/temperature' MESSAGE='{"sensor":"temp","value":24.3}'
```

Expected output (abridged):
- Terminal 1 prints one or more blocks starting with:
  - `Week 13 - MQTT subscribe`
  - `[MESSAGE] topic=iot/sensors/temperature`
- Terminal 2 prints:
  - `Week 13 - MQTT publish`
  - `[PUBLISH] sent 1/3 ...` and `[PUBLISH] sent 2/3 ...`

What you should observe:
- the same JSON payload appears in the subscriber output
- in plaintext mode you can capture and read the payload on the wire

### Demo D: MQTT over TLS

Goal: confirm that MQTT over TLS still delivers messages, but payload visibility changes on the wire.

Terminal 1 — subscribe over TLS

```bash
./.venv/bin/python python/exercises/ex_02_mqtt_client.py \
  --broker 127.0.0.1 --port 8883 \
  --mode subscribe --topic 'iot/sensors/#' --timeout 20 \
  --tls --cafile configs/certs/ca.crt
```

Terminal 2 — publish via TLS port

```bash
make demo-mqtt-tls TOPIC='iot/sensors/temperature' MESSAGE='{"sensor":"temp","value":24.3}'
```

Expected output (abridged):
- subscriber prints `TLS: True` and shows it connected to port 8883
- publisher prints `TLS: True` and shows `CA file: configs/certs/ca.crt`

What you should observe:
- the publish still succeeds and is acknowledged
- packet captures will show TLS handshake and encrypted records rather than cleartext MQTT payload

### Demo E: Observing plaintext vs TLS on the wire

Goal: correlate application behaviour with packet capture evidence.

Terminal 1 — start capture

```bash
sudo make capture-start IFACE=any
```

Terminal 2 — run plaintext publish

```bash
make demo-mqtt-plain
```

Terminal 3 — run TLS publish

```bash
make demo-mqtt-tls
```

Terminal 1 — stop capture

```bash
sudo make capture-stop
```

Expected output (abridged):
- capture start prints: “✓ Capturing on any to artifacts/capture.pcap”
- capture stop prints: “✓ Capture stopped: artifacts/capture.pcap”

Quick analysis with tshark (optional):

```bash
tshark -r artifacts/capture.pcap -Y 'tcp.port==1883' -T fields -e frame.number -e ip.src -e ip.dst -e tcp.len | head

tshark -r artifacts/capture.pcap -Y 'tcp.port==8883 && tls' -T fields -e frame.number -e ip.src -e ip.dst -e tls.handshake.type | head
```

What you should observe:
- plaintext: MQTT packets on port 1883 and readable payload
- TLS: TLS handshake and application data on port 8883, payload not readable without keys

### Demo F: Optional Mininet topologies

These topologies are optional and require Mininet and Open vSwitch.

Base topology:

```bash
sudo make mininet-base
```

Extended topology:

```bash
sudo make mininet-extended
```

Expected output (abridged):
- Mininet starts and provides the `mininet>` CLI prompt
- `nodes` and `net` show the topology

Cleanup:

```bash
sudo make mininet-clean
```

---

## 9. Laboratory exercises

A suggested laboratory progression is documented in `docs/lab.md`. This section gives a concise checklist for students.

1. **Prepare**
   - `make setup`
   - `make verify`

2. **Start services**
   - `make docker-up`
   - confirm ports using `ss -lntp`

3. **Reconnaissance**
   - `make scan TARGET=127.0.0.1 PORTS=1-1024`
   - interpret open ports and map them to services

4. **MQTT plaintext**
   - run Demo C and capture traffic
   - identify MQTT flows on port 1883

5. **MQTT TLS**
   - run Demo D and reuse the same capture method
   - compare what is observable with TLS enabled

6. **Defensive interpretation**
   - `make demo-defensive`
   - read the JSON output under `artifacts/`

7. **Clean up**
   - `make docker-down`
   - `make clean` or `make reset`

---

## 10. Artefacts and submission

The kit writes reproducibility artefacts under `./artifacts/`.

Typical artefacts:
- `demo.log` — timestamped run log
- `validation.txt` — pass and fail markers for core checks
- `scan_results.json` — structured scan output
- `capture.pcap` — network capture (if you used `make capture-start`)

Recommended submission contents:
- `artifacts/demo.log`
- `artifacts/validation.txt`
- `artifacts/scan_results.json`
- `artifacts/capture.pcap` (optional but encouraged)

To create a submission archive:

```bash
zip -r WEEK13_submission.zip artifacts/
```

---

## 11. Troubleshooting

### Docker permission errors

If `make docker-up` fails with permissions, either:
- run it with sudo: `sudo make docker-up`
- or add your user to the docker group and re-login (recommended)

### Port conflicts

If a port is already in use, override it when generating `.env`:

```bash
make env DVWA_HOST_PORT=8081 VSFTPD_HOST_PORT=2122
make docker-up
```

### MQTT TLS failures

If `make demo-mqtt-tls` fails:
- ensure `configs/certs/ca.crt` exists (run `make certs` or `make setup`)
- ensure the TLS port is exposed and the broker is running (`make docker-up`)

### Capture permission errors

Capturing requires privileges. Use:

```bash
sudo make capture-start IFACE=any
```

### Reset the environment

```bash
make reset
```

This stops Docker services, cleans Mininet artefacts and removes temporary files.

---

## Further reading

See `docs/lab.md`, `docs/seminar.md` and `docs/cheatsheet.md` for structured laboratory tasks, suggested seminar flow and a short CLI reminder.
