# Expected Outputs — Week 5

This file documents the minimal artefacts produced by `make demo` and validated by `make test`.

## Required artefacts
- `artifacts/demo.log`
- `artifacts/validation.txt`

Optional (only if capture is enabled and tools are present):
- `artifacts/demo.pcap`

## Minimal content checks
`artifacts/demo.log` must contain:
- `Week 5: IP Addressing`
- `Network base: 10.0.5.0/24`

`artifacts/validation.txt` must contain:
- `OK:` at least once
- `10.0.5.0/24` at least once
