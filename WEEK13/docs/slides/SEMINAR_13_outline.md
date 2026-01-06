# Week 13 Seminar Outline
## IoT Lab: MQTT, Reconnaissance and Defensive Observability

### Seminar goals
- Run a controlled IoT lab environment using Docker
- Observe MQTT plaintext and MQTT over TLS traffic patterns
- Perform basic reconnaissance (target reachability and port exposure)
- Understand how misconfiguration changes the attack surface
- Produce repeatable artefacts (logs, JSON scan output and PCAP files)

### Seminar structure
1. Environment verification and setup
   - `make setup` and `make verify`
2. Bring up the lab services
   - `make docker-up`
3. MQTT plaintext demo
   - publish, subscribe and traffic capture
4. MQTT TLS demo
   - CA file usage and what changes on the wire
5. Port exposure and defensive interpretation
   - `make scan` and reading JSON results
6. Safe backdoor port demonstration
   - `make exploit-ftp` (detection and safe handling, no exploitation)
7. Wrap-up
   - artefacts, clean-up and troubleshooting

### Deliverables
- `artifacts/scan_results.json`
- `artifacts/demo.log`
- optional `artifacts/capture.pcap` from `make capture-start` / `make capture-stop`
