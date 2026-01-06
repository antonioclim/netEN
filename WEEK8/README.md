# WEEK 8 — Transport Layer (TCP/UDP/TLS) + HTTP Server + Reverse Proxy

Computer Networks — ASE-CSIE 2025–2026

---

## 0. Purpose and scope

This laboratory kit introduces practical aspects of the **transport layer** (TCP and UDP) and uses them to build and analyse application-layer behaviour via:

- a **minimal HTTP/1.1 server** implemented with Python sockets
- a **reverse proxy** that forwards requests to multiple backends using **round-robin** load balancing
- optional **traffic capture** and basic analysis (handshake, HTTP, proxy path)

The kit is designed to be:

- reproducible on a minimal **Ubuntu 24.04 LTS** VM
- runnable entirely from the CLI
- self-contained: all demos are started and stopped via `make` targets
- consistent: scripts, comments and user-facing messages are in **British English** (and the documentation avoids an Oxford comma)

---

## 1. Learning outcomes

After completing Week 8 you should be able to:

1. Explain how **TCP connection establishment** works (three-way handshake) and identify it in packet captures.
2. Trace a basic **HTTP/1.1 request–response exchange** and reason about headers and status codes.
3. Implement and evaluate a simple **reverse proxy** that:
   - receives a client connection
   - creates a new connection to a chosen backend
   - forwards the request and response between the two
4. Observe and justify how a proxy adds forwarding headers such as `X-Forwarded-For` and `X-Forwarded-Host`.
5. Distinguish between:
   - a single TCP connection (client ↔ server)
   - two distinct TCP connections in proxying (client ↔ proxy and proxy ↔ backend)

---

## 2. Directory contents (what matters most)

The verification step checks the presence of key kit files, notably:

- `demo_http_server.py`
- `demo_reverse_proxy.py`
- `www/` (static files served by the HTTP server)

(These are reported as present in the provided CLI logs.)【907:10†WEEK8 - CLI outputs.docx†L47-L54】

---

## 3. Prerequisites

### 3.1 Minimum environment

- Ubuntu **24.04 LTS**
- Python 3 (tested with **Python 3.12.x** in the provided logs)【907:10†WEEK8 - CLI outputs.docx†L15-L18】
- `curl` and `netcat`
- Optional but recommended for capture/analysis: `tcpdump` and `tshark`

### 3.2 One-time installation (recommended workflow)

The kit provides two convenience targets:

```bash
make setup
make verify
```

`make verify` prints an explicit checklist of tools and kit files【907:10†WEEK8 - CLI outputs.docx†L3-L57】 and `make setup` performs the installation checks and guidance【907:10†WEEK8 - CLI outputs.docx†L59-L100】.

---

## 4. Quick start (copy and paste)

### 4.1 Obtain the kit (sparse checkout)

If you are cloning the full course repository but only want Week 8, use the sparse workflow below (as in the provided session):

