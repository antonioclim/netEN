# Expected Outputs for WEEK9

## Smoke Test Expected Outputs

### Python Code Tests
```
ex_9_01_endianness.py --selftest → "All tests passed"
Import ex_9_02_pseudo_ftp → No errors
net_utils.py selftest → "All tests passed"
```

### Artefacts After run_all.sh
- `artifacts/demo.log` — Must exist and contain timestamps
- `artifacts/demo.pcap` — Must exist (packet capture from demo)
- `artifacts/validation.txt` — Must contain "PASS"

### Structure Verification
- `scripts/` directory exists
- `python/exercises/` directory exists  
- `python/utils/` directory exists
- `mininet/topologies/` directory exists
- `tests/` directory exists
- `docs/` directory exists

## tshark Recommended Filters

### FTP Traffic Analysis
```bash
tshark -r artifacts/demo.pcap -Y "ftp"
tshark -r artifacts/demo.pcap -Y "ftp.request.command"
tshark -r artifacts/demo.pcap -Y "tcp.port == 9021 || tcp.port == 9020"
```

### Session Management
```bash
# View all TCP streams
tshark -r artifacts/demo.pcap -z conv,tcp

# Follow specific stream
tshark -r artifacts/demo.pcap -z follow,tcp,ascii,0
```

### Endianness Verification
```bash
# Examine raw bytes in packets
tshark -r artifacts/demo.pcap -T fields -e data.data
```

## Success Criteria

**Minimum Requirements:**
1. All Python scripts execute without syntax errors
2. `smoke_test.sh` passes all checks (exit code 0)
3. Demo generates all expected artefacts
4. Packet capture contains FTP control and data channels
5. Endianness exercise demonstrates byte order conversion

**Full Points:**
- Completion of 2+ exercises from lab tasks
- Correct implementation of FTP state machine
- Proper handling of binary data encoding
- Clean packet capture analysis in documentation
