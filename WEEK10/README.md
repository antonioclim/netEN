# Week 10 — HTTP, HTTPS, REST, SOAP and Network Services (DNS, SSH and FTP)

This starter kit supports the Week 10 laboratory. It provides:

- A Docker-based *network services lab* (HTTP, custom DNS, SSH and FTP)
- Two Python exercises focused on HTTPS and REST API design
- Two Mininet topologies to practise routing and service reachability
- Convenience targets in the `Makefile` (setup, tests, captures and cleanup)

The kit is designed for **Ubuntu 24.04** with Python 3.12 and Docker.

---

## Learning outcomes

After completing this laboratory you should be able to:

1. Explain and observe TCP connection establishment, data transfer and teardown for application protocols
2. Distinguish HTTP from HTTPS and articulate what TLS adds (authentication, confidentiality and integrity)
3. Implement a minimal HTTPS service and interact with it using `curl` and a client library
4. Compare API design patterns across the REST maturity levels (Richardson model)
5. Use common tools (`curl`, `dig`, `ssh`, `lftp`, `tcpdump`, `tshark`) to validate and troubleshoot network services
6. Capture and interpret traffic traces (pcap) for HTTP, DNS, SSH and FTP

---

## Repository structure

```
WEEK10/
  Makefile
  README.md
  requirements.txt
  scripts/           # setup, verify, run-all, capture and cleanup
  docker/            # Docker Compose lab services (DNS, SSH, FTP, HTTP and debug tools)
  python/            # exercises and small helpers
  mininet/           # topologies and scenarios
  docs/              # lab notes and a CLI cheat sheet
  tests/             # smoke test and expected output snippets
  artifacts/         # generated logs, validation summary and optional pcap (created at runtime)
  pcap/              # captures created by scripts/capture.sh
  certs/             # generated self-signed TLS certificate for the HTTPS exercise
```

---


## Make targets reference

The following targets are intended for normal student use (all targets are defined in the Makefile):

| Target | Purpose | Requires sudo |
|---|---|---|
| `make setup` | Create `.venv`, install Python packages and prepare directories | No |
| `make verify` | Verify tools and file structure | No |
| `make docker-up` | Start the Docker stack (HTTP, DNS, SSH and FTP) | No (unless Docker requires it) |
| `make docker-health` | Show service status and health summary | No |
| `make docker-down` | Stop the Docker stack | No |
| `make dns-test` | Query the custom DNS server on UDP/5353 | No |
| `make ssh-test` | Demonstrate SSH client behaviour (Paramiko) | No |
| `make ftp-test` | Demonstrate FTP control connection behaviour | No |
| `make https-test` | Run the local HTTPS demo | No |
| `make rest-test` | Run the REST maturity demo | No |
| `make capture` | Capture traffic to `artifacts/demo.pcap` | Yes (recommended) |
| `make run-all` | Full automated pipeline and artefacts | No (pcap is empty without sudo) |
| `make smoke-test` | Quick validation (structure plus basic runs) | No |
| `make clean` | Remove temporary artefacts | No |
| `make reset` | Aggressive cleanup (includes Docker) | No (unless Docker requires it) |

Notes:
- If you are not in the `docker` group, Docker commands may require `sudo`.
- `make run-all` runs successfully without sudo but capture may be empty.

## Quick start

### 1) Clone and set permissions

