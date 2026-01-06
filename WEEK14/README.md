# Computer Networks — Week 14
## Integrated recap: Mininet, TCP and HTTP services, load balancing and packet capture

This starter kit provides a small end-to-end networking scenario that you can run locally on Ubuntu 24.04 (or a compatible Debian-based system). It is designed as a final-week recap that connects concepts from across the semester:

- network namespaces and virtual topologies (Mininet + Open vSwitch)
- TCP services (a simple echo server and client)
- HTTP services (two backend servers)
- a basic reverse proxy acting as a load balancer
- packet capture with `tcpdump` and analysis with `tshark`
- validation and artefact generation for reproducible submissions

The kit is headless-friendly (works over SSH). It does **not** require an external OpenFlow controller.

---

## 0. What you should already have

- Ubuntu 24.04 (recommended), or a compatible Debian-based distribution
- a user with `sudo` rights
- Internet access for `apt` installation

---

## 1. Quick start

### 1.1 Clone (the same sparse checkout workflow used in the course)

```bash
cd ~
git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK14
cd WEEK14
git sparse-checkout set WEEK14

shopt -s dotglob
mv WEEK14/* .
rmdir WEEK14

find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

### 1.2 Setup and verification

```bash
make setup
make verify
```

Expected outcome:
- setup installs Mininet, Open vSwitch, tcpdump, tshark, curl and ApacheBench
- verification reports all required commands as available
- the smoke test passes

If the smoke test fails, open `tests/smoke_test.sh` and follow the printed hints.

---

## 2. Topology, addressing and services

### 2.1 Topology
The recap topology is intentionally small:

```
cli ─── s1 ─── s2 ─── app1
         │       └─── app2
         └─── lb
```

### 2.2 Switch mode (important)
`s1` and `s2` are Open vSwitch switches in `failMode=standalone`:

- they behave as L2 learning switches
- they forward frames without an external controller
- they avoid the common Mininet error `Cannot find required executable controller`

### 2.3 Fixed IP addressing
All hosts are placed in `10.0.14.0/24`:

| Node | Role | IP address |
|------|------|------------|
| `lb` | load balancer / reverse proxy | `10.0.14.1` |
| `cli` | client / traffic generator | `10.0.14.11` |
| `app1` | backend A (HTTP) | `10.0.14.100` |
| `app2` | backend B (HTTP + TCP echo) | `10.0.14.101` |

Why fixed IPs:
- your captures are easier to interpret
- your logs are comparable across runs
- grading and debugging are simpler

### 2.4 Ports and processes
During the integrated demo the following services are expected:

| Service | Host | Listen address | Port | Script |
|---------|------|----------------|------|--------|
| HTTP backend A | `app1` | `10.0.14.100` | 8080 | `python/apps/backend_server.py` |
| HTTP backend B | `app2` | `10.0.14.101` | 8080 | `python/apps/backend_server.py` |
| Reverse proxy / load balancer | `lb` | `10.0.14.1` | 8080 | `python/apps/lb_proxy.py` |
| TCP echo server | `app2` | `10.0.14.101` | 9000 | `python/apps/tcp_echo_server.py` |
| HTTP client (traffic generator) | `cli` | connects to `lb` | - | `python/apps/http_client.py` |
| TCP echo client | `cli` | connects to `app2` | - | `python/apps/tcp_echo_client.py` |

---

## 3. Make targets

From the kit root:

```bash
make help
```

Key targets:
- `make setup` installs system dependencies
- `make verify` checks the environment and runs smoke tests
- `make smoke-test` runs smoke tests only
- `sudo make run-demo` runs the full integrated demo and generates `artifacts/`
- `sudo make run-all` is an alias for `run-demo`
- `sudo make run-lab` starts the interactive Mininet CLI for manual exploration
- `sudo make capture` starts a standalone capture run (manual capture helper)
- `sudo make clean` stops Mininet and terminates demo processes
- `make reset` also removes the `artifacts/` directory

---

## 4. Demo 0: minimal topology smoke test

This is the fastest test if you only want to confirm Mininet and basic connectivity.

```bash
sudo python3 mininet/topologies/topo_14_recap.py --test
```

Expected output (short):
- `pingAll` completes with **0% dropped**
- a temporary HTTP server on `app1:8080` returns **HTTP 200** when queried from `cli`

If this fails, do not proceed to the larger demos. Fix the environment first.

---

## 5. Demo 1: automated integrated demo (recommended)

### 5.1 Run

```bash
sudo make run-demo
# or
sudo make run-all
```

### 5.2 What it does
The orchestrator (`python/apps/run_demo.py`) executes the following steps:

1. cleans previous Mininet artefacts
2. starts the Week 14 topology
3. runs `pingAll`
4. starts `app1` and `app2` backend HTTP servers
5. starts the load balancer on `lb:8080` (round robin)
6. generates HTTP requests from `cli` to `lb:8080`
7. runs a TCP echo test between `cli` and `app2:9000`
8. captures traffic on `lb-eth0` into `artifacts/demo.pcap`
9. runs a basic `tshark` summary
10. writes validation and a JSON report

### 5.3 Expected terminal output (short)
You should see a sequence of stages similar to:

```text
=== Week 14: Integrated Demo ===
[INFO] Starting Mininet topology...
[OK] pingAll: PASS
[INFO] Starting backends and load balancer...
[OK] HTTP requests completed: 30/30
[OK] TCP echo completed: PASS
[INFO] Capture saved to artifacts/demo.pcap
[INFO] Writing report.json and validation.txt
[OK] Demo completed successfully
```

Timestamps, exact wording and minor formatting can differ.

### 5.4 Expected artefacts
After a successful run:

```text
artifacts/
  demo.log
  demo.pcap
  report.json
  tshark_summary.txt
  validation.txt
  app1.log
  app2.log
  lb.log
  http_client.log
