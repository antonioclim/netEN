# Week 14 Laboratory

## Topic
**Integrated recap**: Mininet topology, traffic generation, TCP and HTTP services, a simple load balancer (reverse proxy) and packet capture.

The practical goal is to rehearse end-to-end reasoning: what should happen, where the packets go and how to validate the behaviour with logs and PCAP analysis.

## Objectives
By the end of this lab you should be able to:
- Build a reproducible Mininet topology with a fixed IP plan
- Run application-layer services inside Mininet hosts
- Understand the difference between host namespace traffic and Mininet host traffic
- Verify behaviour with ping, curl, logs and PCAP analysis

## Prerequisites
- Ubuntu 22.04+ or 24.04+ with sudo access
- Mininet and Open vSwitch installed
- tcpdump and tshark installed (for packet capture and analysis)

The kit is designed to work **without** an external OpenFlow controller. Switches run in **Open vSwitch standalone mode**.

## Network topology and IP plan
Nodes (10.0.14.0/24):
- `lb`   — 10.0.14.1    load balancer / reverse proxy
- `cli`  — 10.0.14.11   client
- `app1` — 10.0.14.100  backend server 1
- `app2` — 10.0.14.101  backend server 2

Switches:
- `s1`, `s2` (Open vSwitch in standalone mode)

## 0. Setup
From the kit root directory:

```bash
make setup
make verify
```

Expected output (high level):
- You should see `✓` for Mininet, Open vSwitch, tcpdump and tshark
- The script may print warnings if something is optional

## 1. Start the topology (interactive)

```bash
sudo python3 mininet/topologies/topo_14_recap.py --cli
```

Inside the Mininet CLI:

```text
mininet> net
mininet> dump
mininet> cli ping -c 1 lb
mininet> cli ping -c 1 app1
mininet> cli ping -c 1 app2
```

Expected output:
- `cli` should reach `lb`, `app1` and `app2`
- `net` should show the five links of the topology

## 2. Run the HTTP load balancer manually

### Terminal inside Mininet: start backend servers
In the Mininet CLI, start backend HTTP servers on `app1` and `app2`:

```text
mininet> app1 python3 python/apps/backend_server.py --id app1 --port 8080 &
mininet> app2 python3 python/apps/backend_server.py --id app2 --port 8080 &
```

Expected output:
- Each backend prints a line similar to `Serving on 0.0.0.0:8080 (backend_id=app1)`.

### Terminal inside Mininet: start the load balancer
Start the proxy on `lb`:

```text
mininet> lb python3 python/apps/lb_proxy.py --listen 0.0.0.0:8080 --backend 10.0.14.100:8080 --backend 10.0.14.101:8080 &
```

Expected output:
- The proxy prints it is listening on port 8080
- It lists both configured backends

### Terminal inside Mininet: generate traffic
Run multiple HTTP requests from `cli`:

```text
mininet> cli python3 python/apps/http_client.py --url http://10.0.14.1:8080/ --count 12 --interval 0.10
```

Expected output:
- Most requests should be `status=200`
- You should observe alternating `backend=` values over multiple requests

If you want a quick header-only check:

```text
mininet> cli curl -s -D - http://10.0.14.1:8080/ -o /dev/null | grep X-Backend
```

Expected output:
- A line like `X-Backend: 10.0.14.100:8080` or `X-Backend: 10.0.14.101:8080`

## 3. Run the TCP echo service manually

### Start the echo server on app2

```text
mininet> app2 python3 python/apps/tcp_echo_server.py --host 0.0.0.0 --port 9000 &
```

### Run the client from cli

```text
mininet> cli python3 python/apps/tcp_echo_client.py --host 10.0.14.101 --port 9000 --message 'hello-week14' --repeat 3
```

Expected output:
- The client prints that the echo is valid for each message

## 4. Capture traffic and analyse

### Capture on the load balancer interface
You can capture traffic on the `lb` host interface (inside Mininet namespaces):

```text
mininet> lb tcpdump -ni lb-eth0 -w /tmp/week14_manual.pcap &
```

Generate a few requests from `cli`, then stop tcpdump:

```text
mininet> cli curl -s http://10.0.14.1:8080/ >/dev/null
mininet> lb pkill -INT tcpdump
```

### Analyse with tshark (from the real host OS)
Exit Mininet (`exit`), then run:

```bash
tshark -r /tmp/week14_manual.pcap -q -z http,stat
tshark -r /tmp/week14_manual.pcap -q -z conv,tcp
```

Expected output:
- You should see HTTP statistics and TCP conversations involving 10.0.14.11, 10.0.14.1 and 10.0.14.100/101

## 5. Run the automated demo

```bash
sudo make run-demo
```

Expected artefacts in `artifacts/`:
- `demo.log` — consolidated human-readable output
- `demo.pcap` — demonstrative capture created during the run
- `http_client.log` — per-request log lines
- `report.json` — summary (requests, latency, distribution)
- `tshark_summary.txt` — brief tshark analysis
- `validation.txt` — checklist style pass/fail summary

## Exercises
1. Increase the number of requests and observe how the backend distribution changes.
2. Stop `app1` and observe how the proxy behaves.
3. Modify `lb_proxy.py` to add weighted round-robin and compare distributions.
4. Use `tshark` filters to isolate only traffic between `cli` and `lb`.

