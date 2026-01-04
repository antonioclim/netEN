# Computer Networks – Week 1 starter kit
## Network fundamentals: concepts, components and classifications

**Course:** Computer Networks (25.0205IF3.2-0003)  
**Programme:** Economic Informatics, Year 3, Semester 2  
**Institution:** Bucharest University of Economic Studies (ASE), CSIE  
**Kit scope:** Week 1, Linux CLI-only, reproducible demos and checks  
**Version:** 3.1 (standardised)

## What you will learn
- How to inspect network configuration and routes on Linux
- How to validate connectivity and latency (ping, ip, ss)
- How to run simple TCP client–server experiments (netcat, Python)
- How to capture traffic with tcpdump and inspect it with tshark (optional)
- How to produce a minimal, verifiable artefact bundle for assessment

## Environment requirements
A minimal Linux VM is sufficient. Recommended baseline:
- Ubuntu 22.04 LTS or Debian 12, CLI-only
- Python 3.10+ (tested with Python 3.11 and 3.12)
- Docker (optional, for the containerised demo path)

If you plan to run the Mininet topology:
- Mininet installed from system packages
- Root privileges (sudo)

## Quickstart (host, no Docker)
From the kit root (the folder that contains `README.md`):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt

bash scripts/setup.sh --minimal
bash scripts/run_all.sh
bash tests/smoke_test.sh
bash scripts/cleanup.sh
```

Generated outputs are written to `artifacts/`.

## Quickstart (Docker)
From the kit root:

```bash
docker compose -f docker/docker-compose.yml config -q
make docker-demo
make docker-clean
```

Docker writes artefacts to `./artifacts` on the host via a bind mount.

## Verification
After a successful run you should have, at minimum:
- `artifacts/demo.log` (the demo transcript)
- `artifacts/validation.txt` (a short validation summary)
- `artifacts/demo.pcap` (optional, only if capture is enabled)

Run:

```bash
bash tests/smoke_test.sh
```

and confirm it exits with code `0`.

## Student deliverable and success criteria
Submit the following:
- the full kit folder, unchanged in structure and file names
- the `artifacts/` folder produced by `scripts/run_all.sh`

Success criteria:
- `tests/smoke_test.sh` passes without manual intervention
- artefacts are generated in the expected locations
- commands are reproducible on a clean CLI-only VM

## Troubleshooting
1. **`Permission denied` when running scripts**: run `chmod +x scripts/*.sh tests/*.sh`.
2. **Mininet fails or is missing**: run `bash scripts/setup.sh` without `--minimal`, or skip Mininet with `bash scripts/run_all.sh --quick`.
3. **`tcpdump` not found**: install it via your OS package manager, or rerun `scripts/setup.sh`.
4. **`tshark` requires extra permissions**: either run as root in a disposable VM, or disable capture.
5. **Ports already in use**: check with `ss -lntup` and stop the conflicting service, then rerun.
6. **Python import errors**: ensure you activated `.venv` and installed `requirements.txt`.
7. **Docker build fails behind a proxy**: configure Docker proxy settings, then rerun `make docker-demo`.
8. **Artefacts missing**: check `artifacts/demo.log` for the first failing step.

## Reset to zero
To clean generated files and stop any running services:

```bash
bash scripts/cleanup.sh
```

This removes demo artefacts, resets Mininet state (if used) and stops Docker services (if used).