```

Check the validation report:

```bash
cat artifacts/validation.txt
```

Expected outcome:
- most fields are `PASS`
- if one field is `FAIL`, use `artifacts/demo.log` and the per-process logs to locate the cause

### 5.5 Expected log snippets (what “good” looks like)

Backend logs (`artifacts/app1.log`, `artifacts/app2.log`) should contain lines like:
- `HTTP server started on http://10.0.14.100:8080/`
- `GET / HTTP/1.1`
- `→ 200 OK ...`

Proxy log (`artifacts/lb.log`) should contain lines like:
- `Load balancer listening on 10.0.14.1:8080`
- `Backend selected: 10.0.14.100:8080` (or `10.0.14.101:8080`)

Client request log (`artifacts/http_client.log`) should contain lines like:
- `req=000 status=200 backend=10.0.14.100:8080 latency_ms=...`
- `req=001 status=200 backend=10.0.14.101:8080 latency_ms=...`

---

## 6. Demo 2: reverse proxy round robin (interactive observation)

This demo is about understanding what you should observe and how it maps to the architecture.

### 6.1 Start the lab topology
```bash
sudo make run-lab
```

You will enter the Mininet prompt:

```text
mininet>
```

### 6.2 Start the two backends
In the Mininet prompt:

```text
mininet> app1 python3 python/apps/backend_server.py --id app1 --host 10.0.14.100 --port 8080 &
mininet> app2 python3 python/apps/backend_server.py --id app2 --host 10.0.14.101 --port 8080 &
```

Expected output (short):
- each backend prints that it is listening on its IP and port

### 6.3 Start the reverse proxy load balancer
```text
mininet> lb python3 python/apps/lb_proxy.py --listen-host 10.0.14.1 --listen-port 8080 \
            --backends 10.0.14.100:8080 10.0.14.101:8080 --algorithm roundrobin &
```

Expected output (short):
- `Load balancer listening on 10.0.14.1:8080`
- `Algorithm: roundrobin`

### 6.4 Send requests from the client and observe alternation

Single request with header inspection:
```text
mininet> cli curl -s -D - http://10.0.14.1:8080/ -o /dev/null | grep -i x-backend
```

Short loop:
```text
mininet> cli sh -c 'for i in $(seq 1 6); do curl -s -D - http://10.0.14.1:8080/ -o /dev/null | grep -i x-backend; done'
```

Expected output:
- `X-Backend: 10.0.14.100:8080`
- `X-Backend: 10.0.14.101:8080`
- alternating A, B, A, B…

### 6.5 What you should observe

1. **Backend alternation**  
   The `X-Backend` response header is injected by the proxy and reflects the chosen backend for that request.

