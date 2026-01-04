# Laboratory 5 — Subnetting and Address Plan Validation (CLI-only)

## Prerequisites
- Linux VM, CLI access
- Python 3.10+ and pip
- GNU Make

Optional:
- `tcpdump` or `tshark` for capture
- Mininet if the scenario requires it

## Quickstart
From the kit root:
```bash
make setup
make demo
make test
```

## Tasks

### Task 1 — Verify the Week 5 addressing plan
- Confirm the main lab subnet: `10.0.5.0/24`
- Identify the gateway convention: `10.0.5.1`
- Identify three host conventions: `10.0.5.11`, `10.0.5.12` and `10.0.5.13`

### Task 2 — Use the subnet calculator
Run:
```bash
python3 python/apps/subnet_calc.py 10.0.5.0/24
```
Then run a VLSM case, for example:
```bash
python3 python/apps/subnet_calc.py --vlsm 50 25 10 --base 10.0.5.0/24
```

Save evidence:
- copy the key output to `artifacts/validation.txt`

### Task 3 — Optional traffic capture
If the week includes network traffic:
```bash
sudo ./scripts/capture.sh
```
Confirm `artifacts/demo.pcap` exists.

## Deliverable
A short report that includes:
- the final subnet plan
- the commands used
- the outputs saved under `artifacts/`

## Reset
```bash
make clean
```
