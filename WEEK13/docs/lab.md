# Week 13 Laboratory Manual
## IoT and Security in Computer Networks

This laboratory focuses on basic IoT security practice in a controlled environment:
- MQTT messaging (publish and subscribe)
- the difference between plaintext and TLS transport
- reconnaissance outputs (open ports and banners)
- defensive interpretation and simple reporting

---

## Preparation

### 1. Install prerequisites (Ubuntu 24.04)
You should have:
- Python 3 and `python3-venv`
- Docker Engine and the Docker Compose plugin
- GNU Make
- OpenSSL

Optional:
- tcpdump and Wireshark
- Mininet and Open vSwitch

### 2. Setup the kit
From the Week 13 folder:

```bash
make setup
make verify
```

---

## Part A: Start the lab services

```bash
make docker-up
```

The chosen ports are written to `.env`. You can inspect it:

```bash
cat .env
```

---

## Part B: MQTT plaintext vs MQTT over TLS

### B1. Plaintext publish
```bash
make demo-mqtt-plain
```

### B2. TLS publish
```bash
make demo-mqtt-tls
```

Discussion prompts:
- Which parts of the traffic are visible in plaintext mode?
- What changes when TLS is enabled?
- What metadata remains observable even with TLS (endpoints, ports, timing, sizes)?

---

## Part C: Reconnaissance and exposure

### C1. Port scan
```bash
make scan TARGET=127.0.0.1
```

Inspect:
- `artifacts/scan_results.json`

### C2. Safe backdoor port check
```bash
make exploit-ftp TARGET=127.0.0.1
```

This check is intentionally safe and only demonstrates detection of an unexpected exposed port. No command execution is implemented in the lab container.

---

## Part D: Defensive checks and reporting

### D1. Vulnerability checker (defensive)
Example for DVWA:
```bash
python3 python/exercises/ex_04_vuln_checker.py --target 127.0.0.1 --port 8080 --service http
```

(Use the actual DVWA port from `.env` if it differs.)

### D2. Optional report generation
After running the automated pipeline:
```bash
make run-all
python3 python/utils/report_generator.py
```

This writes `artifacts/report.md`.

---

## Part E: Traffic capture

### E1. Capture with tcpdump
Start capture:
```bash
sudo make capture-start IFACE=any
```

Generate traffic (re-run demos):
```bash
make demo-mqtt-plain
make demo-mqtt-tls
```

Stop capture:
```bash
sudo make capture-stop
```

Open `artifacts/capture.pcap` in Wireshark and compare plaintext vs TLS flows.

### E2. Capture with Scapy (optional)
```bash
sudo python3 python/exercises/ex_03_packet_sniffer.py --iface any --timeout 20
```

---

## Clean-up

Stop Docker services:
```bash
make docker-down
```

Remove temporary files:
```bash
make clean
```

Full reset:
```bash
make reset
```
