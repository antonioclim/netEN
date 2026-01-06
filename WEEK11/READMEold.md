# Week 11 — Application Layer: HTTP, DNS, FTP, SSH and Load Balancing (Docker and Mininet)

This week focuses on application-layer protocols and service composition, with an emphasis on *how* applications use transport and network services in practice. The kit provides working, inspectable implementations and demos for:

- HTTP backends and a custom Python load balancer (round robin, least connections and IP hash)
- An Nginx reverse proxy configured as an HTTP load balancer (Docker Compose)
- Containerised demos for DNS, FTP and SSH
- A Mininet topology to observe flows over an emulated network
- A canonical `Makefile` interface plus scripts for setup, verification, demos, capture and cleanup

All commands below assume you are **inside the `WEEK11/` directory** (the one that contains the `Makefile`).

---

## Repository layout

- `Makefile` — canonical entry point
- `scripts/` — setup, verification, capture, automated runs and cleanup
- `python/exercises/` — the laboratory Python exercises (backend server, load balancer, DNS client)
- `docker/`
  - `nginx_compose/` — Nginx reverse proxy load balancer demo
  - `custom_lb_compose/` — containerised custom load balancer demo
  - `dns_demo/`, `ftp_demo/`, `ssh_demo/` — protocol demos (each includes its own `README.md`)
- `mininet/` — Mininet topology scripts
- `docs/` — laboratory notes and extended explanations
- `artifacts/` — generated logs, validation output and packet captures

---

## Quick start

### 1) Obtain the kit (example: sparse checkout)

```bash
mkdir -p ~/cn-labs && cd ~/cn-labs
git clone <YOUR_REPO_URL> cn-labs
cd cn-labs

git sparse-checkout init --cone
git sparse-checkout set WEEK11
git checkout main

cd WEEK11
```

If you already have the archive, simply extract it and `cd WEEK11`.

### 2) Install dependencies

Minimal dependencies (Python requirements plus standard CLI tools):

```bash
make setup
```

Full environment (adds Docker and Mininet support where possible):

```bash
make setup-full
```

### 3) Verify and run a quick sanity check

```bash
make verify
make smoke-test
```

`make smoke-test` is designed to be safe on a fresh kit. It performs structural and syntax checks. If you have not yet produced `artifacts/` outputs, it will emit warnings rather than failing.

### 4) Run the automated demo pipeline

This generates `artifacts/demo.log`, `artifacts/demo.pcap` and `artifacts/validation.txt`.

```bash
sudo make run-all
# alias:
sudo make all
```

If you want to run without packet capture:

```bash
make run-all-no-capture
```

---

## Port map

These defaults help you avoid collisions between demos.

- **8080** — Nginx load balancer demo (`make demo-nginx`) and the Python lab load balancer (`make lb-start`)
- **8081–8083** — Python lab backends (`make backends-start`)
- **9090** — Docker custom load balancer demo (`make demo-custom-lb`)
- **2121** — FTP demo (Docker)
- Other ports are used internally by the Docker demos and Mininet scripts

If you see `bind: address already in use`, stop the previously running demo (`make demo-*-stop`) or run `make clean`.

---

## Demos

### Demo 1 — Nginx reverse proxy load balancing (Docker, port 8080)

Start:

```bash
make demo-nginx
```

Test (observe alternation in the response body):

```bash
for i in {1..9}; do curl -s http://localhost:8080/ | head -1; done
```

Stop:

```bash
make demo-nginx-stop
```

### Demo 2 — Custom load balancer (Docker, port 9090)

Start:

```bash
make demo-custom-lb
```

Test:

```bash
for i in {1..9}; do curl -s http://localhost:9090/ | head -1; done
```

Stop:

```bash
make demo-custom-lb-stop
```

### Demo 3 — Python lab: backends and load balancer (round robin, least connections and IP hash)

Start the three backends (ports 8081–8083):

```bash
make backends-start
```

Start the load balancer on port 8080 (round robin):

```bash
make lb-start
```

Test alternation:

