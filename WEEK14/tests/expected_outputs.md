# Expected outputs (Week 14)

This file contains short, illustrative snippets. Exact timestamps and minor formatting can differ.

## 1) `make verify`

Expected outcome:
- All required tools are detected.
- The smoke test passes.

Example (abridged):

```text
>>> Verifying dependencies and environment...

[OK] python3 available
[OK] mn (Mininet) available
[OK] ovs-vsctl available
[OK] tcpdump available
[OK] tshark available
[OK] curl available
[OK] ab (ApacheBench) available

[SMOKE] Checking kit file structure...
  ✓ PASS: README.md exists
  ✓ PASS: Makefile exists
  ✓ PASS: scripts/ directory exists
  ✓ PASS: python/apps/ directory exists
  ✓ PASS: mininet/topologies/topo_14_recap.py exists

[SMOKE] Basic syntax checks...
  ✓ PASS: bash scripts parse
  ✓ PASS: python modules compile

All smoke tests passed.
```

Notes:
- If `make verify` warns about local TCP ports (8080, 9000 etc), this refers to the host namespace.
  Mininet hosts run in separate network namespaces so those ports do not conflict.

## 2) `sudo python3 mininet/topologies/topo_14_recap.py --test`

Expected outcome:
- `pingAll` completes.
- An HTTP request from `cli` to a temporary server on `app1:8080` returns 200.

Example:

```text
============================================================
Week 14 Topology (automated test)
============================================================
[test] Ping all pairs...
*** Ping: testing ping reachability
cli -> lb app1 app2
lb -> cli app1 app2
app1 -> cli lb app2
app2 -> cli lb app1
*** Results: 0% dropped (12/12 received)

[test] Starting a temporary HTTP server on app1:8080...
[test] Testing HTTP from cli...
[test] HTTP status: 200
[test] Result: PASS
```

## 3) `sudo make run-demo`

Expected outcome:
- The automated demo completes without errors.
- `artifacts/` contains logs, a packet capture and a summary report.

Example (abridged):

```text
>>> Running integrated Week 14 demo (produces artifacts/)...

=== Week 14: Integrated Demo ===
[INFO] Starting Mininet topology...
[OK] pingAll: PASS
[INFO] Starting backends and load balancer...
[OK] HTTP requests completed: 30/30
[OK] TCP echo completed: PASS
[INFO] Capture saved to artifacts/demo.pcap
[INFO] Writing report.json and validation.txt
[OK] Demo completed successfully
✓ Demo completed successfully
```

Expected artefacts:

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

