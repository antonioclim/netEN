# Expected Outputs - Week 8

This document describes the expected outputs for the automatic demo and verification tests.

## Generated Artefacts

After running `./scripts/run_all.sh`, the `artifacts/` directory should contain:

### artifacts/demo.log

Complete log of the demo execution. Contains:
- Timestamps for each operation
- HTTP test results (GET /, GET /not-found)
- Round-robin request distribution
- Error messages (if any)

**Partial example:**
```
[14:30:01] [INFO] Automatic demo started
[14:30:01] [INFO] Configuration: WEEK=8, HTTP_PORT=8080, PROXY_PORT=8888
[14:30:02] [STEP] [1/8] Checking preconditions...
[14:30:02] [INFO]   Preconditions OK
[14:30:03] [INFO]   HTTP server started on port 8080
[14:30:03] [INFO]   ✓ GET / → 200 OK
[14:30:03] [INFO]   ✓ GET /not-found → 404
```

### artifacts/validation.txt

Results of each test in structured format. Used by smoke_test.sh for validation.

**Format:**
```
PREREQS: PASS
HTTP_GET_ROOT: PASS
HTTP_GET_404: PASS
BACKENDS_START: PASS
PROXY_START: PASS
ROUND_ROBIN_BALANCED: PASS
X_REQUEST_ID: PASS
X_SERVED_BY: PASS
PCAP_GENERATED: PASS (1234 bytes)

===== SUMMARY =====
Timestamp: 2025-01-01 14:30:05
WEEK: 8
HTTP_PORT: 8080
PROXY_PORT: 8888
BACKENDS: 9001, 9002
DEMO_COMPLETED: SUCCESS
```

### artifacts/demo.pcap

Traffic capture (if tcpdump is available). Contains:
- TCP three-way handshake
- HTTP requests/responses
- Client→proxy→backend flow

**Analysis with tshark:**
```bash
tshark -r artifacts/demo.pcap -Y "http" -T fields -e ip.src -e http.request.uri
```

---

## HTTP Server Expected Output

### GET / → 200 OK

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 1234
Connection: close
Server: ASE-S8-Server/1.0
X-Backend: http-server

<!DOCTYPE html>
...
```

### GET /not-found → 404 Not Found

```http
HTTP/1.1 404 Not Found
Content-Type: text/html; charset=utf-8
Content-Length: 123
Connection: close
Server: ASE-S8-Server/1.0
X-Backend: http-server

<!DOCTYPE html>
<html><body><h1>404 - Not Found</h1><p>Resource does not exist.</p></body></html>
```

### GET /../../../etc/passwd → 400 Bad Request

```http
HTTP/1.1 400 Bad Request
Content-Type: text/plain; charset=utf-8
Content-Length: 12
X-Backend: http-server

Bad Request
```

---

## Reverse Proxy Expected Output

### Round-Robin Distribution

For 6 consecutive requests through the proxy:
```
Request 1: X-Served-By: backend-A
Request 2: X-Served-By: backend-B
Request 3: X-Served-By: backend-A
Request 4: X-Served-By: backend-B
Request 5: X-Served-By: backend-A
Request 6: X-Served-By: backend-B
```

### Added Headers

The proxy adds the following headers:
- `X-Forwarded-For: <client IP>`
- `X-Forwarded-Host: <original host>`
- `X-Forwarded-Proto: http`
- `Via: 1.1 ASE-S8-Proxy`
- `X-Request-ID: <uuid>`

---

## Validation Criteria

| Test | Criterion | Status |
|------|-----------|--------|
| Preconditions | Python 3, curl, kit files exist | PASS/FAIL |
| HTTP GET / | Status 200, body contains HTML | PASS/FAIL |
| HTTP GET 404 | Status 404 for non-existent resource | PASS/FAIL |
| Backend Start | Both backends respond | PASS/FAIL |
| Proxy Start | Proxy responds | PASS/FAIL |
| Round-Robin | Balanced distribution A/B | PASS/FAIL |
| X-Request-ID | Header present in response | PASS/FAIL |
| X-Served-By | Header identifies backend | PASS/FAIL |
| PCAP | File generated (if tcpdump available) | PASS/WARN |

---

*Material for Week 8, Computer Networks, ASE Bucharest*
