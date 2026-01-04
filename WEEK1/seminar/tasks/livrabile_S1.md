# Week 1 student deliverables

Submit a single archive that contains:
- the full Week 1 kit folder (structure unchanged)
- the `artifacts/` folder produced by the demo

## Minimum required artefacts
- `artifacts/demo.log`
- `artifacts/validation.txt`

Optional:
- `artifacts/demo.pcap` if you enabled capture

## How to validate before submission
Run:

```bash
bash scripts/run_all.sh
bash tests/smoke_test.sh
```

Your submission is accepted if `tests/smoke_test.sh` exits with code `0`.
