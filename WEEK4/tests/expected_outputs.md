# Expected outputs (Week 4)

This starter kit is considered correctly executed when the following artefacts exist after the demo:

- `artifacts/demo.log`  
  A non-empty log produced by `./scripts/run_all.sh`. It should contain sections for TEXT, BINARY and UDP.

- `artifacts/validation.txt`  
  A short validation summary produced by `./scripts/run_all.sh`. It should include at least:
  - `TEXT protocol: OK`
  - `BINARY protocol: OK`
  - `UDP sensor: OK`

- `artifacts/demo.pcap` (optional)  
  If packet capture is permitted on the host, the demo writes a pcap capture file.
  If capture is not permitted or `--quick` is used, the file may be empty but should still exist for predictable checks.

## Ports

Default ports used by the demo:

- TEXT (TCP): 5400  
- BINARY (TCP): 5401  
- UDP sensor (UDP): 5402
