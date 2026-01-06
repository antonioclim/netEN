# Week 13 Laboratory Scenarios
## IoT and Security in Computer Networks

Estimated duration: 120 minutes  
Difficulty: intermediate to advanced

This guide describes a set of repeatable laboratory scenarios based on the Week 13 kit:
- Docker-based lab services (DVWA, Mosquitto, vsftpd with a safe stub port)
- Python tools (port scanner, MQTT client, vulnerability checker)
- Optional Mininet topologies for segmentation exercises

---

## Contents
1. Preparation and verification
2. Scenario A: Offensive perspective (reconnaissance)
3. Scenario B: Defensive perspective (observability)
4. Scenario C: MQTT and IoT messaging patterns
5. Scenario D: Segmentation and firewall in Mininet (optional)
6. Clean-up

---

## 1. Preparation and verification

From the Week 13 folder:

```bash
make setup
make verify
```

If Docker commands fail, you are likely not in the `docker` group. In that case use:

```bash
sudo make docker-up
```

---

## 2. Scenario A: Offensive perspective
Goal: enumerate exposed services and interpret the attack surface.

### 2.1 Start the lab services
```bash
make docker-up
```

Note the printed ports in `.env`. If your system already uses port 8080 or 2121, delete `.env` and rerun `make env`.

### 2.2 Run a targeted port scan
```bash
make scan TARGET=127.0.0.1
```

Inspect:
- `artifacts/scan_results.json`
- the list of open ports and their inferred services

### 2.3 Backdoor port demonstration (safe)
```bash
make exploit-ftp TARGET=127.0.0.1
```

This step is intentionally safe. It checks whether an unexpected TCP port is reachable and records the banner. No command execution is provided by the lab container.

---

## 3. Scenario B: Defensive perspective
Goal: observe traffic and relate transport decisions to observable artefacts.

### 3.1 Start a capture
In a separate terminal:

```bash
sudo make capture-start IFACE=any
```

### 3.2 Generate MQTT plaintext traffic
```bash
make demo-mqtt-plain
```

### 3.3 Generate MQTT TLS traffic
```bash
make demo-mqtt-tls
```

### 3.4 Stop the capture
```bash
sudo make capture-stop
```

Open `artifacts/capture.pcap` in Wireshark. Compare plaintext payload visibility vs TLS encrypted payloads.

---

## 4. Scenario C: MQTT and IoT messaging patterns
Goal: demonstrate publish and subscribe, topic design and wildcard subscriptions.

### 4.1 Subscribe to a topic filter
In terminal 1:
```bash
make mqtt-sub TOPIC='iot/sensors/#'
```

### 4.2 Publish messages
In terminal 2:
```bash
make mqtt-pub TOPIC='iot/sensors/temperature' MESSAGE='{"sensor":"temp","value":25.1}'
make mqtt-pub TOPIC='iot/sensors/humidity' MESSAGE='{"sensor":"hum","value":41.0}'
```

Observe how topic design affects routing and how wildcard filters capture multiple streams.

---

## 5. Scenario D: Segmentation and firewall in Mininet (optional)
Goal: understand segmentation boundaries and firewall enforcement.

### 5.1 Start the segmented topology
```bash
sudo make mininet-extended
```

### 5.2 Validate connectivity
From the Mininet CLI:

```text
mininet> pingall
mininet> sensor1 nc -vz 10.0.2.100 1883
mininet> sensor1 nc -vz 10.0.2.100 80
```

Expected:
- MQTT ports (1883 and 8883) are allowed IoT -> broker
- other IoT -> management traffic is blocked by the router policy

---

## 6. Clean-up
To stop Docker services and remove containers and networks:

```bash
make docker-down
```

To remove captures and temporary files:

```bash
make clean
```

For a full reset (Docker, Mininet and captures):

```bash
make reset
```
