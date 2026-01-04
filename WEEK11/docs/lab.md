# Laboratory 11: FTP, DNS, SSH + Load Balancing

## Overview

**Week**: 11 of 14  
**Duration**: 2-3 hours practical laboratory  
**Objective**: Hands-on experimentation with application protocols and load balancing

---

## Laboratory Structure

| Step | Activity | Est. Duration |
|------|----------|---------------|
| 0 | Environment preparation | 10 min |
| 1 | System verification | 5 min |
| 2 | HTTP Backend | 10 min |
| 3 | Python Load Balancer | 20 min |
| 4 | Nginx Docker | 15 min |
| 5 | Manual DNS Client | 15 min |
| 6 | FTP Active/Passive | 15 min |
| 7 | Mininet Topology | 20 min |
| 8 | Traffic capture | 10 min |
| 9 | Benchmarking | 10 min |
| 10 | Cleanup | 5 min |

---

## Step 0: Environment Preparation

### Requirements
- Ubuntu 22.04+ (VM or native)
- Python 3.10+
- Docker + Docker Compose v2
- Mininet 2.3+
- tshark/Wireshark

### Quick installation

```bash
cd starterkit
make setup
```

### Verification

```bash
make verify
```

**Expected output**: All checks pass (✓).

---

## Step 1: System Verification

Run the verification script to confirm everything is ready:

```bash
./scripts/verify.sh --smoke
```

Check manually:
```bash
python3 --version       # >= 3.10
docker --version        # >= 24.0
docker compose version  # v2.x
mn --version            # 2.3.x
tshark --version        # 4.x
```

---

## Step 2: Starting HTTP Backends

### Manual (3 terminals)

**Terminal 1:**
```bash
python3 python/exercises/ex_11_01_backend.py --id 1 --port 8081
```

**Terminal 2:**
```bash
python3 python/exercises/ex_11_01_backend.py --id 2 --port 8082 --delay 0.1
```

**Terminal 3:**
```bash
python3 python/exercises/ex_11_01_backend.py --id 3 --port 8083 --delay 0.2
```

### Automatic (Makefile)

```bash
make backends-start
```

### Testing

```bash
curl http://localhost:8081/
curl http://localhost:8082/
curl http://localhost:8083/
```

**Expected output**: Each backend responds with its ID.

---

## Step 3: Python Load Balancer

### Starting LB

```bash
python3 python/exercises/ex_11_02_loadbalancer.py \
    --backends localhost:8081,localhost:8082,localhost:8083 \
    --port 8080 \
    --algorithm round_robin
```

### Round Robin Test

```bash
for i in {1..6}; do curl -s http://localhost:8080/; echo; done
```

**Expected output**: Backend 1, 2, 3, 1, 2, 3 (rotation).

### IP Hash Test

Stop LB (Ctrl+C), restart with:
```bash
python3 python/exercises/ex_11_02_loadbalancer.py \
    --backends localhost:8081,localhost:8082,localhost:8083 \
    --port 8080 \
    --algorithm ip_hash
```

```bash
for i in {1..5}; do curl -s http://localhost:8080/; echo; done
```

**Expected output**: Same backend for all requests.

### Failover Simulation

With LB in round_robin, stop Backend 2 (Ctrl+C in its terminal):
```bash
for i in {1..6}; do curl -s http://localhost:8080/ 2>/dev/null || echo "ERROR"; done
```

**Expected output**: First request to Backend 2 fails, then LB excludes it.

---

## Step 4: Nginx Load Balancer (Docker)

### Starting stack

```bash
make demo-nginx
# or
cd docker/nginx_compose && docker compose up -d
```

### Testing

```bash
for i in {1..6}; do curl -s http://localhost:80/; done
```

**Expected output**: Responses from web1, web2, web3 in rotation.

### Changing algorithm

Edit `docker/nginx_compose/nginx.conf`:
```nginx
upstream backend_pool {
    least_conn;  # Uncomment this line
    server web1:80;
    server web2:80;
    server web3:80;
}
```

Reload Nginx:
```bash
docker compose -f docker/nginx_compose/docker-compose.yml exec lb nginx -s reload
```

### Stopping

```bash
make demo-nginx-stop
```

---

