# Mininet Scenario — Week 5 Tasks (IP Addressing)

If Mininet is available on your VM, this scenario helps you practise addressing in a reproducible topology.

## IP plan
- Main subnet: `10.0.5.0/24`
- Gateway or router: `10.0.5.1`
- Typical hosts: `10.0.5.11`, `10.0.5.12`, `10.0.5.13`
- Application server (if used): `10.0.5.100`

## Tasks
1. Start the topology using the provided script under `mininet/`
2. Assign IPs consistently with the plan above
3. Verify connectivity using `ping` and `ip a`
4. Record routing state with `ip r`
5. Optionally capture traffic to `artifacts/demo.pcap`

## Evidence
Store your outputs under `artifacts/` and ensure `tests/smoke_test.sh` passes afterwards.
