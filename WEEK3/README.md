# Starter Kit — Week 3: UDP broadcast and multicast, TCP tunnelling

## Overview
This kit supports Week 3 of the Networks of Computers course (Year 3, Semester 2). It focuses on practical socket programming with UDP broadcast, UDP multicast and a simple TCP tunnel used as a forwarding bridge between subnets.

**Primary learning outcomes**
- Explain when UDP and TCP are appropriate and what trade-offs follow
- Implement UDP broadcast and multicast senders and receivers in Python
- Implement a simple TCP tunnel (port forwarding) and observe traffic on the wire
- Capture and inspect packets using tcpdump or tshark

## IP and port plan
- **Mininet subnet (Week 3):** `10.0.3.0/24` (router/gateway: `10.0.3.1`)
- **Example ports used by the demos:** `5300–5399` (derived from the Week number)

Do not change these values unless you update every reference in scripts, docs and tests.

## Quickstart (host run)
Run on a Linux VM with Python 3.10+.

```bash
cd WEEK3

make setup
make verify

# Full non-interactive demo (writes logs into ./artifacts)
sudo ./scripts/run_all.sh

# Validate the produced artefacts
./tests/smoke_test.sh

# Reset to a clean state
sudo ./scripts/cleanup.sh
```

## Docker quickstart (optional)
If Docker is available, you can run a contained demo. The container writes artefacts to `./artifacts` on the host.

```bash
cd WEEK3
make docker-demo
make docker-clean
```

## Verification
After `scripts/run_all.sh`, you should have at least:
- `artifacts/demo.log`
- `artifacts/validation.txt`
- optionally `artifacts/demo.pcap` (if capture is enabled)

The smoke test checks that Python sources compile, CLI help works and the expected artefacts exist.

## Troubleshooting
1. **Permission denied** when running capture or Mininet: use `sudo` and confirm your user is in the required groups.
2. **Mininet not installed:** run `make setup` or install `mininet` from your distribution repositories.
3. **tcpdump not found:** install `tcpdump` or use `tshark` if available.
4. **tshark permission issues:** run as `sudo` or configure capture capabilities as per your distro guidance.
5. **Port already in use:** stop the process or change the port consistently in scripts, docs and tests.
6. **Multicast not received:** confirm the correct multicast group, TTL and interface binding, then check firewall rules.
7. **Docker compose fails:** run `docker compose config -q` to validate YAML and check Docker daemon status.
8. **Nothing in the pcap:** ensure capture is started before traffic, then confirm the capture filter matches the demo port.

## Student deliverable and success criteria
Deliver a short report containing:
- commands executed and key outputs
- a brief explanation of broadcast vs multicast behaviour in your tests
- a screenshot or excerpt from `tshark` showing UDP and TCP traffic
- confirmation that `tests/smoke_test.sh` completed with exit code `0`
