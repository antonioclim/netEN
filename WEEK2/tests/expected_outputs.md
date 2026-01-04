# Expected Outputs - Week 2: Socket Programming

## Generated artefacts

After running `scripts/run_all.sh`, the following files must exist in `artifacts/`:

### 1) demo.log

- **Path:** `artifacts/demo.log`
- **Type:** Text log
- **Minimum content:** 20+ lines

**Expected structure (illustrative):**
```
[YYYY-MM-DD HH:MM:SS][INFO] ==========================================
[YYYY-MM-DD HH:MM:SS][INFO] WEEK 2 - Automated demo: Socket Programming
...
result: VALIDATION OK
==========================================
```

**Success indicators:**
- Contains `result: VALIDATION OK`
- Contains multiple lines with `[OK]`
- Contains no `[FAIL]`

### 2) validation.txt

- **Path:** `artifacts/validation.txt`
- **Type:** Text
- **Minimum content:** 5+ lines

**Success indicators:**
- A final line stating `result: VALIDATION OK`

### 3) Optional captures

If `tcpdump` is available on the host, the demo may also produce capture files:

- `artifacts/tcp_demo.pcap`
- `artifacts/udp_demo.pcap`
- `artifacts/demo.pcap` (combined, if enabled)

The smoke test does not fail if captures are missing and `tcpdump` is not installed.

## Secondary logs

Some steps also write extra logs under `logs/` when the full interactive workflow is used. These are not required by the smoke test.

## Notes

- Do not treat timestamps as stable test values.
- Port numbers must match the kit configuration: TCP 9090 and UDP 9091.
- Mininet scenarios use the Week 2 address plan where applicable.
