# Mininet Scenarios – Week 9 (Session, Presentation and File Protocols)

This document provides practical Mininet scenarios for Week 9, including clear objectives, exact commands, expected results and short reflection questions.

Do not translate protocol tokens, CLI flags and expected output markers such as TCP, UDP, FTP, CRC, RTT, INFO, OK and ERROR.

## Assumptions

- Subnet plan: `10.0.9.0/24`
- Gateway (if used): `10.0.9.1`
- Hosts: `10.0.9.11`, `10.0.9.12`, `10.0.9.13`
- Server: `10.0.9.100`
- Default ports:
  - TCP application: `9090`
  - UDP application: `9091`
  - HTTP (if used): `8080`
  - Proxy (if used): `8888`

## Scenario 1: Baseline file transfer over a simple topology

### Objective
Run the Week 9 pseudo-FTP demo, transfer a file and confirm integrity.

### Steps
1. Start the topology:
   ```bash
   sudo python3 mininet/topologies/topo_base.py
   ```
2. In the Mininet CLI, verify addressing:
   ```bash
   mininet> h1 ip a
   mininet> h2 ip a
   ```
3. Run the server on `h1` and the client on `h2` (see `scripts/run_demo.sh` for the exact command set):
   ```bash
   mininet> h1 bash -lc "python3 -m python.server.pseudo_ftp_server --host 10.0.9.100 --port 9090"
   mininet> h2 bash -lc "python3 -m python.client.pseudo_ftp_client --host 10.0.9.100 --port 9090 --user test --password test --get sample.bin --out /tmp/sample.bin"
   ```
4. Check integrity:
   ```bash
   mininet> h2 sha256sum /tmp/sample.bin
   ```

### Expected results
- The client prints a final status line containing `[OK]`.
- The downloaded file hash matches the expected value recorded by the server or by `tests/expected_outputs.md`.

### Reflection
1. Which layer is responsible for data integrity checks in this demo?
2. What would happen if the server was not running?

## Scenario 2: Latency impact on transfer duration

### Objective
Observe how added delay changes RTT and end-to-end transfer time.

### Steps
1. Start the latency topology:
   ```bash
   sudo python3 mininet/topologies/topo_extended.py --delay 100ms
   ```
2. Measure RTT:
   ```bash
   mininet> h2 ping -c 5 10.0.9.100
   ```
3. Repeat the same file transfer as in Scenario 1.
4. Repeat with a different delay:
   ```bash
   sudo python3 mininet/topologies/topo_extended.py --delay 10ms
   sudo python3 mininet/topologies/topo_extended.py --delay 500ms
   ```

### Expected results
- RTT grows approximately with the configured delay.
- Transfer time increases and the increase may be non-linear due to protocol behaviour.

### Reflection
1. Why can transfer time grow non-linearly with delay?
2. What role does the TCP window play in this behaviour?

## Scenario 3: Two clients, one server

### Objective
Run two clients concurrently and observe server behaviour under parallel transfers.

### Steps
1. Start the extended topology:
   ```bash
   sudo python3 mininet/topologies/topo_extended.py
   ```
2. Start the server on `h1`.
3. Start clients from `h2` and `h3` in parallel:
   ```bash
   mininet> h2 bash -lc "python3 -m python.client.pseudo_ftp_client --host 10.0.9.100 --port 9090 --user test --password test --get sample.bin --out /tmp/h2.bin" &
   mininet> h3 bash -lc "python3 -m python.client.pseudo_ftp_client --host 10.0.9.100 --port 9090 --user test --password test --get sample.bin --out /tmp/h3.bin" &
   mininet> wait
   ```

### Expected results
- Both clients complete with `[OK]`.
- Server logs show two sessions.
- Hashes for `/tmp/h2.bin` and `/tmp/h3.bin` match.

### Reflection
1. Which client finishes first and why?
2. Which parts of the protocol are sensitive to concurrent sessions?

## Notes

- Use `scripts/capture_traffic.sh` if you need a `.pcap` for analysis.
- Use `scripts/cleanup.sh` to reset Mininet state (`mn -c`) and remove temporary artefacts.
