# Week 4 seminar guide: Building reliable messages over TCP and UDP

## Why this week matters

TCP provides reliable delivery but it does not preserve message boundaries.
Your application must decide how to separate a continuous byte stream into messages.
UDP preserves datagram boundaries but can drop, reorder or duplicate messages.
This week shows minimal patterns that are easy to test and reason about.

## Core concepts

### Framing for TCP

A common choice is a **length-prefixed** frame:

- 4-byte length (network byte order)
- payload bytes

This allows the receiver to:

1. read exactly the header
2. determine how many bytes belong to the payload
3. reassemble a full message even if `recv()` returns partial data

### Integrity checking

A checksum such as **CRC32** can detect accidental corruption.
CRC32 is not a cryptographic integrity guarantee but it is sufficient for many teaching scenarios.

### Binary encoding

Binary messages reduce overhead and support fixed-width fields.
Python `struct` gives explicit control over:

- endianness
- integer sizes
- packing layout

## What the demo does

`./scripts/run_all.sh` starts:

- a TEXT TCP server and a client sequence on port 5400
- a BINARY TCP server and a client sequence on port 5401
- a UDP sensor server and a client sequence on port 5402/udp

It writes:

- `artifacts/demo.log`
- `artifacts/validation.txt`
- `artifacts/demo.pcap` (optional, depends on capture permissions)

## Common failure modes and fixes

- **Port already in use**: stop old servers, run `./scripts/cleanup.sh`
- **Capture fails**: run `--quick` or skip capture, it is optional
- **Client cannot connect**: verify server started and ports match
- **Binary decode errors**: confirm both ends use the same `struct` format
- **Flaky output**: remove timestamps from test markers and keep deterministic messages

## Student success criteria

You succeed when:

- `./tests/smoke_test.sh` exits with code 0
- `artifacts/validation.txt` contains `TEXT protocol: OK`, `BINARY protocol: OK` and `UDP sensor: OK`
