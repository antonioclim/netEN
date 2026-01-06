# Seminar 8 — Practical Tasks

This worksheet provides guided tasks for Week 8 (HTTP server and reverse proxy).
Use the `make` targets to ensure reproducible steps.

> Important: run commands from the `WEEK8` directory, or use `make -C ~/WEEK8 <target>`.

---

## Preparation (5–10 min)

1. Install and verify dependencies:

```bash
make setup
make verify
```

2. Open **four terminals** (or tabs) for the proxy exercise (Task 2).

---

## Task 1 — Minimal HTTP server (20–25 min)

### Task 1.1: Run the demo server

```bash
make demo-http
```

### Task 1.2: Manual requests with curl

Start the server:

```bash
make http-server
```

In a separate terminal, issue requests:

```bash
curl -v http://localhost:8080/
curl -v http://localhost:8080/hello.txt
curl -v http://localhost:8080/not-found
```

**Questions**
1. Which status code do you receive for `/` and why?
2. Which status code do you receive for `/not-found`?
3. Which headers identify the responding server?

Stop the server with Ctrl+C, or run:

```bash
make kill-servers
```

---

## Task 2 — Reverse proxy with round-robin (25–35 min)

### Task 2.1: Start the components (four terminals)

**Terminal 1:**

```bash
make backend-a
```

**Terminal 2:**

```bash
make backend-b
```

**Terminal 3:**

```bash
make proxy-server
```

### Task 2.2: Generate traffic through the proxy (Terminal 4)

Send six requests through the proxy port (`8888`):

```bash
for i in {1..6}; do
  curl -sS -D - -o /dev/null http://localhost:8888/ | grep -E '^(X-Served-By|X-Backend|HTTP/)'
done
```

**Questions**
1. Do you observe alternation between backend A and backend B?
2. Where can you see that the proxy adds `X-Forwarded-For`?
3. Why should there be two TCP connections in this scenario?

---

## Task 3 — Packet captures (15–20 min)

### Task 3.1: Capture a TCP three-way handshake

```bash
make capture-handshake
```

Open the produced `.pcap` in Wireshark or inspect with tshark:

```bash
tshark -r artifacts/handshake.pcap -Y "tcp.flags.syn==1"
```

### Task 3.2: Capture proxy traffic

```bash
make capture-proxy
```

Inspect the capture:

```bash
tshark -r artifacts/proxy_capture.pcap -Y "http"
```

---

## Task 4 — Validation (5–10 min)

```bash
make smoke-test
make test-all
```

---

## Cleanup

```bash
make kill-servers
make clean
```
