# Week 11 — Load Balancing (Nginx, Docker and a Custom Proxy)

This starter kit supports several practical demonstrations and laboratory exercises around **load balancing** and **reverse proxies**. The core goals are to understand how a load balancer distributes requests across backends, how failures are handled and how traffic can be observed with headers, logs and packet capture.

The kit is designed so that:

- a clean clone can be verified immediately (`make smoke-test`)
- each demo can be run in isolation (`make demo-*`)
- there is an automated end-to-end run that produces artefacts (`make run-all`)

---

## Learning objectives

By the end of this week you should be able to:

- explain why load balancing is needed (availability, throughput and latency)
- compare **round-robin**, **least-connections**, **weighted** strategies and **sticky** strategies
- identify what the client sees versus what the backend sees in a reverse-proxy architecture
- use basic observability techniques (response headers, backend logs and PCAP capture)

---

## Repository structure

```
WEEK11/
├── Makefile
├── README.md
├── scripts/                 # setup, verify, cleanup, capture and run-all
├── tests/                   # smoke test
├── docker/
│   ├── nginx_compose/        # Nginx load balancer + 3 backends
│   ├── custom_lb_compose/    # optional: custom Python load balancer in Docker
│   ├── dns_demo/
│   ├── ftp_demo/
│   └── ssh_demo/
├── python/                   # laboratory Python exercises
├── topo/                     # Mininet topologies
├── docs/                     # supplementary notes and analysis
├── pcap/                     # capture output from make capture/capture-traffic
└── artifacts/                # artefacts produced by make run-all
```

---

## Requirements

Essential:

- Ubuntu 22.04+ (tested on Ubuntu 24.04)
- Python 3
- Docker (Docker Engine) and Docker Compose v2 (`docker compose`)
- `curl`
- `netcat` (`nc`)

Optional but recommended:

- `tshark` (Wireshark CLI) or `tcpdump` for traffic capture

---

## Setup and verification

From inside the kit directory:

```bash
cd ~/WEEK11
make verify
```

If anything essential is missing:

```bash
make setup
make verify
```

---

## Quick validation

A quick, non-destructive check:

```bash
make smoke-test
```

Notes:

- On a fresh clone, the smoke test will report **warnings** for missing demo artefacts (because you have not run any demo yet). This is expected.
- After `make run-all`, the smoke test will also validate the generated logs and validation report.

---

## Demo 1 — Nginx reverse proxy load balancer

This demo uses **Docker Compose** to start:

- an Nginx reverse proxy load balancer
- three backend web servers (`web1`, `web2` and `web3`)

The public endpoint is:

- `http://localhost:8080/`
- `http://localhost:8080/health`

### One-command demo

```bash
make demo-nginx
```

What the demo prints:

- HTTP status codes
- `X-Load-Balancer: nginx`
- `X-Served-By: <upstream_ip:80>` (the upstream address selected by Nginx)
- the first line of the response body (`Backend 1 ...`, `Backend 2 ...`, `Backend 3 ...`)

Stop it with:

```bash
make demo-nginx-stop
```

### Multi-terminal observation (recommended)

This is the easiest way to *see activity* and connect it to concepts.

#### Terminal 1 — start the stack

```bash
make demo-nginx
```

#### Terminal 2 — watch backend logs (includes X-Forwarded-For)

```bash
docker compose -f docker/nginx_compose/docker-compose.yml logs -f web1
```

#### Terminal 3 — watch another backend

```bash
docker compose -f docker/nginx_compose/docker-compose.yml logs -f web2
```

#### Terminal 4 — generate traffic and observe backend selection

```bash
for i in {1..12}; do
  echo "--- request $i ---"
  curl -s -D - -o /dev/null http://localhost:8080/ | grep -iE 'HTTP/|X-Load-Balancer:|X-Served-By:'
  curl -s http://localhost:8080/ | head -n 1
  sleep 0.2
done
```

What you should observe:

- **Round-robin distribution**: `X-Served-By` alternates across multiple upstream addresses
- **Reverse-proxy behaviour**: the backend logs show `xff="..."` (the `X-Forwarded-For` value)
- **Two TCP legs**: client→load balancer and load balancer→backend (best observed via a capture)

#### Mapping `X-Served-By` to backends

`X-Served-By` reports an upstream address (IP:80). You can map it to containers:

```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' s11_backend_1
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' s11_backend_2
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' s11_backend_3
```

---

## Demo 2 — Custom load balancer (Python reverse proxy)

This demo uses a small **Python reverse proxy** that performs load balancing across backends.

### Option A: Dockerised demo

```bash
make demo-custom-lb
```

Stop it with:

```bash
make demo-custom-lb-stop
```

### Option B: Laboratory mode (run processes locally)

This mode is useful when you want to edit the Python exercise code.

#### Terminal 1 — start backends

```bash
make backends-start
```

#### Terminal 2 — start the Python load balancer

```bash
make lb-start
```

#### Terminal 3 — test distribution

```bash
for i in {1..12}; do
  curl -s http://localhost:8080/ | head -n 1
  sleep 0.2
done
```

Stop processes:

```bash
make lb-stop
make backends-stop
```

---

## DNS, FTP and SSH demos

These are additional supporting demos.

- DNS:
  - `make demo-dns`
  - `make demo-dns-stop`
- FTP:
  - `make demo-ftp`
  - `make demo-ftp-stop`
- SSH:
  - `make demo-ssh`
  - `make demo-ssh-stop`

---

## Traffic capture

### Capture with tshark

```bash
make capture
```

### Capture with tcpdump

```bash
make capture-traffic
```

Captures are written under:

- `pcap/` (captures started via Makefile targets)
- `artifacts/demo.pcap` (capture attempted automatically by `make run-all`)

Useful display filters:

- `tcp.port == 8080`
- `http`

---

## Automated end-to-end run

`make run-all` starts the Nginx load balancer demo, generates traffic, attempts a capture (when permitted) and writes a validation report.

```bash
make run-all
```

Outputs are written to:

- `artifacts/demo.log`
- `artifacts/demo.pcap` (may be empty if capture privileges were not available)
- `artifacts/validation.txt`

If you do not want any capture attempt:

```bash
make run-all-no-capture
```

If you want to keep containers running after the script completes:

```bash
bash scripts/run_all.sh --keep-containers
```

---

## Troubleshooting

### Docker permission errors

If you see errors related to Docker permissions, ensure your user is in the `docker` group:

```bash
sudo usermod -aG docker "$USER"
```

Then **log out and log back in**.

### Nginx returns an HTML error page (for example, 502 Bad Gateway)

This typically means one or more backends were not reachable at that moment.

- Re-run the demo (it waits for HTTP 200)
- Inspect logs:

```bash
docker compose -f docker/nginx_compose/docker-compose.yml logs --tail=80 nginx
```

### Packet capture is empty

Traffic capture requires privileges.

- Use `make capture` (it uses `sudo`)
- Alternatively, allow non-root capture through your system configuration (for example, Wireshark group membership)

### Ports already in use

If a demo fails with a message similar to “port is already allocated”, stop the corresponding demo:

```bash
make demo-nginx-stop
make demo-ftp-stop
make demo-custom-lb-stop
```

---

## Exercises

Suggested experiments:

- In `docker/nginx_compose/nginx.conf`, switch the upstream strategy to `least_conn` and compare behaviour
- Change backend weights and measure request distribution
- Stop one backend container and observe failover
- In the Python exercise, implement weighted round-robin or least-connections