2. **Two distinct TCP connections**  
   - client → proxy: `cli` connects to `lb:8080`
   - proxy → backend: `lb` connects to `app1:8080` or `app2:8080`

3. **Forwarded client identity**  
   The proxy adds an `X-Forwarded-For` header with the client IP.

### 6.6 Stop services
```text
mininet> app1 pkill -f backend_server.py
mininet> app2 pkill -f backend_server.py
mininet> lb pkill -f lb_proxy.py
mininet> exit
```

---

## 7. Demo 2 with multiple terminals (headless friendly)

If you want to *see activity* as if you had four separate consoles, you can redirect each service output to a file and tail it from separate SSH sessions.

### Terminal 1 (Mininet)
Start the lab:
```bash
sudo make run-lab
```

In the Mininet prompt, start services with log redirection:

```text
mininet> app1 sh -c 'python3 python/apps/backend_server.py --id app1 --host 10.0.14.100 --port 8080 > /tmp/app1.log 2>&1 &' 
mininet> app2 sh -c 'python3 python/apps/backend_server.py --id app2 --host 10.0.14.101 --port 8080 > /tmp/app2.log 2>&1 &' 
mininet> lb  sh -c 'python3 python/apps/lb_proxy.py --listen-host 10.0.14.1 --listen-port 8080 --backends 10.0.14.100:8080 10.0.14.101:8080 --algorithm roundrobin > /tmp/lb.log 2>&1 &' 
```

Generate requests:
```text
mininet> cli sh -c 'for i in $(seq 1 10); do curl -s http://10.0.14.1:8080/ >/dev/null; done'
```

### Terminal 2 (host shell)
```bash
sudo tail -f /tmp/app1.log
```

Expected output:
- `GET / HTTP/1.1`
- `→ 200 OK ...`

### Terminal 3 (host shell)
```bash
sudo tail -f /tmp/app2.log
```

Expected output:
- similar to Terminal 2, for `app2`

### Terminal 4 (host shell)
```bash
sudo tail -f /tmp/lb.log
```

Expected output:
- repeated `Backend selected: ...` lines
- alternating backend selection

This method works without X11 and without `xterm`.

---

## 8. Demo 3: manual capture and analysis (interactive)

This demo focuses on validation using PCAP.

### 8.1 Capture from the load balancer interface
Start the topology (`sudo make run-lab`), start backends and the proxy (Demo 2) and then:

```text
mininet> lb tcpdump -ni lb-eth0 -w /tmp/manual_demo.pcap &
```

Generate a few requests (Demo 2) and then stop tcpdump:

```text
mininet> lb pkill -INT tcpdump
```

### 8.2 Analyse with tshark
Still inside Mininet:

```text
mininet> lb tshark -r /tmp/manual_demo.pcap -q -z conv,tcp
mininet> lb tshark -r /tmp/manual_demo.pcap -Y http.request -T fields -e ip.src -e ip.dst -e http.host -e http.request.uri | head
```

Expected outcome:
- TCP conversations exist for `cli↔lb` and `lb↔app1/app2`
- HTTP requests are visible

Copy the capture out:
```bash
sudo cp /tmp/manual_demo.pcap artifacts/manual_demo.pcap
sudo chown $USER:$USER artifacts/manual_demo.pcap
```

---

## 9. Protocol-level view: what happens on the wire

When you request `http://10.0.14.1:8080/` from `cli`, the following happens:

1. `cli` establishes a TCP connection to `lb:8080` (three-way handshake).
2. `cli` sends an HTTP request to the proxy.
3. `lb` selects a backend using round robin.
4. `lb` establishes a second TCP connection to the chosen backend.
5. `lb` forwards the HTTP request and receives the backend response.
6. `lb` returns the response to `cli` and adds helpful headers:
   - `X-Backend: <selected backend>`
   - `X-Forwarded-For: <client ip>`

In a PCAP captured on `lb-eth0` you should therefore be able to find:
- two separate TCP conversations
- one HTTP request stream from `cli` to `lb`
- one HTTP request stream from `lb` to the chosen backend

Useful filters:
- `ip.addr == 10.0.14.1`
- `tcp.port == 8080`
- `http.request`
- `http.response`

---

## 10. Troubleshooting

### 10.1 “Cannot find required executable controller”
If you see:

```text
c0 Cannot find required executable controller.
```

