# Expected Outputs

This file summarises what you should typically see after running the automated demo.

## Artefacts produced by `scripts/run_all.sh`

The runner writes into `artifacts/`:

### `artifacts/demo.log`
A plain-text log containing:

- timestamps for each step
- the Docker stack lifecycle (up and down)
- the round-robin probe (HTTP status plus `X-Served-By`)
- a health check

### `artifacts/demo.pcap`
A capture of HTTP traffic on TCP port 8080 **when capture privileges are available**. Depending on how your capture tool is configured, you should see:

- client → load balancer requests
- load balancer → backend requests
- HTTP responses

If capture permissions are missing, the PCAP may be missing or empty.

### `artifacts/validation.txt`
A small validation report containing:

- PASS/FAIL for each verification
- distribution statistics
- file size checks

## Expected verification results

### Round-robin distribution
The runner issues **12** requests to `/`. With three backends, a typical healthy run yields:

- Backend 1: 4 requests
- Backend 2: 4 requests
- Backend 3: 4 requests

Small deviations can occur if a request fails and is retried, or if you change the Nginx algorithm or weights.

### Load balancer health
Expected response at `http://localhost:8080/health`:

- `healthy`

## Useful test commands

```bash
# Verify artefacts
ls -la artifacts/

# Inspect the demo log
sed -n '1,200p' artifacts/demo.log

# Inspect the validation report
cat artifacts/validation.txt

# Quick header check (manual)
curl -s -D - -o /dev/null http://localhost:8080/ | grep -i x-served-by

# Analyse capture (if tshark is available)
tshark -r artifacts/demo.pcap -Y http
```
