# CLI Cheatsheet — Week 8

Quick reference for commands used in the HTTP server and reverse proxy laboratory.

> Run commands from the `WEEK8` directory, or use `make -C ~/WEEK8 <target>` from anywhere.

---

## Make targets

### Setup and verification

```bash
make setup
make verify
make help
```

### Demos

```bash
make demo-http
make demo-proxy
make run-demo
make run-all
make run-all-quick
```

### Manual servers (foreground)

```bash
make http-server    # HTTP server on :8080
make backend-a      # backend A on :9001
make backend-b      # backend B on :9002
make proxy-server   # reverse proxy on :8888
```

### Captures and analysis

```bash
make capture
make capture-handshake
make capture-proxy
make analyse
```

### Tests

```bash
make smoke-test
make test-ex1
make test-ex2
make test-all
```

### Cleanup

```bash
make kill-servers
make clean
make reset
```

---

## Curl examples

### HTTP server (port 8080)

```bash
curl -v http://localhost:8080/
curl -v http://localhost:8080/hello.txt
curl -v http://localhost:8080/not-found
```

### Reverse proxy (port 8888)

```bash
# Show the selected backend via response headers
for i in {1..6}; do
  curl -sS -D - -o /dev/null http://localhost:8888/ | grep -E '^(X-Served-By|X-Backend|HTTP/)'
done
```

---

## Traffic capture tips

> Capture targets may require `sudo`.

```bash
# Inspect listening ports
ss -ltnp | grep -E ':(8080|8888|9001|9002)\b'

# Tail logs produced by automated runs
tail -n 50 artifacts/demo.log
```

---

## Safety notes (lab context)

- Keep servers bound to `127.0.0.1` unless you explicitly need remote access.
- Treat directory traversal attempts as a test case and ensure the server rejects them.
