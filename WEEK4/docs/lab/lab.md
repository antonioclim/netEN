# Week 4 lab notes: Physical layer, data link and custom protocols

This week focuses on building small, testable protocol components on top of TCP and UDP.
You will work with message framing, checksums (CRC32), binary packing and simple request–response patterns.

## Learning outcomes

By the end of this lab you should be able to:

- explain why TCP is a byte stream and why framing is required
- implement a length-prefixed frame format
- compute and validate CRC32 for integrity checking
- encode and decode binary messages using `struct`
- test a client and server pair locally using loopback
- capture traffic (when permitted) and inspect it with `tcpdump` or `tshark`

## What you run in this kit

- TEXT protocol over TCP on port **5400**
- BINARY protocol over TCP on port **5401**
- UDP sensor messages on port **5402/udp**

All demos are non-interactive and write artefacts to `artifacts/`.

## Suggested flow

1. Create a local Python environment  
   `./scripts/setup.sh`

2. Run the automated demo  
   `./scripts/run_all.sh`

3. Verify outputs  
   `./tests/smoke_test.sh`

4. Reset to a clean state  
   `./scripts/cleanup.sh`

## Exercises (mapped to the kit)

- Implement a new TEXT command on the server (for example `TIME` or `ECHO`)
- Extend the binary message format with a new field and update both client and server
- Add a simple UDP message acknowledgement pattern
- Make outputs deterministic where tests depend on them (avoid timestamps in test markers)

## Student deliverable

Submit:

- `artifacts/demo.log`
- `artifacts/validation.txt`
- short notes (5–10 lines) describing what you changed and how you verified it