```bash
# Example (sparse checkout)
cd ~
git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK10
cd WEEK10
git sparse-checkout set WEEK10
shopt -s dotglob
mv WEEK10/* . && rmdir WEEK10

# Ensure scripts are executable
find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

### 2) Create the Python environment

```bash
make setup
```

This will:

- Create a local virtual environment in `.venv/`
- Install Python packages from `requirements.txt`
- Generate a self-signed TLS certificate into `certs/` (for the HTTPS exercise)

### 3) Verify the environment

```bash
make verify
```

### 4) Run the complete automated demonstration

```bash
make run-all
```

This target:

- Starts the Docker stack
- Executes basic DNS, HTTP, SSH and FTP tests
- Produces `artifacts/demo.log`, `artifacts/validation.txt` and (when possible) `artifacts/demo.pcap`

---

## Part A — Docker network services laboratory

The Docker lab is defined in `docker/docker-compose.yml`. It provides:

- `web` — a simple HTTP server (`python -m http.server`) on port **8000**
- `dns-server` — a small authoritative DNS server on UDP port **5353**
- `ssh-server` — OpenSSH server on port **2222** (host) → 22 (container)
- `ssh-client` — a Paramiko client that connects to `ssh-server`
- `ftp-server` — a pyftpdlib-based FTP server on port **2121**
- `debug` — diagnostic tools (curl, dig, lftp, tcpdump)

### Start and stop

```bash
make docker-up
make docker-health
make docker-down
```

### HTTP (port 8000)

From the host:

```bash
curl -v http://localhost:8000/
curl -v http://localhost:8000/hello.txt
```

Key observations:

- HTTP is plaintext over TCP
- You can correlate requests with TCP segments in a capture

### Custom DNS (UDP port 5353)

The DNS server provides static A records (examples):

- `myservice.lab.local` → `10.10.10.10`
- `api.lab.local` → `10.10.10.20`
- `web.lab.local` → `172.20.0.10`

Run:

```bash
make dns-test
```

Key observations:

- DNS is usually UDP (connectionless)
- A DNS reply can be analysed by inspecting the header, question and answer sections

### SSH (host port 2222)

From the host:

```bash
ssh -p 2222 labuser@localhost
# password: labpass
```

Or run the containerised Paramiko demo:

```bash
make ssh-test
```

Key observations:

- SSH negotiates algorithms and keys during the handshake
- Payload is encrypted after key exchange (unlike HTTP)

### FTP (host port 2121)

Run the basic Python ftplib test:

```bash
make ftp-test
```

Or use an interactive client:

```bash
lftp -u labftp,labftp -p 2121 localhost
```

Key observations:

- FTP is an instructive example of multi-channel protocols
- Active vs passive mode interacts with NAT and firewalls

---

## Part B — Packet capture and traffic analysis

To capture traffic, you need `tcpdump` or `tshark` and sufficient privileges.

```bash
sudo make capture
```

Captures are written to `pcap/` by default. The automated demo may also create a
small capture in `artifacts/demo.pcap` when it can obtain capture privileges.

For quick inspection:

```bash
tshark -r pcap/week10_capture_*.pcap -q -z conv,tcp
```

---

## Part C — Python exercises

### Exercise 10.1 — HTTPS + CRUD REST API

A minimal HTTPS server is implemented in:

- `python/exercises/ex_10_01_https.py`

Selftest:

```bash
make https-test
```

Run the server (default port 8443):

```bash
. .venv/bin/activate
python python/exercises/ex_10_01_https.py serve --host 0.0.0.0 --port 8443
```

Interact with it from another terminal:

```bash
# Self-signed certificate, so use -k for lab work
curl -k https://localhost:8443/api/resources
curl -k -X POST https://localhost:8443/api/resources \
  -H 'Content-Type: application/json' \
  -d '{"name":"example","value":123}'
```

What to focus on:

- TLS handshake and certificate validation
- Correct HTTP status codes for CRUD operations

### Exercise 10.2 — REST maturity levels

Implemented in:

- `python/exercises/ex_10_02_rest_levels.py`

Selftest:

```bash
make rest-test
```

Run the server:

```bash
. .venv/bin/activate
python python/exercises/ex_10_02_rest_levels.py serve --host 127.0.0.1 --port 5000
```

Browse or query endpoints:

- `http://127.0.0.1:5000/` (index)
- `/level0/service` (RPC style)
- `/level1/users/...` (resources + action paths)
- `/level2/users/...` (verbs + status codes)
- `/level3/users/...` (adds links)

---