you are running a topology that tries to start the legacy Mininet `Controller` process.
This kit uses Open vSwitch in `failMode=standalone` and **does not** start a controller.

Fix:
- ensure you are using the updated file `mininet/topologies/topo_14_recap.py`
- run `sudo make clean`
- re-run `sudo make run-demo`

### 10.2 Open vSwitch is not active
If verification reports Open vSwitch is inactive:

```bash
sudo systemctl start openvswitch-switch
sudo systemctl enable openvswitch-switch
```

### 10.3 PCAP is empty or missing
- ensure you ran the demo with `sudo`
- ensure `tcpdump` is installed (`make setup`)
- check `artifacts/demo.log` for messages about starting tcpdump

### 10.4 “Port 8080 is in use”
`make verify` reports ports in the host namespace only. Mininet hosts use separate network namespaces so host port usage usually does not block Mininet services.

### 10.5 Cleanup and reset
If you suspect stale state:

```bash
sudo make clean
make reset
```

---

## 11. Where to look next

- `docs/lab.md` contains a longer lab walkthrough
- `mininet/scenarios/scenario_14_tasks.md` contains scenario-style tasks for practice
- `tests/expected_outputs.md` contains short “what good looks like” snippets

---

## Licence
Educational material for the course. See `LICENSE` if included in your distribution.


---

## 12. Self-check checklist (before submission)

Use this list to validate that you are on the correct track:

### Environment
- `make verify` reports no missing required tools
- `openvswitch-switch` is active

### Automated demo
- `sudo make run-demo` completes without errors
- `artifacts/validation.txt` contains `PASS` for:
  - `ping_all`
  - `http_test`
  - `tcp_echo_test`
  - `pcap_generated`
- `artifacts/demo.pcap` is non-empty

### Manual reasoning
- you can explain why there are **two** TCP connections per HTTP request (client→proxy and proxy→backend)
- you can locate at least one HTTP request in the capture using `tshark -Y http.request`
- you can identify backend alternation using the `X-Backend` header

---

## 13. Appendix: useful analysis commands

All examples assume that you ran `sudo make run-demo` and generated `artifacts/demo.pcap`.

### 13.1 Quick capture metadata
```bash
capinfos artifacts/demo.pcap 2>/dev/null || true
```

Expected outcome:
- file size is greater than zero
- capture has packets and a valid start time

### 13.2 Conversations (who talked to whom)
```bash
tshark -r artifacts/demo.pcap -q -z conv,ip | head -80
```

Expected outcome:
- a conversation involving `10.0.14.11` and `10.0.14.1`
- one or more conversations involving `10.0.14.1` and `10.0.14.100` or `10.0.14.101`

### 13.3 HTTP requests summary
```bash
tshark -r artifacts/demo.pcap -Y http.request -T fields -e frame.number -e ip.src -e ip.dst -e http.host -e http.request.uri | head -20
```

Expected outcome:
- rows with `ip.src=10.0.14.11` and `ip.dst=10.0.14.1`
- rows with `ip.src=10.0.14.1` and `ip.dst=10.0.14.100` or `10.0.14.101`

### 13.4 Inspect proxy-added headers
Because the proxy injects headers, you can search for them in HTTP responses:

```bash
tshark -r artifacts/demo.pcap -Y 'http.response and http contains "X-Backend"' -V | head -80
```

Expected outcome:
- one or more HTTP responses contain an `X-Backend` header

### 13.5 TCP handshake observation
```bash
tshark -r artifacts/demo.pcap -Y 'tcp.flags.syn==1 and tcp.flags.ack==0' -T fields -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport | head -20
```

Expected outcome:
- SYN packets for connections `cli→lb` and `lb→backend`

---

## 14. Optional extensions (for deeper understanding)

These are not required for a basic pass, but they can help you practise:

1. **Proxy algorithm**  
   Add a new selection algorithm to `python/apps/lb_proxy.py` (example: weighted round robin).

2. **Timeouts and resilience**  
   Introduce a backend delay and observe how it affects end-to-end latency.

3. **Measurement**  
   Extend `python/apps/http_client.py` to compute latency percentiles (p50, p95 and p99).

4. **Failure modes**  
   Stop `app1` during a run and document the observed error behaviour, then restore it and confirm recovery.

