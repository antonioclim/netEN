# Week 13 Assessment Rubric
## IoT and Security in Computer Networks

Total: 10 points

This rubric is designed to assess reproducible lab work, correct interpretation and clear documentation.

---

## A. Reproducibility and environment setup (2 points)
- **2**: `make setup` and `make verify` succeed, and the submission includes clear steps to reproduce the environment
- **1**: environment mostly works but some steps are missing or unclear
- **0**: environment cannot be reproduced

---

## B. MQTT demonstrations and interpretation (3 points)
- **3**: both plaintext and TLS demos run successfully, and the student explains what changes on the wire and what remains observable
- **2**: both demos run, interpretation is partial or superficial
- **1**: only one demo runs, or interpretation is incorrect
- **0**: no MQTT demonstration

---

## C. Reconnaissance and exposure analysis (3 points)
- **3**: port scan results are correctly interpreted, and exposed services are discussed with appropriate risk framing for IoT deployments
- **2**: scan is performed but the interpretation is incomplete
- **1**: scan is performed but interpretation is mostly incorrect
- **0**: no scan or no analysis

---

## D. Defensive checks and artefacts (2 points)
- **2**: defensive checks are executed (vulnerability checker and, if applicable, packet capture) and artefacts are provided with clear labelling
- **1**: artefacts exist but are incomplete or poorly documented
- **0**: no defensive checks or no artefacts

---

## Submission artefacts (recommended)
- `artifacts/scan_results.json`
- `artifacts/validation.txt`
- `artifacts/demo.log`
- optional `artifacts/capture.pcap`
- optional `artifacts/report.md`
