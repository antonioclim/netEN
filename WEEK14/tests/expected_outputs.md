# Expected Outputs - Week 14

This document contains expected outputs for the demonstrations and tests in the starterkit.

## 1. Environment verification (`make verify`)

### Expected output (success)

```
[INFO] Environment verification for Week 14...

[CHECK] Python 3...
  ✓ Python 3.10.12

[CHECK] Mininet...
  ✓ Mininet 2.3.0

[CHECK] Open vSwitch...
  ✓ OVS 2.17.7

[CHECK] tcpdump...
  ✓ tcpdump 4.99.1

[CHECK] tshark...
  ✓ tshark 3.6.2

[CHECK] Free ports...
  ✓ Port 8080: free
  ✓ Port 9090: free
  ✓ Port 9091: free

[INFO] All checks passed!
```

### Error output (example)

```
[INFO] Environment verification for Week 14...

[CHECK] Python 3...
  ✓ Python 3.10.12

[CHECK] Mininet...
  ✗ Mininet is not installed

[ERROR] Verification failed. Run: sudo bash scripts/setup.sh
```

## 2. Smoke Test (`bash tests/smoke_test.sh`)

### Expected output (success)

```
================================================================================
SMOKE TEST - Starterkit Week 14
================================================================================

[1/4] Checking file structure...
  ✓ README.md
  ✓ Makefile
  ✓ python/apps/backend_server.py
  ✓ python/apps/lb_proxy.py
  ✓ python/apps/http_client.py
  ✓ python/apps/tcp_echo_server.py
  ✓ python/apps/tcp_echo_client.py
  ✓ python/apps/run_demo.py
  ✓ python/exercises/ex_14_01.py
  ✓ python/exercises/ex_14_02.py
  ✓ mininet/topologies/topo_14_recap.py
  ✓ scripts/setup.sh
  ✓ scripts/cleanup.sh

[2/4] Checking Python syntax...
  ✓ backend_server.py
  ✓ lb_proxy.py
  ✓ http_client.py
  ✓ tcp_echo_server.py
  ✓ tcp_echo_client.py
  ✓ run_demo.py
  ✓ ex_14_01.py
  ✓ ex_14_02.py
  ✓ topo_14_recap.py

[3/4] Checking Mininet import...
  ✓ Import mininet.net OK
  ✓ Import mininet.topo OK

[4/4] Checking script permissions...
  ✓ setup.sh executable
  ✓ cleanup.sh executable

================================================================================
RESULT: 24/24 checks passed
STATUS: PASS ✓
================================================================================
```

## 3. Complete demo (`make run-demo`)

### Expected output (stdout)

```
================================================================================
DEMO - Week 14: Review and Integration
================================================================================

[SETUP] Cleaning previous Mininet...
[SETUP] Creating topology...

*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2 h3 h4 
*** Adding switches:
s1 s2 
*** Adding links:
(h1, s1) (h2, s1) (h3, s2) (h4, s2) (s1, s2) 
*** Configuring hosts
h1 h2 h3 h4 
*** Starting controller
*** Starting 2 switches
s1 s2 ...

[INFO] Topology created successfully

[DEMO 1] Connectivity test (ping)...
  h1 -> h2: OK (0.5ms)
  h1 -> h3: OK (1.2ms)
  h1 -> h4: OK (1.5ms)
  Connectivity: 100%

[DEMO 2] Starting backend servers...
  app1 (h2:8001): started
  app2 (h3:8001): started
  Waiting 2s for initialisation...

[DEMO 3] Starting load balancer (h4:8080)...
  Load balancer: started
  Backends configured: h2:8001, h3:8001

[DEMO 4] Starting TCP echo server (h3:9000)...
  Echo server: started

[DEMO 5] Starting packet capture (interface lb-eth0)...
  tcpdump PID: 12345
  Output: artifacts/capture_lb.pcap

[DEMO 6] Generating HTTP traffic...
  Request 1 -> 200 OK (backend: app1) 12ms
  Request 2 -> 200 OK (backend: app2) 15ms
  Request 3 -> 200 OK (backend: app1) 11ms
  Request 4 -> 200 OK (backend: app2) 13ms
  Request 5 -> 200 OK (backend: app1) 14ms
  Request 6 -> 200 OK (backend: app2) 12ms
  Request 7 -> 200 OK (backend: app1) 11ms
  Request 8 -> 200 OK (backend: app2) 16ms
  Request 9 -> 200 OK (backend: app1) 13ms
  Request 10 -> 200 OK (backend: app2) 14ms
  
  Total: 10 requests, 10 successful, 0 errors
  Distribution: app1=5, app2=5

[DEMO 7] TCP echo test...
  Sent: "Hello from client"
  Received: "Hello from client"
  RTT: 2.3ms
  Status: OK

[DEMO 8] Stopping capture and analysis...
  Packets captured: 156
  
[ANALYZE] Traffic summary (tshark):

=== IP Conversations ===
                                               |       <-      | |       ->      | |     Total     |
                                               | Frames  Bytes | | Frames  Bytes | | Frames  Bytes |
10.0.0.1         <-> 10.0.0.10                     38     3.2k       42     4.1k       80     7.3k
10.0.0.10        <-> 10.0.0.2                      19     1.6k       21     2.0k       40     3.6k
10.0.0.10        <-> 10.0.0.3                      18     1.5k       18     1.8k       36     3.3k

=== HTTP Requests ===
GET / HTTP/1.1  (10 requests)
Host: 10.0.0.10:8080

=== SYN Packets ===
10 SYN packets detected (10 connections initiated)

[CLEANUP] Stopping processes...
  app1: stopped
  app2: stopped
  load balancer: stopped
  echo server: stopped
  tcpdump: stopped

[CLEANUP] Cleaning Mininet...

================================================================================
DEMO COMPLETED SUCCESSFULLY
================================================================================

Generated artefacts:
  artifacts/capture_lb.pcap (15KB)
  artifacts/tshark_summary.txt
  artifacts/http_client.log
  artifacts/report.json

For manual analysis:
  tshark -r artifacts/capture_lb.pcap -q -z conv,tcp
  tshark -r artifacts/capture_lb.pcap -Y http
```

