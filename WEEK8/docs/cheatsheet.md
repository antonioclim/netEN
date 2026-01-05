# 📋 CLI Cheatsheet - Week 8

Quick reference for commands used in the HTTP Server and Reverse Proxy laboratory.

## 🔧 Make Commands

```bash
# Setup and verification
make setup              # Install dependencies
make verify             # Verify environment

# Automatic demo (produces artefacts)
make run-all            # Complete demo + capture
make run-all-quick      # Quick demo (without pcap)

# Manual demos
make demo-http          # HTTP server demo
make demo-proxy         # Reverse proxy demo

# Individual servers
make http-server        # HTTP server (port 8080)
make backend-a          # Backend A (port 9001)
make backend-b          # Backend B (port 9002)
make proxy-server       # Reverse proxy (port 8888)

# Captures
make capture-handshake  # TCP handshake capture
make capture-proxy      # Client→proxy→backend capture

# Tests and cleanup
make smoke-test         # Quick functionality test
make clean              # Clean temporary files
make kill-servers       # Stop all servers
make reset              # Complete reset
```

## 🐍 Python Scripts

```bash
# HTTP Server
python3 python/demos/demo_http_server.py --port 8080 --www www
python3 python/demos/demo_http_server.py --host 0.0.0.0 --port 80 --id backend-A
python3 python/demos/demo_http_server.py --selftest

# Reverse Proxy
python3 python/demos/demo_reverse_proxy.py --listen-port 8888 \
    --backends 127.0.0.1:9001,127.0.0.1:9002
python3 python/demos/demo_reverse_proxy.py --selftest
```

## 🌐 curl - HTTP Testing

```bash
# Simple GET
curl http://localhost:8080/

# With verbose headers
curl -v http://localhost:8080/

# Headers only (HEAD)
curl -I http://localhost:8080/

# Headers in output, body separate
curl -D - http://localhost:8080/ -o /dev/null

# POST with data
curl -X POST -d "key=value" http://localhost:8080/api

# JSON
curl -H "Content-Type: application/json" -d '{"key":"val"}' http://localhost:8080/api

# Follow redirects
curl -L http://localhost:8080/redirect

# Timeout
curl --connect-timeout 5 --max-time 10 http://localhost:8080/
```

## 📡 netcat - TCP Debug

```bash
# Simple TCP client
echo -e "GET / HTTP/1.1\r\nHost: localhost\r\n\r\n" | nc localhost 8080

# Simple TCP server
nc -l 9000

# Check open port
nc -zv localhost 8080

# Timeout
nc -w 5 localhost 8080
```

## 🔍 tcpdump - Packet Capture

```bash
# Capture on loopback
sudo tcpdump -i lo port 8080 -nn

# With ASCII content
sudo tcpdump -i lo port 8080 -nn -A

# With hex content
sudo tcpdump -i lo port 8080 -nn -X

# Save to file
sudo tcpdump -i lo port 8080 -nn -w capture.pcap

# Read from file
sudo tcpdump -r capture.pcap -nn

# Multiple ports
sudo tcpdump -i lo '(port 8080 or port 9001)' -nn

# Only SYN packets (new connections)
sudo tcpdump -i lo 'tcp[tcpflags] & tcp-syn != 0' -nn
```

## 📊 tshark - Wireshark CLI Analysis

```bash
# Live capture
sudo tshark -i lo -f "port 8080"

# HTTP filter
tshark -r capture.pcap -Y "http"

# Extract fields
tshark -r capture.pcap -Y "http" -T fields -e ip.src -e http.request.uri

# Statistics
tshark -r capture.pcap -q -z http,stat
tshark -r capture.pcap -q -z io,stat,1

# Follow TCP stream
tshark -r capture.pcap -q -z follow,tcp,ascii,0
```

## 🔌 Port Verification

```bash
# Processes on port
sudo lsof -i :8080
sudo fuser 8080/tcp

# Listening ports
netstat -tlnp | grep LISTEN
ss -tlnp

# Check connectivity
nc -zv localhost 8080

# Kill process on port
sudo fuser -k 8080/tcp
```

## 🐳 Docker (optional)

```bash
# Build and run
make docker-build
make docker-up
make docker-down
make docker-logs

# Manual
docker-compose -f docker/docker-compose.yml up -d
docker-compose -f docker/docker-compose.yml logs -f
docker-compose -f docker/docker-compose.yml down
```

## 📁 Directory Structure

```
WEEK8/
├── artifacts/          # Demo output (demo.log, demo.pcap, validation.txt)
├── python/
│   ├── demos/          # Complete demos
│   ├── exercises/      # Exercises to complete
│   └── utils/          # Common functions
├── scripts/
│   ├── setup.sh        # Environment configuration
│   ├── run_all.sh      # Automatic demo
│   └── cleanup.sh      # Cleanup
├── tests/
│   └── smoke_test.sh   # Quick test
├── www/                # Static files
└── docs/               # Documentation
```

## 🎯 Standard Ports (WEEK=8)

| Service | Port | Description |
|---------|------|-------------|
| HTTP | 8080 | Main HTTP server |
| Proxy | 8888 | Reverse proxy |
| Backend A | 9001 | Backend server 1 |
| Backend B | 9002 | Backend server 2 |
| Week Base | 5800 | WEEK_PORT_BASE |

## 🔒 Security Tips

```bash
# Do not expose servers on 0.0.0.0 in production
# Use 127.0.0.1 for local testing

# Check directory traversal
curl http://localhost:8080/../../../etc/passwd  # Should return 400

# Check HTTP methods
curl -X DELETE http://localhost:8080/  # Should return 405
```
