# Week 6 Starter Kit – Computer Networks

## NAT/PAT, ARP, DHCP, NDP, ICMP and SDN (Software-Defined Networking)

This kit is designed for a minimal Linux VM used in CLI-only mode. It provides a reproducible workflow for running a small Mininet topology, capturing traffic when needed and validating outputs via a non-interactive smoke test.

### Quickstart

```bash
cd WEEK6
make setup
make demo
make test
make clean
```

If you want the containerised run (Docker installed):

```bash
cd WEEK6
make docker-demo
make docker-clean
```

### Verification

After `make demo`, you should obtain:

- `artifacts/demo.log`
- `artifacts/validation.txt`
- optionally `artifacts/demo.pcap` (only when capture is enabled by the demo script)

Then run:

```bash
./tests/smoke_test.sh
```

The smoke test checks artefact presence and a small set of key strings. See `tests/expected_outputs.md` for what is verified.

### Reset to zero

```bash
./scripts/cleanup.sh
```

This resets Mininet state (`mn -c`), removes temporary artefacts and, if Docker was used, stops and removes containers.

### Student deliverable and success criteria

Deliver:

- `artifacts/demo.log`
- `artifacts/validation.txt`
- answers to the tasks in `docs/lab.md` (commands used, observations and short explanations)

Success criteria:

- The demo runs without interactive prompts
- The smoke test passes
- Your explanation links observed packets and logs to the relevant protocol behaviour (NAT, ARP, DHCP, ICMP and SDN control)

### Troubleshooting

1. **Mininet not found**: install it (`sudo apt-get install -y mininet`) and rerun `make setup`.
2. **Open vSwitch missing**: install `openvswitch-switch` then rerun `make setup`.
3. **Permission denied on scripts**: run `chmod +x scripts/*.sh tests/*.sh`.
4. **Ports in use**: stop conflicting services or update only the environment variables used by the demo.
5. **No `demo.pcap` produced**: capture is optional, check the demo script flags and whether `tcpdump` is installed.
6. **Smoke test fails on strings**: open `artifacts/demo.log` and `tests/expected_outputs.md`, confirm the demo completed and logs were written.
7. **Docker compose not available**: install Docker Compose v2 (`docker compose version`) or use the host-run path.
8. **Leftover Mininet state**: run `sudo mn -c`, then rerun `make demo`.

## Repository structure

Canonical top-level folders (kept consistent across weeks):

- `docs/` lab notes and checklists
- `scripts/` setup, demo and cleanup scripts
- `python/` Python utilities used by the demos
- `mininet/` Mininet topologies for this week
- `tests/` non-interactive smoke tests
- `docker/` containerised demo (optional path)
- `artifacts/` generated outputs only
- `configs/` small configuration files
- `legacy/` compatibility materials kept without breaking paths
- `generate_docx/` placeholder for future document generation