### Expected report.json

```json
{
  "timestamp": "2025-01-15T10:30:45",
  "demo_version": "14.0",
  "topology": {
    "hosts": ["h1", "h2", "h3", "h4"],
    "switches": ["s1", "s2"],
    "links": 5
  },
  "connectivity": {
    "h1_to_h2": {"status": "ok", "rtt_ms": 0.5},
    "h1_to_h3": {"status": "ok", "rtt_ms": 1.2},
    "h1_to_h4": {"status": "ok", "rtt_ms": 1.5}
  },
  "http_test": {
    "total_requests": 10,
    "successful": 10,
    "failed": 0,
    "avg_latency_ms": 13.1,
    "distribution": {
      "app1": 5,
      "app2": 5
    }
  },
  "tcp_echo_test": {
    "status": "ok",
    "rtt_ms": 2.3,
    "data_verified": true
  },
  "capture": {
    "file": "artifacts/capture_lb.pcap",
    "packets": 156,
    "duration_seconds": 12.5
  }
}
```

## 4. Review quiz (`python3 python/exercises/ex_14_01.py`)

### Interactive mode output

```
================================================================================
REVIEW QUIZ - COMPUTER NETWORKS
================================================================================

Mode: Interactive (self-test)
Questions: 21 available

Press Enter to begin or 'q' to exit...

--------------------------------------------------------------------------------
Question 1/21:

Which OSI layer is responsible for packet routing?

  A) Data Link Layer
  B) Network Layer
  C) Transport Layer
  D) Physical Layer

Your answer (A/B/C/D): B

✓ CORRECT!

Explanation: The Network Layer (Layer 3) handles logical addressing (IP) and 
routing packets between different networks. Routers operate at this level.

--------------------------------------------------------------------------------
Question 2/21:
...
```

### Quiz generation mode output

```bash
$ python3 python/exercises/ex_14_01.py --generate 10 --output quiz.json
```

```
Quiz generated with 10 questions in: quiz.json

Summary:
  - OSI layers: 2 questions
  - Addressing: 2 questions
  - TCP/UDP: 2 questions
  - Routing: 1 question
  - HTTP: 2 questions
  - Diagnostics: 1 question
```

## 5. Project verification harness (`python3 python/exercises/ex_14_02.py`)

### Output with functional project

