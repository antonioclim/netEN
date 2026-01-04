# Expected Outputs - Week 12: Email and RPC

## 1. Main artefacts

After running `./scripts/run_all.sh`, the kit must produce:

- `artifacts/demo.log` (required)
- `artifacts/validation.txt` (required)
- `artifacts/demo.pcap` (optional, only if traffic capture is available and permitted)

## 2. `artifacts/demo.log` minimal markers

The `artifacts/demo.log` file must contain, at minimum:

- `WEEK 12: AUTOMATIC EMAIL & RPC DEMO`
- `Project root:`

## 3. `artifacts/validation.txt` minimal markers

The `artifacts/validation.txt` file should state whether the demo completed, plus a short summary of checks performed.

## 4. Smoke test expectations

`./tests/smoke_test.sh` must pass when the artefacts are present and contain the minimal markers above.
