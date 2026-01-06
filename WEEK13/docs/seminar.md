# Week 13 Seminar Notes
## IoT and Security in Computer Networks

This seminar uses a controlled laboratory environment to explore basic IoT security concepts:
- MQTT publish and subscribe flows
- plaintext vs TLS transport and what changes on the wire
- defensive observability (captures, logs and simple fingerprinting)
- safe enumeration of exposed services

The kit provides:
- Docker services: Mosquitto (MQTT), DVWA (web) and vsftpd with a safe stub port
- Python tools: port scanner, MQTT client and a defensive vulnerability checker
- Optional Mininet topologies for segmentation exercises

## Suggested seminar flow

### 1. Setup and verification
```bash
make setup
make verify
```

### 2. Start the Docker lab
```bash
make docker-up
```

### 3. Run the MQTT demos
Plaintext:
```bash
make demo-mqtt-plain
```

TLS:
```bash
make demo-mqtt-tls
```

### 4. Capture traffic (optional)
In a separate terminal:
```bash
sudo make capture-start IFACE=any
```

Re-run `make demo-mqtt-plain` and `make demo-mqtt-tls`, then stop the capture:
```bash
sudo make capture-stop
```

Open `artifacts/capture.pcap` in Wireshark and compare plaintext visibility vs TLS encryption.

### 5. Reconnaissance and interpretation
```bash
make scan TARGET=127.0.0.1
```

Inspect `artifacts/scan_results.json` and discuss:
- which ports are open
- which services they correspond to
- which exposures are expected in a hardened deployment

### 6. Safe backdoor port demonstration
```bash
make exploit-ftp TARGET=127.0.0.1
```

This is intentionally safe and demonstrates detection of an unexpected exposed port without providing exploitation capability.

### 7. Clean-up
```bash
make docker-down
make clean
```
