# Week 13 Checklist

Use this checklist to validate your laboratory submission artefacts and reproducibility.

## Environment
- [ ] Ubuntu 24.04 is used, or the environment is equivalent
- [ ] `make setup` completes successfully
- [ ] `make verify` completes successfully

## Docker lab
- [ ] `make docker-up` starts Mosquitto, DVWA and vsftpd
- [ ] `.env` exists and contains host port mappings
- [ ] DVWA is reachable in a browser at `http://127.0.0.1:${DVWA_HOST_PORT}/`

## MQTT
- [ ] `make demo-mqtt-plain` publishes messages successfully
- [ ] `make demo-mqtt-tls` publishes messages successfully using `configs/certs/ca.crt`
- [ ] You can subscribe and observe messages using `make mqtt-sub`

## Reconnaissance and defensive interpretation
- [ ] `make scan` produces `artifacts/scan_results.json`
- [ ] `make exploit-ftp` runs and prints the backdoor port reachability result (safe stub)
- [ ] `python3 python/exercises/ex_04_vuln_checker.py --service http` runs against DVWA

## Artefacts
- [ ] `artifacts/demo.log` exists (created by `make run-all`)
- [ ] `artifacts/validation.txt` exists (created by `make run-all`)
- [ ] Optional: `artifacts/capture.pcap` exists if you captured traffic

## Clean-up
- [ ] `make docker-down` completes successfully
- [ ] `make reset` returns the system to a clean lab state