## Part D — Mininet topologies

Mininet exercises require root privileges.

### Base routed topology

```bash
sudo make mininet-cli
```

This launches a small routed topology (two subnets separated by a Linux router).
You can validate end-to-end reachability with `ping`, inspect routes and capture
packets on interfaces.

### Topology with simple services

```bash
sudo make mininet-services
```

This topology starts lightweight demo services (HTTP, UDP DNS-like replies and
TCP banners) directly inside Mininet hosts.

### Automated Mininet smoke test

```bash
sudo make mininet-test
```

---


## Laboratory checklist

Use the following checklist as a structured path through the practical session.
If you can justify each observation, you are ready for the related exercise
questions.

### HTTP service

1. Start the Docker stack (`make docker-up`).
2. Fetch the web page and a text resource:

   ```bash
   curl -v http://localhost:8000/
   curl -v http://localhost:8000/hello.txt
   ```

3. Identify:
   - The HTTP status code and headers (Content-Type, Content-Length)
   - Whether the server closes the connection or keeps it alive

### DNS service

1. Query a Docker service name (`web`) using Docker’s embedded DNS.
2. Query the custom server on UDP/5353.
3. Compare:
   - Transport (UDP)
   - Message pattern (single request, single response)
   - Failure semantics (empty answer section vs NXDOMAIN)

### SSH service

1. Connect from the host using OpenSSH:

   ```bash
   ssh -p 2222 labuser@localhost
   ```

2. Observe:
   - Host key prompt (first connection)
   - Authentication method (password)
   - A remote command run via the Paramiko client (`make ssh-test`)

### FTP service

FTP is useful pedagogically because it illustrates *multi-connection* protocols.
Check that you can explain the difference between:

- The control connection (commands and responses)
- The data connection (directory listing and file transfer)

The provided server uses a passive port range `30000–30009`. This is intentional
so that you can see extra connections in packet captures.

---


## Laboratory tasks and expected observations

This section describes what you should actively look for when running the laboratory.

### Task 1 — HTTP service behaviour

1. Start the stack:

```bash
make docker-up
make docker-health
```

2. Query the HTTP service:

```bash
curl -v http://localhost:8000/
curl -v http://localhost:8000/hello.txt
```

What to observe:

- `HTTP/1.0` or `HTTP/1.1` in the response line (depending on the server implementation)
- response headers and content length
- a plain TCP connection visible in packet captures

### Task 2 — DNS over UDP (custom authoritative server)

Run:

```bash
make dns-test
```

Optional manual queries:

```bash
dig @127.0.0.1 -p 5353 myservice.lab.local A +noall +answer
dig @127.0.0.1 -p 5353 does-not-exist.lab.local A +noall +comments
```

What to observe:

- UDP request/response pairs
- record name, record type, TTL and response code
- how `NXDOMAIN` differs from a missing answer section

### Task 3 — SSH is encrypted application data

Run:

```bash
make ssh-test
```

What to observe:

- TCP connection establishment succeeds when the port is open
- after the SSH handshake, payload is encrypted and not visible as plaintext in captures
- authentication failure is a protocol outcome, not a connectivity failure

### Task 4 — FTP control and data channel implications

Run:

```bash
make ftp-test
```

What to observe:

- FTP uses a control connection for commands and responses
- in real deployments, data transfer behaviour involves additional connections and ports
- this is why FTP is historically sensitive to NAT and firewall policies

### Task 5 — HTTPS (TLS) local selftest

Run:

```bash
make https-test
```

What to observe:

- a TLS handshake occurs before any application data is exchanged
- certificate validation fails by default for self-signed certificates
- insecure client modes exist for lab purposes but are not safe defaults

### Task 6 — REST maturity levels

Run:

```bash
make rest-test
```

What to observe:

- Level 0: RPC style interactions over HTTP
- Level 1: resources appear as distinct URIs
- Level 2: semantics of HTTP methods and status codes are respected
- Level 3: hypermedia links are present for discoverability