```
================================================================================
PROJECT VERIFICATION - NETWORKING
================================================================================

Configuration loaded from: project_config.json
Checks defined: 8

[1/8] Checking ping h1 -> h2...
  Command: ping -c 3 10.0.0.2
  Result: 3/3 packets received
  Status: PASS ✓

[2/8] Checking ping h1 -> h3...
  Command: ping -c 3 10.0.0.3
  Result: 3/3 packets received
  Status: PASS ✓

[3/8] Checking TCP port 8001 on h2...
  Command: nc -zv 10.0.0.2 8001
  Result: Connection succeeded
  Status: PASS ✓

[4/8] Checking TCP port 8001 on h3...
  Command: nc -zv 10.0.0.3 8001
  Result: Connection succeeded
  Status: PASS ✓

[5/8] Checking TCP port 8080 on h4...
  Command: nc -zv 10.0.0.10 8080
  Result: Connection succeeded
  Status: PASS ✓

[6/8] Checking HTTP GET /...
  Command: curl -s http://10.0.0.10:8080/
  Result: HTTP 200, body non-empty
  Status: PASS ✓

[7/8] Checking HTTP GET /health...
  Command: curl -s http://10.0.0.10:8080/health
  Result: HTTP 200, body contains "healthy"
  Status: PASS ✓

[8/8] Checking HTTP GET /lb-status...
  Command: curl -s http://10.0.0.10:8080/lb-status
  Result: HTTP 200, JSON valid
  Status: PASS ✓

================================================================================
VERIFICATION SUMMARY
================================================================================

Total checks: 8
  PASS: 8 ✓
  FAIL: 0 ✗

Score: 100%
Status: PROJECT FUNCTIONAL ✓

Report saved to: verification_report.json
```

### Output with errors

```
[3/8] Checking TCP port 8001 on h2...
  Command: nc -zv 10.0.0.2 8001
  Result: Connection refused
  Status: FAIL ✗
  Suggestion: Check if the backend server is running on h2:8001

[6/8] Checking HTTP GET /...
  Command: curl -s http://10.0.0.10:8080/
  Result: curl: (7) Failed to connect
  Status: FAIL ✗
  Suggestion: Check if the load balancer is running and has backends configured

================================================================================
VERIFICATION SUMMARY
================================================================================

Total checks: 8
  PASS: 5 ✓
  FAIL: 3 ✗

Score: 62.5%
Status: PROJECT REQUIRES CORRECTIONS ✗

Problems identified:
  1. Backend server h2:8001 not responding
  2. Load balancer cannot forward
  3. ...
```

## 6. tcpdump capture (`make capture`)

### Terminal output

```
[INFO] Capturing packets on interface eth0...
[INFO] Duration: 30 seconds (or Ctrl+C to stop)
[INFO] Output: pcap/capture_manual.pcap

tcpdump: listening on eth0, link-type EN10MB (Ethernet), capture size 262144 bytes
^C
45 packets captured
45 packets received by filter
0 packets dropped by kernel

[INFO] Capture saved to: pcap/capture_manual.pcap
[INFO] For analysis: tshark -r pcap/capture_manual.pcap
```

## 7. tshark analysis - Useful commands and output

### TCP conversations

```bash
$ tshark -r artifacts/capture_lb.pcap -q -z conv,tcp
```

```
================================================================================
TCP Conversations
Filter:<No Filter>
                                               |       <-      | |       ->      | |     Total     |    Rel    |   Duration  |
                                               | Frames  Bytes | | Frames  Bytes | | Frames  Bytes |   Start   |             |
10.0.0.1:45678     <-> 10.0.0.10:8080             19     1.6k      21     2.0k      40     3.6k     0.000000         3.2
10.0.0.10:34567    <-> 10.0.0.2:8001               9      800      10      920      19     1.7k     0.001234         1.5
10.0.0.10:34568    <-> 10.0.0.3:8001               9      800       9      880      18     1.6k     0.102345         1.4
================================================================================
```

### HTTP requests

```bash
$ tshark -r artifacts/capture_lb.pcap -Y http.request -T fields -e http.request.method -e http.host -e http.request.uri
```

```
GET	10.0.0.10:8080	/
GET	10.0.0.10:8080	/
GET	10.0.0.10:8080	/health
GET	10.0.0.10:8080	/
GET	10.0.0.10:8080	/
```

### SYN packets only

```bash
$ tshark -r artifacts/capture_lb.pcap -Y "tcp.flags.syn==1 && tcp.flags.ack==0"
```

```
  1   0.000000 10.0.0.1 → 10.0.0.10 TCP 74 45678 → 8080 [SYN]
  5   0.001234 10.0.0.10 → 10.0.0.2 TCP 74 34567 → 8001 [SYN]
 11   0.102345 10.0.0.1 → 10.0.0.10 TCP 74 45679 → 8080 [SYN]
```

---

## Notes

1. **Exact values vary** - Timestamps, RTTs and PIDs will differ with each run
2. **Backend order** - Round-robin, but first request may go to either
3. **Packet sizes** - Depend on payload and TCP options
4. **Possible errors** - If ports are occupied or Mininet is not installed correctly

---
*Revolvix&Hypotheticalandrei*
