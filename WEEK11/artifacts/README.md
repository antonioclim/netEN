# Artifacts directory

This directory is used by the automation and capture targets to store generated outputs.

Typical files created during a run:

- `demo.log` — plain-text execution log produced by `make run-all`
- `validation.txt` — a short, machine-readable summary of the run
- `demo.pcap` — packet capture produced by `make run-all` when capture permissions allow

For ad-hoc captures created with `make capture` or `make capture-traffic`, see the `pcap/` directory.
