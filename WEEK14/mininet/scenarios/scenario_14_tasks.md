# Scenario W14 — Laboratory Tasks (Review)

**Week 14 — Integrated Review & Project Evaluation**  
Computer Networks — CSIE/ASE

---

## Objectives

- Consolidate semester concepts in an integrated scenario
- Verify reproducibility of a distributed system
- Prepare for team project presentation

---

## Tasks

### S1: Setup and Environment Verification (10 min)

```bash
# Start from kit directory
cd starterkit_week_14

# Verify dependencies
make verify

# Run automated demo
make run-demo

# Check artefacts
ls -la artifacts/
cat artifacts/validation.txt
```

**Control questions:**
1. What artefacts does the demo produce?
2. What does the `validation.txt` file contain?
3. What TCP conversations appear in `demo.pcap`?

---

### S2: Traffic Analysis (15 min)

Use tshark for capture analysis:

```bash
# IP conversations
tshark -r artifacts/demo.pcap -q -z conv,ip

# HTTP requests
tshark -r artifacts/demo.pcap -Y "http.request" \
  -T fields -e ip.src -e ip.dst -e http.request.uri

# TCP handshakes (SYN)
tshark -r artifacts/demo.pcap \
  -Y "tcp.flags.syn==1 && tcp.flags.ack==0" \
  -T fields -e frame.number -e ip.src -e ip.dst -e tcp.dstport

# Connections on port 8080
tshark -r artifacts/demo.pcap -Y "tcp.port==8080" | head -20
```

**Task:** Identify and document:
- Number of distinct TCP connections
- Distribution of HTTP requests between backends
- Average response latency

---

### S3: Error Diagnostics (15 min)

Simulate and diagnose errors:

```bash
# Start topology interactively
make run-lab

# In Mininet CLI:
mininet> app1 ip link set app1-eth0 down  # Disconnect app1
mininet> cli curl -v http://10.0.14.10:8080/
mininet> app1 ip link set app1-eth0 up    # Reconnect
```

**Questions:**
1. What happens when a backend becomes unavailable?
2. How does the load balancer detect backend state?
3. How would you implement automatic health checking?

---

### S4: Modifications and Tests (20 min)

#### S4a: Topology modification

Edit `mininet/topologies/topo_14_recap.py`:
- Add a third backend (`app3` with IP 10.0.14.4)
- Change link delay to 5ms
- Run demo again and compare latencies

#### S4b: Load balancer modification

Edit `python/apps/lb_proxy.py`:
- Change algorithm from round-robin to random
- Add logging for each distributed request
- Test with 50 requests and verify distribution

---

### S5: Verification Harness (10 min)

Use the harness for automated verification:

```bash
# From kit directory
python3 python/exercises/ex_14_02.py \
  --config project_config.json \
  --out artifacts/harness_report.json

# Check results
cat artifacts/harness_report.json | python3 -m json.tool
```

**Task:** Modify `project_config.json` to add:
- Latency check (verify that RTT < 100ms)
- Check for `/health` endpoint on load balancer
- Check for TCP echo server availability

---

### S6: Project Presentation Preparation (10 min)

**Project checklist:**

- [ ] Clear README.md with: installation, startup, testing, cleanup
- [ ] Demo plan: steps + commands + expected output
- [ ] pcap capture (1-2 files) with interpretation
- [ ] Report.json from harness
- [ ] Prepared answers for defence questions

**Frequent defence questions:**
1. How does TCP handshake work in your system?
2. What happens when a component fails?
3. How did you test reproducibility?
4. What limitations does your implementation have?
5. What would you do differently if you started again?

---

## Deliverables

After completing tasks, students should have:

1. **Generated artefacts:** `artifacts/demo.pcap`, `demo.log`, `validation.txt`
2. **Harness report:** `artifacts/harness_report.json`
3. **Personal notes:** Answers to control questions
4. **Modifications (optional):** Modified code + observed differences

---

## Useful Resources

- RFC 793 (TCP): https://datatracker.ietf.org/doc/html/rfc793
- RFC 2616 (HTTP/1.1): https://datatracker.ietf.org/doc/html/rfc2616
- Mininet Walkthrough: http://mininet.org/walkthrough/
- Tshark Manual: https://www.wireshark.org/docs/man-pages/tshark.html