### Task 7 — Evidence with tshark

If you captured traffic:

```bash
sudo make capture
```

Use tshark filters to extract evidence:

```bash
# DNS
tshark -r artifacts/demo.pcap -Y "udp.port==5353" -T fields -e dns.qry.name -e dns.flags.rcode

# HTTP
tshark -r artifacts/demo.pcap -Y "tcp.port==8000 && http" -T fields -e http.request.method -e http.host -e http.request.uri

# SSH and FTP (TCP only)
tshark -r artifacts/demo.pcap -Y "tcp.port==2222 || tcp.port==2121" -T fields -e tcp.srcport -e tcp.dstport
```

Interpretation guidance:

- you should be able to show at least one DNS query and its response
- you should show at least one HTTP request and response
- for SSH, you should explain why you cannot see the command content after the handshake

## Packet capture analysis with tshark

If you captured traffic with `make capture` (or `sudo ./scripts/capture.sh`), you
can extract key events with `tshark`.

Examples:

```bash
# DNS queries sent to the custom server

tshark -r pcap/week10_capture.pcap -Y "udp.port==5353" -T fields -e frame.time -e ip.src -e dns.qry.name

# TCP connection attempts to SSH and FTP

tshark -r pcap/week10_capture.pcap -Y "tcp.flags.syn==1 && tcp.flags.ack==0" -T fields -e frame.time -e ip.dst -e tcp.dstport

# HTTP requests to the demo web service

tshark -r pcap/week10_capture.pcap -Y "http.request" -T fields -e frame.time -e ip.src -e http.host -e http.request.method -e http.request.uri
```

Interpretation questions (typical exam style):

- Where do you see the TCP three-way handshake and how does it differ from DNS?
- Why does FTP create additional TCP flows compared to HTTP?
- In which packets do you see application-layer metadata (Host header, DNS name, SSH banner)?

---

## Optional extension: SOAP

SOAP is part of the Week 10 syllabus but is not implemented in this starter kit.
As an extension, you can:

- Implement a minimal SOAP endpoint (for example using Flask)
- Compare message structure and error handling with the REST exercises
- Capture and annotate SOAP XML payloads in Wireshark

## Troubleshooting

- **Docker permission denied:** ensure your user is in the `docker` group or run Docker commands with `sudo`.
- **Port already in use:** check with `ss -ltnup | grep -E ':(8000|2121|2222|8443|5000)'` and stop the conflicting process.
- **Self-signed certificate warnings:** expected for the lab. Use `curl -k` for quick tests and discuss why this is unsafe in production.
- **Captures are empty:** you likely ran capture commands without the required privileges.

---

## Licence

MIT (see repository root).

## Scripts reference

The Makefile is the recommended interface. Each target wraps one of these scripts:

| Script | Used by | Description |
|---|---|---|
| `scripts/setup.sh` | `make setup` | Environment preparation (Python, directories and certificates) |
| `scripts/verify.sh` | `make verify` | Environment verification and structure checks |
| `scripts/run_all.sh` | `make run-all` | Automated demo, validation and artefact generation |
| `scripts/capture.sh` | `make capture` | Packet capture helper (tcpdump based) |
| `scripts/cleanup.sh` | `make clean`, `make reset` | Cleanup routines (safe and reset modes) |

## Suggested report template (short form)

Include the following in your submission:

1. **Environment**: OS version, Python version, Docker version
2. **Commands executed**: the exact Make targets used
3. **Results summary**: paste `artifacts/validation.txt`
4. **Protocol evidence**:
   - DNS: one query and response, include filter and extracted fields
   - HTTP: one request and response, include filter and extracted fields
   - SSH: show TCP connection and explain encryption visibility limits
   - FTP: explain control channel observations and expected data channel behaviour
5. **Discussion**:
   - what broke when a service was stopped
   - what changes when capture is not run with sudo
6. **Conclusion**: concise, evidence driven conclusions