```bash
cd ~
git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK8
cd WEEK8
git sparse-checkout set WEEK8

shopt -s dotglob
mv WEEK8/* .
rmdir WEEK8

find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

This exact sequence appears in the CLI evidence.【907:9†WEEK8 - CLI outputs.docx†L1-L3】

### 4.2 Setup and verification

```bash
cd ~/WEEK8
make setup
make verify
```

### 4.3 Run the complete demonstration

```bash
cd ~/WEEK8
make run-all
```

If you only want a fast run without capture, use:

```bash
cd ~/WEEK8
make run-all-quick
```

Both targets are listed by `make help`【907:3†WEEK8 - CLI outputs.docx†L37-L48】.

---

## 5. Command reference

Run:

```bash
make help
```

The kit exposes the following high-level targets (as shown in the logs)【907:3†WEEK8 - CLI outputs.docx†L29-L111】:

### Configuration
- `make setup` — install or validate dependencies
- `make verify` — verify dependencies and kit files

### Demos
- `make run-all` — complete automatic demo
- `make run-all-quick` — automatic demo without packet capture
- `make run-demo` — complete demo (server and proxy)
- `make demo-http` — HTTP server demo (self-contained)
- `make demo-proxy` — proxy demo (self-contained)

### Laboratory (manual mode)
- `make run-lab` — start laboratory environment
- `make http-server` — HTTP server on port **8080**
- `make backend-a` — backend A on port **9001**
- `make backend-b` — backend B on port **9002**
- `make proxy-server` — reverse proxy on port **8888**

### Captures and analysis
- `make capture`
- `make capture-handshake`
- `make capture-proxy`
- `make analyze` — analyse the last capture (note: command name is `analyze` even though the description uses British spelling)【907:3†WEEK8 - CLI outputs.docx†L65-L74】

### Docker
- `make docker-build`
- `make docker-up`
- `make docker-down`
- `make docker-logs`

### Tests
- `make test-ex1`
- `make test-ex2`
- `make test-all`
- `make smoke-test`

### Cleanup
- `make clean`
- `make reset`
- `make kill-servers`

> Note: the help output explicitly warns that some commands require `sudo` due to `tcpdump`.【907:3†WEEK8 - CLI outputs.docx†L109-L111】

---

## 6. Ports and roles

The demos use fixed local ports:

| Component | Command | Port | Purpose |
|---|---:|---:|---|
| HTTP server (single instance) | `make http-server` | 8080 | Serve `www/` over HTTP/1.1 |
| Backend A | `make backend-a` | 9001 | Upstream server for the reverse proxy |
| Backend B | `make backend-b` | 9002 | Upstream server for the reverse proxy |
| Reverse proxy | `make proxy-server` | 8888 | Round-robin forwarding to backends |

In the automatic proxy demo, the proxy is shown as started on `0.0.0.0:8888` and the two backends on `127.0.0.1:9001` and `127.0.0.1:9002`.【907:0†WEEK8 - CLI outputs.docx†L67-L107】

---

## 7. Demo 1 — Minimal HTTP server (socket-based)

### 7.1 Automated version (recommended first)

```bash
cd ~/WEEK8
make demo-http
```

What it does (as shown in the logs):

1. Starts the server on **127.0.0.1:8080**【907:10†WEEK8 - CLI outputs.docx†L113-L116】
2. Performs a request to `/` (expect 200 OK)
3. Prints response headers including `X-Backend` and `X-Served-By`【907:0†WEEK8 - CLI outputs.docx†L17-L29】
4. Performs a request to a missing path (expect 404 Not Found)【907:0†WEEK8 - CLI outputs.docx†L35-L46】
5. Stops the server cleanly

### 7.2 Manual server mode (laboratory style)

Start the server:

```bash
cd ~/WEEK8
make http-server
```

In another terminal, test with curl:

```bash
curl -v http://localhost:8080/
curl -v http://localhost:8080/hello.txt
curl -v http://localhost:8080/not-found
```

In the sample output, curl first tries IPv6 (`::1`) and may show *Connection refused* before falling back to IPv4 (`127.0.0.1`) which succeeds.【907:4†WEEK8 - CLI outputs.docx†L41-L53】 This is normal on many systems when a service is bound only to IPv4.

If you want to avoid the IPv6 attempt, force IPv4:

```bash
curl -4 -v http://localhost:8080/
```

### 7.3 What to observe

- **HTTP status codes**:
  - `200 OK` for existing resources
  - `404 Not Found` for missing paths【907:4†WEEK8 - CLI outputs.docx†L65-L83】
- **Server-identifying headers** such as:
  - `Server: ASE-S8-Server/1.0`
  - `X-Backend: ...`
  - `X-Served-By: ...`【907:4†WEEK8 - CLI outputs.docx†L21-L26】

These headers are intentionally present so you can trace which component served the response.

---

## 8. Demo 2 — Reverse proxy with round-robin load balancing

You can run this demo in two ways:

- **Automated**: single command, prints a complete trace (recommended for the first run)
- **Manual**: four terminals, closer to a real lab workflow

### 8.1 Automated version (recommended first)

```bash
cd ~/WEEK8
make demo-proxy
```

This demo starts:

- Backend A on port 9001
- Backend B on port 9002
- Reverse proxy on port 8888, configured with a round-robin algorithm【907:0†WEEK8 - CLI outputs.docx†L67-L107】

Then it performs six requests through the proxy and prints an alternating sequence of backend selections. The logs also show that the proxy injects forwarding headers such as `X-Forwarded-For` and `X-Forwarded-Host`【907:2†WEEK8 - CLI outputs.docx†L1-L27】.

### 8.2 Manual version (four terminals)

This is the version where it is easiest to make a procedural mistake. The most important rule is:

> **Always run `make` from the kit directory (`~/WEEK8`) or use `make -C ~/WEEK8 …`.**

In the provided evidence, `make proxy-server` was executed from `~` and therefore failed with **“No rule to make target 'proxy-server'”**【907:1†WEEK8 - CLI outputs.docx†L51-L54】. When the proxy does not start, `curl` has nothing to talk to so you will not observe backend alternation.

#### Terminal 1 — Backend A

```bash
cd ~/WEEK8
make backend-a
```

#### Terminal 2 — Backend B

```bash
cd ~/WEEK8
make backend-b
```

#### Terminal 3 — Reverse proxy

```bash
cd ~/WEEK8
make proxy-server
```

You should see the proxy start on port 8888 (the automated demo shows this explicitly)【907:0†WEEK8 - CLI outputs.docx†L99-L107】.

#### Terminal 4 — Client requests through the proxy (observe alternation)

Use `curl` against **port 8888** (the proxy), not 8080 (the standalone server):

```bash
for i in {1..6}; do
  echo "Request $i"
  curl -sS -D - -o /dev/null http://127.0.0.1:8888/ \
    | grep -E '^(HTTP/|X-Backend:|X-Served-By:)'
  echo
