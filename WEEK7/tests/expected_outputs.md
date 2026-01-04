# Expected outputs (Week 7)

This file contains indicative outputs and verification checks. Exact values may differ, but the structure and the key markers should match.

## 1) Demo artefacts
After `./scripts/run_all.sh` you should have:

- `artifacts/demo.log`
- `artifacts/validation.txt` containing at least:
  - `BASELINE_OK`
  - `BLOCK_TCP_OK`
  - `BLOCK_UDP_OK`
- `artifacts/demo.pcap` (if tcpdump is installed)

## 2) Validation example
Example lines (your timestamps will differ):

```text
BASELINE_OK: tcp_echo=ok udp_echo=ok
BLOCK_TCP_OK: tcp_echo=blocked udp_echo=ok
BLOCK_UDP_OK: tcp_echo=ok udp_echo=blocked
```

## 3) tshark filters to validate behaviour
TCP echo traffic:

```bash
tshark -r artifacts/demo.pcap -Y "tcp.port==9090"
```

UDP echo traffic:

```bash
tshark -r artifacts/demo.pcap -Y "udp.port==9091"
```

Look for rejected TCP connections (RST or ICMP unreachable may appear depending on rules):

```bash
tshark -r artifacts/demo.pcap -Y "tcp.flags.reset==1"
```

## 4) Criteria of success
- You can reproduce the baseline, the TCP block and the UDP block without editing files.
- You can explain, using packet evidence, why a client succeeded or failed.
- Your new profile changes exactly one aspect of the policy and you can justify it.
