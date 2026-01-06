# Week 10 — Application Layer Protocols

**Topics:** HTTP and HTTPS, REST, DNS, SSH and FTP

This starter kit has two complementary parts:

1. **Docker Compose seminar stack** — small, observable services (HTTP, DNS, SSH and FTP) that you can probe with standard tooling.
2. **Python laboratory exercises** — HTTPS (self-signed) and REST maturity levels (Richardson model), with built-in selftests.

The kit is designed to be easy to run, easy to observe and easy to grade. The automated workflow always produces an `artifacts/validation.txt` summary, even when some tests fail.

## Learning outcomes

After completing Week 10 you should be able to:

- Distinguish **application-layer semantics** (HTTP methods, status codes, DNS records, FTP commands) from **transport-layer behaviour** (TCP connections, UDP datagrams, handshakes)
- Use standard tools to test services: `curl`, `dig`, `ssh`, `netcat`, `tcpdump`, `tshark`
- Explain what changes when adding **TLS** (server identity, certificates and trust)
- Recognise and explain the **REST maturity levels** (levels 0–3)
- Produce a packet capture and extract evidence (requests, replies and handshakes)

## Tested environment

The kit is written for a Linux host and has been tested in the following baseline configuration:

- Ubuntu 24.04 LTS
- Python 3.12
- Docker Engine and Docker Compose (v2)
- Mininet (optional for the Mininet section)

## Repository structure

Key directories:

- `docker/` — Docker Compose stack and service implementations
- `python/exercises/` — laboratory exercises (`ex_10_01_https.py`, `ex_10_02_rest_levels.py`)
- `mininet/topologies/` — optional Mininet topology scripts
- `scripts/` — canonical scripts used by Make targets
- `tests/` — smoke tests
- `certs/` — generated TLS certificate and key (created by `make setup`)
- `artifacts/` — generated outputs from `make run-all` (logs, pcap and validation)
- `pcap/` — manual capture output from `make capture`

## Quick start

### 1) Install host dependencies

On Ubuntu 24.04, a typical baseline is:

```bash
sudo apt-get update
sudo apt-get install -y \
  python3 python3-pip python3-venv \
  curl netcat-openbsd \
  tcpdump tshark \
  docker.io docker-compose \
  mininet openvswitch-switch
```

Notes:

- If Docker is installed from the Docker repository (recommended in many environments), `docker compose` is still the expected interface.
- Some environments restrict packet capture. If packet capture fails without `sudo`, run capture commands with `sudo`.

### 2) Initialise the Python environment and generate TLS certificates

```bash
make setup
```

This will:

- Create a local virtual environment in `.venv/`
- Install `requirements.txt`
- Generate a self-signed certificate and key in `certs/`

### 3) Verify the environment

```bash
make verify
```

### 4) Run the automated demo

```bash
make run-all
```

If you want a real packet capture in `artifacts/demo.pcap`, run:

```bash
sudo make run-all
```

Without `sudo`, the kit still completes but it writes a placeholder pcap (so grading pipelines are not blocked by capture permissions).

## Automated demo and grading artefacts

`make run-all` performs the following checks:

1. Builds Docker images
2. Starts the Docker stack (`web`, `dns-server`, `ssh-server`, `ftp-server`, `debug`)
3. Probes services:
   - HTTP probe (host `curl`)
   - DNS probe (`dig` inside the debug container)
   - SSH probe (Paramiko client in a short-lived container)
   - FTP probe (Python `ftplib` on the host)
4. Runs local Python selftests:
   - HTTPS exercise selftest
   - REST maturity selftest
5. Writes logs and a final validation summary
6. Cleans up the environment

Artefacts written to `artifacts/` include:

- `validation.txt` — summary of PASS or FAIL for each check
- `demo.log` — high-level log of the run
- `docker_status.log` — Docker Compose status during the run
- `http_test.log`, `dns_test.log`, `ssh_test.log`, `ftp_test.log` — per-service outputs
- `https_selftest.log`, `rest_selftest.log` — local exercise selftest outputs
- `demo.pcap` — packet capture (real if run with `sudo`, placeholder otherwise)

## Seminar demos

### Start and stop the Docker stack

Start services:

```bash
make docker-up
```

Check service status and health:

```bash
make docker-health
```

Tail logs:

```bash
make docker-logs
```

Stop services:

```bash
make docker-down
```

Important detail: the **SSH client** is executed on demand (it is not a long-running service). Use `make ssh-test` to run it.

### Ports and endpoints

On the host:

- HTTP web server: `http://127.0.0.1:8000/`
- DNS server: UDP `127.0.0.1:5353`
- SSH server: `ssh -p 2222 lab@127.0.0.1` (password `labpass`)
- FTP server: `127.0.0.1:2121` (anonymous login)

Inside the Docker network:

- Services are reachable by name: `web`, `dns-server`, `ssh-server`, `ftp-server`

### Demo 1 — HTTP

```bash
make docker-up
curl -i http://127.0.0.1:8000/
curl -i http://127.0.0.1:8000/hello.txt
curl -i http://127.0.0.1:8000/does-not-exist
```

What to observe:

- Request and response headers
- Status codes (`200 OK`, `404 Not Found`)
- Content type and content length

### Demo 2 — DNS

Recommended (uses the debug container so that `dig` is always available):

```bash
make dns-test
```

Manual equivalent:

```bash
cd docker
docker compose exec debug sh -lc 'dig @dns-server -p 5353 example.com +noall +answer'
```

If you have `dig` on the host you can also query directly:

```bash
dig @127.0.0.1 -p 5353 example.com +noall +answer
```

What to observe:

- UDP request and reply
- Response record type and value

