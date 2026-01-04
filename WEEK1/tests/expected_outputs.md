# Expected outputs (Week 1)

This file describes what `scripts/run_all.sh` and `tests/smoke_test.sh` expect.

## Required artefacts
- `artifacts/demo.log` contains the demo transcript and must include the line:
  - `[run_all] Starting Week 1 demo`
- `artifacts/validation.txt` is a short summary and must contain:
  - `Week: 1`

## Optional artefacts
- `artifacts/demo.pcap` is created only if capture is enabled and `tcpdump` is available.

## Typical successful commands
```bash
bash scripts/run_all.sh
bash tests/smoke_test.sh
```