## Step 5: Manual DNS Client

### A Record Query

```bash
python3 python/exercises/ex_11_03_dns_client.py google.com A --verbose
```

**Expected output**: Hexdump of sent packet + response with Google IP.

### Other record types

```bash
python3 python/exercises/ex_11_03_dns_client.py google.com MX
python3 python/exercises/ex_11_03_dns_client.py google.com TXT
python3 python/exercises/ex_11_03_dns_client.py ase.ro NS
```

### Comparison with dig

```bash
dig google.com A +short
dig google.com MX +short
```

---

## Step 6: FTP Active vs Passive

### Passive Mode (recommended)

```bash
python3 python/exercises/ex_11_04_ftp_client.py \
    --host ftp.gnu.org \
    --mode passive \
    --command "LIST /"
```

**Expected output**: Directory listing, with passive connection details.

### Active Mode

```bash
python3 python/exercises/ex_11_04_ftp_client.py \
    --host ftp.gnu.org \
    --mode active \
    --command "LIST /"
```

**Expected output**: Probably timeout (firewall blocks incoming connection).

### FTP Capture

In another terminal:
```bash
sudo tshark -i any -f "port 21" -Y ftp -c 20
```

Then run the FTP client and observe the commands and responses.

---

## Step 7: Mininet Topology

### Starting demo

```bash
sudo make demo-mininet
# or
sudo python3 mininet/topologies/topo_11_base.py
```

**Expected output**: Topology created, backends started, load balancing test, failover simulation.

### Interactive mode

```bash
sudo python3 mininet/topologies/topo_11_base.py --interactive
```

Commands in Mininet CLI:
```
mininet> h1 ping -c 3 lb
mininet> h1 curl -s http://10.0.0.1:8080/
mininet> net
mininet> exit
```

---

## Step 8: Traffic Capture

### HTTP Capture

**Terminal 1 (capture)**:
```bash
sudo tshark -i lo -f "tcp port 8080 or tcp port 8081" -w /tmp/lb.pcap
```

**Terminal 2 (traffic)**:
```bash
for i in {1..10}; do curl -s http://localhost:8080/; done
```

Stop capture (Ctrl+C) and analyse:
```bash
tshark -r /tmp/lb.pcap -Y "http" -T fields -e ip.src -e ip.dst -e http.request.uri
```

### Automatic script

```bash
make capture
```

---

## Step 9: Benchmarking

### Apache Bench

```bash
ab -n 1000 -c 10 http://localhost:8080/
```

**Metrics to observe**:
- Requests per second
- Time per request (mean)
- Percentile latencies (50%, 95%, 99%)

### Integrated generator

```bash
python3 python/exercises/ex_11_02_loadbalancer.py \
    --backends localhost:8081,localhost:8082,localhost:8083 \
    --load-test --requests 500 --workers 20
```

### Algorithm comparison

```bash
# Test round_robin
make lb-start-rr && make benchmark && make lb-stop

# Test least_conn
make lb-start-lc && make benchmark && make lb-stop
```

---

## Step 10: Cleanup

```bash
make clean
```

Verify no processes remain:
```bash
ps aux | grep -E "backend|loadbalancer" | grep -v grep
docker ps
```

---

## Expected Outcomes

| Step | What you should observe |
|------|-------------------------|
| 2 | 3 backends respond on different ports |
| 3 | Round robin distributes uniformly; IP hash maintains sticky sessions |
| 4 | Nginx works similarly to Python LB, but faster |
| 5 | Manual DNS packet construction, decoded responses |
| 6 | Passive works, active fails in most configurations |
| 7 | Complete virtual topology in Mininet |
| 8 | Traffic visible in tshark, analysable |
| 9 | Python LB: ~500 req/s; Nginx: ~10,000+ req/s |

---

## Troubleshooting

### Port occupied

```bash
sudo lsof -i :8080
sudo kill <PID>
```

### Docker permission denied

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Mininet requires root

```bash
sudo mn -c  # Clean old processes
sudo python3 <script>.py
```

---

## Grading

The laboratory contributes to the seminar grade according to the rubric in `docs/rubrici.md`.

---

*Document generated for Laboratory 11 – Computer Networks*  
*Revolvix&Hypotheticalandrei*