```bash
for i in {1..9}; do curl -s http://127.0.0.1:8080/ -D - | grep -E "X-Backend-ID|HTTP/" | head -2; done
```

Try other algorithms:

```bash
make lb-stop
make lb-start-lc   # least connections
# or:
make lb-stop
make lb-start-ip   # IP hash (sticky per client address)
```

Stop everything:

```bash
make lb-stop
make backends-stop
```

### Demo 4 — DNS client

```bash
make demo-dns
```

This uses the Python DNS client in `python/exercises/ex_11_03_dns_client.py` and, by default, queries a public resolver. An extended containerised DNS setup is available under `docker/dns_demo/` (see its `README.md`).

### Demo 5 — FTP and SSH (Docker)

```bash
make demo-ftp
make demo-ssh
```

For interactive walkthroughs, consult:

- `docker/ftp_demo/README.md`
- `docker/ssh_demo/README.md`

### Demo 6 — Mininet topology

Run the Mininet demo:

```bash
sudo make demo-mininet
```

To open a Mininet CLI after the topology starts:

```bash
sudo make demo-mininet-cli
```

A slightly extended topology is available via:

```bash
sudo make demo-mininet-extended
```

---

## Packet capture

The capture script writes to `artifacts/demo.pcap`. Capture requires elevated privileges.

Capture the default HTTP port (8080):

```bash
sudo make capture
```

Capture a different port (example: the Docker custom load balancer on 9090):

```bash
make capture CAPTURE_PORT=9090
```

To print a live summary of traffic on the default port:

```bash
make capture-traffic
```

---

## Cleanup and reset

Stop demos and remove temporary files:

```bash
make clean
```

Full reset (also performs Docker pruning and Mininet/OVS cleanup, requires sudo):

```bash
make reset
```

---

## Laboratory notes

See the detailed laboratory explanation in:

- `docs/lab.md`

The laboratory Python exercises are in:

- `python/exercises/`



## Learning objectives

By the end of Week 11, you should be able to:

- Describe how HTTP applications sit on top of TCP and what happens when intermediaries (proxies and load balancers) are inserted
- Compare common load-balancing strategies (round robin, least connections and IP hash) and state when each is appropriate
- Explain the practical role of DNS, FTP and SSH as application-layer protocols, including typical ports and common failure modes
- Use containerised services to reproduce network behaviour in a controlled manner
- Capture and interpret traffic traces in Wireshark, including HTTP request/response exchanges and connection reuse

---

## What you should observe

### Python lab load balancer

When you call the load balancer repeatedly:

- The response header `X-Backend-ID` should rotate across the configured backends under **round robin**
- Under **least connections**, concurrent requests should be biased towards the backend(s) with fewer active connections
- Under **IP hash**, the same client address should be routed consistently to the same backend (sticky behaviour)

### Nginx reverse proxy load balancer

When you call the Nginx endpoint repeatedly:

- The response body should alternate between the upstream backends (for example, `Backend 1`, `Backend 2`, `Backend 3`)
- If you run a packet capture, you should see HTTP requests from the client to the proxy and from the proxy to the upstream containers

---

## Troubleshooting

### Docker is installed but `docker compose` fails

- Ensure the Docker daemon is running: `sudo systemctl status docker`
- If you are not using `sudo` for Docker commands, ensure your user is in the `docker` group and you have started a new login session:
  `sudo usermod -aG docker "$USER"`

### `bind: address already in use`

A demo is already using the port. Stop the relevant stack and retry:

```bash
make demo-nginx-stop
make demo-custom-lb-stop
make clean
```

### Packet capture produces an empty file

Packet capture requires elevated privileges. Use:

```bash
sudo make capture
```

If capture is deliberately disabled, use:

```bash
make run-all-no-capture
```

---

## Further reading within this kit

- `docs/curs.md` — lecture notes
- `docs/seminar.md` — seminar material
- `docs/lab.md` — laboratory instructions
- `docs/checklist.md` — self-check list for the week
- `docs/rubrici.md` — evaluation rubric

