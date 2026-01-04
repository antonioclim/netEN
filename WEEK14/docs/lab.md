# Laboratory 14 — Dry-Run Evaluation & Practical Diagnostics

**Course:** Computer Networks / Networking  
**Week:** 14 (final)  
**Duration:** 90-120 minutes

---

## Objective

The laboratory simulates a **realistic technical evaluation**: we run the demo from the starterkit, interpret the artefacts, make controlled modifications and produce a short report.

---

## Time Plan

| Time | Activity | Deliverable |
|------|----------|-------------|
| 0-10 min | Setup + smoke test | `smoke_test.sh` OK |
| 10-25 min | Automated demo | `artifacts/` complete |
| 25-55 min | Guided pcap analysis | Answers to questions |
| 55-75 min | Modification + rerun | Observed differences |
| 75-95 min | REPORT.md | Conclusions + commands + output |
| 95-120 min | Debrief + checklist | Project presentation plan |

---

## Step 0: Environment Setup

```bash
# Enter the kit directory
cd starterkit_week_14

# Install dependencies (if not already)
sudo bash scripts/setup.sh

# Verify the environment
bash tests/smoke_test.sh
```

**Expected output:** All tests pass (✓).

---

## Step 1: Automated Demo

```bash
# Run the complete demo
make run-demo

# OR explicitly
sudo bash scripts/run_all.sh
```

**What happens:**
1. Starts Mininet network (4 hosts, 2 switches)
2. Starts backend servers on app1 and app2
3. Starts load balancer on lb
4. Starts tcpdump capture
5. Generates TCP echo and HTTP traffic
6. Stops capture and processes with tshark
7. Generates report.json

**Verification:**
```bash
ls -la artifacts/
# You should see:
# - capture_lb.pcap
# - tshark_summary.txt
# - http_client.log
# - report.json
# - app1.log, app2.log, lb.log
```

---

## Step 2: pcap Analysis

### 2.1 IP Conversations
```bash
tshark -r artifacts/capture_lb.pcap -q -z conv,ip
```

**Question:** How many distinct IP pairs appear? Which are they?

### 2.2 TCP Conversations
```bash
tshark -r artifacts/capture_lb.pcap -q -z conv,tcp
```

**Question:** How many TCP connections were established?

### 2.3 HTTP Requests
```bash
tshark -r artifacts/capture_lb.pcap -Y "http.request" \
  -T fields -e frame.number -e ip.src -e ip.dst -e http.request.uri
```

**Question:** How many HTTP requests appear? To what destinations?

### 2.4 TCP Handshake (SYN)
```bash
tshark -r artifacts/capture_lb.pcap -Y "tcp.flags.syn==1 && tcp.flags.ack==0"
```

**Question:** How many new connections (SYN) were initiated?

### 2.5 Correlation with Logs
```bash
cat artifacts/http_client.log | head -10
cat artifacts/report.json | python3 -m json.tool
```

**Question:** Does the distribution across backends correspond to what you see in the pcap?

---

## Step 3: Controlled Modifications

### Modification A: Stop a Backend
```bash
# During the demo or in a separate session:
# 1. Find the PID of the app2 backend
ps aux | grep backend_server

# 2. Stop it
kill <PID>

# 3. Generate traffic and observe
curl http://10.0.0.10:8080/
# What status do you receive? What do you see in lb.log?
```

**Expected observation:** All requests go to app1; app2 is marked unhealthy.

### Modification B: Add Delay
Edit `mininet/topologies/topo_14_recap.py`:
```python
# Change delay="1ms" to delay="50ms" in addLink()
```

Rerun the demo and compare latencies from `http_client.log`.

### Modification C: Timeout Too Small
Edit `python/apps/http_client.py`, set `--timeout 0.01` and observe the errors.

---

## Step 4: Report (REPORT.md)

Create a file `REPORT.md` with:

```markdown
# Laboratory Report W14

## 1. Commands Run
- `make run-demo`
- `tshark -r artifacts/capture_lb.pcap -q -z conv,tcp`
- ...

## 2. Main Results
- Total HTTP requests: X
- Distribution: app1=Y, app2=Z
- Average latency: W ms

## 3. Observations from pcap
- Observed N TCP handshakes
- HTTP requests distributed to: ...

## 4. Modification Tested
- Stopped backend app2
- Effect: all requests went to app1

## 5. Conclusion
- The kit correctly demonstrates the LB pattern
- Diagnostics with tshark confirm distribution
```

---

## Step 5: Cleanup

```bash
make clean
# OR
sudo bash scripts/cleanup.sh
```

---

## Additional Exercises (optional)

### E1: Own Project Verification
Adapt `project_config.json` for your project and run the harness:
```bash
python3 python/exercises/ex_14_02.py --config my_config.json --out my_report.json
```

### E2: Review Quiz
```bash
python3 python/exercises/ex_14_01.py --selftest
```

### E3: Manual Capture
```bash
# Terminal 1: start server
python3 python/apps/backend_server.py --id test --port 9999

# Terminal 2: capture
sudo tcpdump -i lo port 9999 -w /tmp/test.pcap

# Terminal 3: client
curl http://localhost:9999/

# Analysis
tshark -r /tmp/test.pcap
```

---

## Reflection Questions

1. What minimal evidence would you include in a network bug report?
2. When is pcap too much and when is it indispensable?
3. What would you automate (in CI) from this workflow?
4. How would you demonstrate that the load balancer distributes correctly?

---

## Laboratory Evaluation Criteria

| Criterion | Points |
|-----------|--------|
| Correct setup + smoke test | 2 |
| Demo ran successfully | 2 |
| Correct pcap analysis | 2 |
| Modification tested | 2 |
| REPORT.md complete | 2 |
| **Total** | **10** |

---

## Resources

- `docs/curs.md` - Review theory
- `docs/seminar.md` - Presentation preparation
- `docs/checklist.md` - Teaching staff checklist
- `tests/expected_outputs.md` - Reference outputs