### Demo 3 — SSH

Paramiko client demo (recommended):

```bash
make ssh-test
```

Host interactive login:

```bash
ssh -p 2222 lab@127.0.0.1
```

What to observe:

- TCP connection to port 2222 on the host
- Key exchange and encryption negotiation
- Authentication and command execution

### Demo 4 — FTP

Automated FTP test:

```bash
make ftp-test
```

Manual control-channel inspection (useful for seeing banner and replies):

```bash
nc -v 127.0.0.1 2121
```

Then try commands:

```
USER anonymous
PASS anonymous@
SYST
PWD
LIST
QUIT
```

What to observe:

- FTP is command-driven on a TCP control channel
- Server replies are numeric codes (`220`, `331`, `230` and so on)

### Debug container

Enter the debug container:

```bash
make docker-debug
```

Typical commands to run inside:

```bash
ip a
netstat -tulpn || true
nc -vz web 8000
nc -vz ftp-server 2121
```

## Laboratory exercise 1 — HTTPS (self-signed)

The HTTPS exercise is in `python/exercises/ex_10_01_https.py`.

### Run the selftest

```bash
make https-test
```

### Run manually

Terminal 1 (server):

```bash
. .venv/bin/activate
python3 python/exercises/ex_10_01_https.py serve --host 127.0.0.1 --port 8443
```

Terminal 2 (client using curl):

```bash
# You will get a certificate verification error unless you disable verification
curl -i https://127.0.0.1:8443/

# Ignore certificate verification (for demonstration only)
curl -k -i https://127.0.0.1:8443/

# Verify using the generated certificate as a trusted root
curl --cacert certs/server.crt \
  --resolve lab.network.local:8443:127.0.0.1 \
  https://lab.network.local:8443/
```

Terminal 2 (client using the Python client mode):

```bash
. .venv/bin/activate
python3 python/exercises/ex_10_01_https.py client --url https://127.0.0.1:8443/ --insecure
python3 python/exercises/ex_10_01_https.py client --url https://lab.network.local:8443/ --ca certs/server.crt
```

What to observe:

- The TLS handshake occurs before HTTP application data
- Certificate name matching and trust chain validation

## Laboratory exercise 2 — REST maturity levels

The REST maturity exercise is in `python/exercises/ex_10_02_rest_levels.py`.

### Run the selftest

```bash
make rest-test
```

### Run manually

Terminal 1 (server):

```bash
. .venv/bin/activate
python3 python/exercises/ex_10_02_rest_levels.py serve --host 127.0.0.1 --port 5000
```

Terminal 2 (probe endpoints):

Level 0 (procedure-style endpoints):

```bash
curl -s http://127.0.0.1:5000/level0/list_users
curl -s http://127.0.0.1:5000/level0/get_user/1
curl -s -X POST http://127.0.0.1:5000/level0/create_user \
  -H 'Content-Type: application/json' \
  -d '{"name":"Alice"}'
```

Level 1 (resource, but verbs embedded in the URI):

```bash
curl -s http://127.0.0.1:5000/level1/users
curl -s http://127.0.0.1:5000/level1/users/1
curl -s -X POST http://127.0.0.1:5000/level1/users \
  -H 'Content-Type: application/json' \
  -d '{"name":"Bob"}'
```

Level 2 (resources and proper HTTP verbs):

```bash
curl -i http://127.0.0.1:5000/level2/users
curl -i -X POST http://127.0.0.1:5000/level2/users \
  -H 'Content-Type: application/json' \
  -d '{"name":"Charlie"}'
```

Level 3 (HATEOAS, hypermedia links):

```bash
curl -s http://127.0.0.1:5000/level3/
curl -s http://127.0.0.1:5000/level3/users
curl -s http://127.0.0.1:5000/level3/users/1
```

What to observe:

- How the URI design changes across levels
- How HTTP methods and status codes are used properly at higher maturity levels
- How `_links` allows discoverability at level 3

## Mininet topologies (optional)

Mininet is optional for Week 10 but it is included for students who want to observe routing and service placement.

Start the base routed topology:

```bash
sudo make mininet-cli
```

Start the services topology (router plus service hosts):

```bash
sudo make mininet-services
```

Quick tests:

```bash
sudo make mininet-test
```

Cleanup:

```bash
sudo make mininet-clean
```

## Packet capture

### Automated capture

Run the full demo with capture enabled:

```bash
sudo make run-all
```

This should generate a real `artifacts/demo.pcap`.

### Manual capture

```bash
sudo make capture
```

This writes `pcap/last_capture.pcap` (a short capture focused on the demo ports).

The capture filters include the following ports:

- 8000 (HTTP)
- 8443 (HTTPS)
- 5000 (REST maturity demo)
- 5353/udp (DNS)
- 2222 (SSH host port mapping)
- 2121 (FTP)

## Troubleshooting

### Docker permission denied

If you see a permission error when running Docker, either run with `sudo` or add your user to the `docker` group:

```bash
sudo usermod -aG docker "$USER"
# then log out and log back in
```

### A port is already in use

Check:

```bash
sudo ss -ltnup | grep -E ':(8000|8443|5000|5353|2222|2121)'
```

Then stop the conflicting process or change the port mapping in `docker/docker-compose.yml`.

### A Docker service is unhealthy

Run:

```bash
make docker-health
make docker-logs
```

### Packet capture is empty

Packet capture generally requires elevated privileges. Use:

```bash
sudo make run-all
# or
sudo make capture
```

## Cleaning and reset

- `make clean` removes generated files (artefacts, captures and caches) but keeps `.venv/` and `certs/`.
- `make reset` performs a full reset (includes Docker, Mininet, `.venv/` and generated certificates).

