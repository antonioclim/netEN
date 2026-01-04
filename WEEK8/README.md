# 🌐 Week 8 - Transport Layer + HTTP Server + Reverse Proxy

**Computer Networks** | ASE Bucharest - CSIE | Business Informatics

---


## 🚀 Quick Clone & Setup

To clone **only this week's content** directly into `~/WEEK8` and make all scripts executable, run the following commands:

### Option A: One-liner (recommended)

```bash
cd ~ && git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK8 && cd WEEK8 && git sparse-checkout set WEEK8 && shopt -s dotglob && mv WEEK8/* . && rmdir WEEK8 && find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

### Option B: Step-by-step (for understanding)

```bash
# 1. Navigate to home directory
cd ~

# 2. Clone repository with sparse checkout (downloads only metadata initially)
git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK8

# 3. Enter the cloned directory
cd WEEK8

# 4. Configure sparse checkout to fetch only WEEK8
git sparse-checkout set WEEK8

# 5. Move contents up one level (flatten structure)
shopt -s dotglob
mv WEEK8/* .
rmdir WEEK8

# 6. Make all shell scripts and Python files executable
find . -type f -name "*.sh" -exec chmod +x {} \;
find . -type f -name "*.py" -exec chmod +x {} \;

# 7. Verify the setup
ls -la
ls -la scripts/
```

### Option C: Without Git history (lightweight)

If you don't need Git history and want the smallest possible download:

```bash
cd ~ && mkdir -p WEEK8 && cd WEEK8 && curl -L https://github.com/antonioclim/netEN/archive/refs/heads/main.tar.gz | tar -xz --strip-components=2 netEN-main/WEEK8 && find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

### Verify Installation

After cloning, verify that scripts are executable:

```bash
cd ~/WEEK8
ls -la scripts/*.sh      # Should show 'x' permission
file scripts/*.sh        # Should show "shell script"
./scripts/setup.sh --help 2>/dev/null || head -5 scripts/setup.sh
```

---


## 📋 Contents

- [What we will learn](#-what-we-will-learn)
- [Why it matters](#-why-it-matters)
- [Prerequisites](#-prerequisites)
- [Quick start](#-quick-start)
- [Kit structure](#-kit-structure)
- [Demos](#-demos)
- [Laboratory](#-laboratory)
- [Troubleshooting](#-troubleshooting)

---


## 📚 What we will learn

### Lecture (Theory)
- **Transport Layer** in the TCP/IP model
- **TCP**: Three-way handshake, flags, options (MSS, SACK, Window Scaling)
- **UDP**: Characteristics, use cases
- **TLS/DTLS**: Securing transport
- **QUIC**: The modern transport protocol

### Seminar/Laboratory (Practice)
- Implementing a **minimal HTTP server** with sockets
- Implementing a **reverse proxy** with round-robin load balancing
- **Traffic capture and analysis** with tcpdump/tshark
- Observing the **three-way handshake** in practice
- Understanding HTTP headers and modifying them

---


## 💡 Why it matters

As a programmer, you will constantly interact with networks:
- **REST APIs** - require understanding HTTP
- **Microservices** - load balancing, reverse proxy
- **Debugging** - tcpdump, Wireshark
- **Security** - TLS, certificates
- **Performance** - TCP optimisations, QUIC

This week builds the foundation for all of these.

---


## 📋 Prerequisites

### Required software
- Python 3.8+ (essential)
- curl (essential)
- netcat/nc (essential)
- tcpdump (recommended, for captures)
- Docker (optional, for advanced scenarios)

### Prior knowledge
- Week 5: IP addressing, subnetting
- Week 6-7: Routing protocols, NAT
- Python programming basics

---


## 🚀 Quick start

```bash
# 1. Verify the environment
make verify

# 2. Run setup (if something is missing)
make setup

# 3. Quick demo - HTTP Server
make demo-http

# 4. Full demo - Reverse Proxy with Round-Robin
make demo-proxy

# 5. See all available commands
make help
```

---


## 📁 Kit structure

```
starterkit_s8/
├── README.md                    # This file
├── Makefile                     # Automations (make help)
│
├── python/
│   ├── demos/
│   │   ├── demo_http_server.py  # Complete HTTP server, commented
│   │   └── demo_reverse_proxy.py # Reverse proxy with round-robin
│   ├── exercises/
│   │   ├── ex_01_http_server.py # Exercise: completee the TODOs
│   │   └── ex_02_reverse_proxy.py
│   └── utils/
│       └── net_utils.py         # Helper functions (HTTP parsing, etc.)
│
├── docs/
│   ├── curs/
│   │   └── c8_transport_layer.md
│   └── seminar/
│       ├── s8_explanation.md
│       └── s8_tasks.md
│
├── www/                         # Static files for the server
│   ├── index.html
│   ├── hello.txt
│   └── api/status.json
│
├── scenarios/                   # Demonstrative scenarios
│   ├── http-server/run.sh
│   ├── reverse-proxy/run.sh
│   ├── tcp-analysis/run.sh
│   └── tls-demo/run.sh
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── nginx/
│   ├── nginx.conf
│   └── conf.d/default.conf
│
├── scripts/
│   ├── setup.sh
│   └── cleanup.sh
│
├── tests/
│   └── smoke_test.sh
│
├── pcap/                        # Captures (generated)
└── slides/                      # Outline for presentations
```

---


## 🎮 Demos

### Demo 1: Minimal HTTP Server

```bash
# Terminal 1: Start the server
make http-server

# Terminal 2: Test with curl
curl -v http://localhost:8080/
curl -v http://localhost:8080/hello.txt
curl -v http://localhost:8080/not-found  # → 404
```

**What we observe:**
- HTTP request/response structure
- Headers added by the server (Content-Type, Content-Length)
- Status codes (200, 404, etc.)

### Demo 2: Reverse Proxy Round-Robin

```bash
# Terminal 1
make backend-a

# Terminal 2
make backend-b

# Terminal 3
make proxy-server

# Terminal 4: Test
for i in {1..6}; do
    curl -s http://localhost:8080/ -D - | grep X-Served-By
done
```

**What we observe:**
- Backend alternation (A, B, A, B...)
- The `X-Forwarded-For` header added by the proxy
- Two distinct TCP connections

### Demo 3: TCP Handshake Capture

```bash
make capture-handshake
```

**What we observe in the capture:**
- `[S]` - SYN (client initiates)
- `[S.]` - SYN-ACK (server accepts)
- `[.]` - ACK (client confirms)
- `[P.]` - PSH-ACK (HTTP data)
- `[F.]` - FIN-ACK (closure)

---


## 🔬 Laboratory

### Exercise 1: Complete HTTP Server

Open `python/exercises/ex_01_http_server.py` and completee the sections marked with `# TODO`:

```python
# TODO 1: Parse request line
# TODO 2: Validate HTTP method
# TODO 3: Directory traversal protection
# TODO 4: Build HTTP response
```

Test: `make test-ex1`

### Exercise 2: Complete Reverse Proxy

Open `python/exercises/ex_02_reverse_proxy.py`:

```python
# TODO 1: Select backend (round-robin)
# TODO 2: Modify X-Forwarded-For header
# TODO 3: Forward request to backend
# TODO 4: Handle errors (502 Bad Gateway)
```

Test: `make test-ex2`

---


## 🔧 Troubleshooting

### Port already in use

```bash
# Check what is using the port
sudo lsof -i :8080

# Stop all servers
make kill-servers
```

### Permission denied for tcpdump

```bash
# tcpdump requires sudo for capture
sudo tcpdump -i lo port 8080 -nn
```

### Python module not found

```bash
# Check the Python path
python3 -c "import sys; print(sys.path)"

# Run from the kit directory
cd starterkit_s8
python3 python/demos/demo_http_server.py
```

### curl: connection refused

```bash
# Check that the server is running
ps aux | grep python

# Check the port
netstat -tlnp | grep 8080
```

---


## 📖 Bibliography

| Reference | Description |
|-----------|-------------|
| RFC 793 | TCP (Transmission Control Protocol) |
| RFC 768 | UDP (User Datagram Protocol) |
| RFC 7230-7235 | HTTP/1.1 |
| RFC 8446 | TLS 1.3 |
| RFC 9000 | QUIC |
| Kurose & Ross | Computer Networking: A Top-Down Approach |

---


## 📝 Note for students

This kit contains:
- **Complete demos** - for observation and understanding
- **Exercises** - for active practice
- **Automations** - for productivity

Recommended approach:
1. Read the documentation in `docs/`
2. Run the demos and observe the output
3. Complete the exercises step by step
4. Experiment with your own variations

---


*Computer Networks - ASE Bucharest - CSIE*  
*Revolvix&Hypotheticalandrei*