done
```

Why this variant:
- `-sS` remains quiet on success but still shows errors, which avoids “nothing happens”
- `-D -` prints response headers so you can observe `X-Backend` values
- `-o /dev/null` suppresses the HTML body

### 8.3 What you should observe (and where)

#### (A) Backend alternation (A, B, A, B…)

In the automated demo, requests alternate between `backend-A` and `backend-B` and the response header `X-Backend` matches the selected backend【907:8†WEEK8 - CLI outputs.docx†L7-L46】.

#### (B) Proxy-added forwarding headers

The backend-side logs show that forwarded requests include:

- `X-Forwarded-For: 127.0.0.1`
- `X-Forwarded-Host: 127.0.0.1:8888`【907:8†WEEK8 - CLI outputs.docx†L13-L16】

#### (C) Two distinct TCP connections

Conceptually, each proxied request uses two separate connections:

1. client ↔ proxy (client connects to port 8888)
2. proxy ↔ selected backend (proxy connects to port 9001 or 9002)

You can validate this empirically with packet captures or by inspecting connection tables (`ss -tnp`) while running the demo.

---

## 9. Captures and analysis

The kit includes capture targets and an analysis target【907:3†WEEK8 - CLI outputs.docx†L65-L73】. Some capture commands require elevated privileges due to `tcpdump`【907:3†WEEK8 - CLI outputs.docx†L109-L111】.

Typical workflow:

```bash
cd ~/WEEK8

# capture the TCP handshake
sudo make capture-handshake

# or capture proxy traffic
sudo make capture-proxy

# analyse the last capture
make analyze
```

If you are unsure where captures are saved, search for `.pcap` files after running a capture target:

```bash
find . -maxdepth 2 -type f -name "*.pcap" -print
```

---

## 10. Tests

The kit defines the following test targets【907:3†WEEK8 - CLI outputs.docx†L89-L97】:

```bash
make test-ex1
make test-ex2
make test-all
make smoke-test
```

Use these after you modify code, especially if you work on the exercises rather than only running the demos.

---

## 11. Cleanup and reset

To stop running servers, remove temporary files and return to a clean state, use:

```bash
make kill-servers
make clean
```

If you need a full reset (including captures), use:

```bash
make reset
```

All three commands are listed in the kit help output【907:3†WEEK8 - CLI outputs.docx†L101-L107】.

---

## 12. Common mistakes and how to avoid them

### 12.1 “No rule to make target …”

If you run `make` from `~` instead of `~/WEEK8`, Make will not find the kit Makefile and you will see errors like:

- `make: *** No rule to make target 'proxy-server'. Stop.`【907:1†WEEK8 - CLI outputs.docx†L51-L54】
- `make: *** No rule to make target 'capture-handshake'. Stop.`【907:1†WEEK8 - CLI outputs.docx†L79-L82】

Fix:

```bash
cd ~/WEEK8
# or, without changing directory:
make -C ~/WEEK8 proxy-server
```

### 12.2 Typing `demo2` or `demo 2`

`demo2` is not a shell command. In the logs it fails as expected【907:1†WEEK8 - CLI outputs.docx†L15-L18】. Use:

- `make demo-proxy` for the automated reverse proxy demo
- or the manual four-terminal steps in Section 8.2

### 12.3 “Nothing happens” when testing with curl

Most often this is because:
- the proxy is not running (see 12.1), or
- you are using `curl -s` plus a `grep` that finds no matching header line

Use `curl -sS` and print headers with `-D -` as in Section 8.2.

---

## 13. Suggested laboratory exercises

1. **Handshake capture**: capture the TCP three-way handshake, identify SYN, SYN-ACK and ACK, then map them to the client and server ports.
2. **HTTP semantics**: modify `www/hello.txt`, then confirm that `Content-Length` changes accordingly.
3. **Proxy correctness**: add a backend C, extend the round-robin set and confirm the selection sequence.
4. **Failure handling**: stop backend B and observe how the proxy behaves. Propose improvements for resilience.

---

## 14. Licence and usage

Educational use only — Computer Networks course (ASE-CSIE).

