# Starterkit Week 14 — Integrated Review & Project Evaluation

**Course:** Computer Networks / Networking  
**Semester:** Year 3, Sem. 2 — Business Informatics (CSIE/ASE)  
**Version:** 2025-12-31  
**Code Licence:** MIT | **Course Materials Authors:** Hypotheticalandrei & Revolvix

---


## 🚀 Quick Clone & Setup

To clone **only this week's content** directly into `~/WEEK14` and make all scripts executable, run the following commands:

### Option A: One-liner (recommended)

```bash
cd ~ && git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK14 && cd WEEK14 && git sparse-checkout set WEEK14 && shopt -s dotglob && mv WEEK14/* . && rmdir WEEK14 && find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

### Option B: Step-by-step (for understanding)

```bash
# 1. Navigate to home directory
cd ~

# 2. Clone repository with sparse checkout (downloads only metadata initially)
git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK14

# 3. Enter the cloned directory
cd WEEK14

# 4. Configure sparse checkout to fetch only WEEK14
git sparse-checkout set WEEK14

# 5. Move contents up one level (flatten structure)
shopt -s dotglob
mv WEEK14/* .
rmdir WEEK14

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
cd ~ && mkdir -p WEEK14 && cd WEEK14 && curl -L https://github.com/antonioclim/netEN/archive/refs/heads/main.tar.gz | tar -xz --strip-components=2 netEN-main/WEEK14 && find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

### Verify Installation

After cloning, verify that scripts are executable:

```bash
cd ~/WEEK14
ls -la scripts/*.sh      # Should show 'x' permission
file scripts/*.sh        # Should show "shell script"
./scripts/setup.sh --help 2>/dev/null || head -5 scripts/setup.sh
```

---


## Quickstart (under 2 minutes)

```bash
# 0) In a Linux VM (Ubuntu/Debian CLI), from the kit root:
cd starterkit_week_14

# 1) Install dependencies (Mininet, OVS, tshark, utilities)
sudo bash scripts/setup.sh

# 2) Verify that the environment is OK
bash tests/smoke_test.sh

# 3) Run the complete automated demo
make run-demo

# 4) Check the generated artefacts
ls -la artifacts/

# 5) Analyse the pcap offline
tshark -r artifacts/demo.pcap -q -z conv,tcp

# 6) Complete cleanup
make clean
```

---


## What this kit demonstrates

1. **Compact Mininet Topology:**  
   `client ↔ switch1 ↔ switch2 ↔ [app1, app2]` + `switch1 ↔ lb`

2. **Load Balancer / Reverse Proxy Pattern:**  
   The client sends HTTP requests to `lb:8080` (10.0.14.1:8080); the proxy distributes them round-robin to backends (`app1:8080`, `app2:8080` = 10.0.14.100:8080, 10.0.14.101:8080).

3. **Diversified Traffic:**  
   - ICMP (ping) for basic connectivity  
   - TCP echo (simple server/client)  
   - HTTP (multiple requests, distribution observation)

4. **Capture and Analysis:**  
   - `tcpdump` on the lb interface → pcap  
   - `tshark` post-processing: IP/TCP conversations, HTTP requests, handshakes

5. **Verifiable Artefacts:**  
   - `artifacts/demo.pcap` (Mininet capture)
   - `artifacts/demo.log` (consolidated log)
   - `artifacts/validation.txt` (verification checklist)
   - `artifacts/tshark_summary.txt`  
   - `artifacts/report.json` (summary)  
   - Individual logs per component

---


## Minimum Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | Ubuntu 20.04+ / Debian 11+ | Ubuntu 22.04 Server (CLI) |
| Python | 3.8+ | 3.10+ |
| RAM | 2 GB | 4 GB |
| vCPU | 1 | 2 |
| Disk | 10 GB | 15 GB |
| Access | sudo | root |

**Required Packages** (automatically installed by `setup.sh`):  
`mininet`, `openvswitch-switch`, `tcpdump`, `tshark`, `iproute2`, `netcat-openbsd`, `curl`, `apache2-utils`

---


## Kit Structure

```
starterkit_week_14/
├── README.md                    # this file
├── Makefile                     # automation (setup, run-demo, run-lab, etc.)
├── requirements.txt             # Python dependencies
├── project_config.json          # configuration for verification harness
│
├── scripts/
│   ├── setup.sh                 # package installation + configuration
│   ├── run_all.sh               # complete automated demo
│   ├── cleanup.sh               # stop processes + Mininet cleanup
│   ├── capture.sh               # standalone tcpdump capture start
│   └── verify.sh                # environment and dependency verification
│
├── python/
│   ├── apps/
│   │   ├── backend_server.py    # simple HTTP server (backend)
│   │   ├── lb_proxy.py          # load balancer / reverse proxy
│   │   ├── http_client.py       # HTTP client with logging
│   │   ├── tcp_echo_server.py   # TCP echo server
│   │   ├── tcp_echo_client.py   # TCP echo client
│   │   └── run_demo.py          # automated demo orchestrator
│   ├── utils/
│   │   ├── net_utils.py         # network utilities
│   │   └── __init__.py
│   └── exercises/
│       ├── ex_14_01.py          # review drills (quiz)
│       ├── ex_14_02.py          # project verification harness
│       └── ex_14_03.py          # advanced exercises (challenge)
│
├── mininet/
│   ├── topologies/
│   │   └── topo_14_recap.py     # topology: cli, lb, app1, app2
│   └── scenarios/
│       └── scenario_14_tasks.md # laboratory tasks
│
├── docker/
│   ├── README.md                # Docker guide (optional)
│   ├── Dockerfile               # minimal image
│   └── docker-compose.yml       # orchestration
│
├── pcap/
│   └── sample_http.pcap         # example pcap for offline analysis
│
├── docs/
│   ├── curs.md                  # lecture material (Markdown)
│   ├── seminar.md               # seminar material (Markdown)
│   ├── lab.md                   # laboratory guide (Markdown)
│   ├── checklist.md             # teaching staff checklist
│   └── rubrici.md               # evaluation criteria
│
├── slides/
│   ├── curs_slides_outline.txt  # lecture slides outline
│   └── seminar_slides_outline.txt # seminar slides outline
│
├── tests/
│   ├── smoke_test.sh            # quick environment checks
│   └── expected_outputs.md      # reference outputs
│
├── configs/
│   └── sysctl.conf              # kernel tuning (optional)
│
└── assets/
    ├── style.css                # common HTML style
    └── logo.svg                 # minimal logo
```

---


## Makefile — Main Commands

| Command | Description |
|---------|-------------|
| `make setup` | Installs OS + Python dependencies |
| `make run-demo` | Runs the complete demo (Mininet + traffic + pcap) |
| `make run-lab` | Starts topology interactively (Mininet CLI) |
| `make capture` | Starts only tcpdump capture |
| `make verify` | Verifies environment and dependencies |
| `make clean` | Stops processes, cleans Mininet |
| `make reset` | Clean + deletes artefacts |

---


## Quick Laboratory Guide

### Step 0: Setup
```bash
make setup
make verify
```

### Step 1: Automated Demo
```bash
make run-demo
```
Check `artifacts/` for pcap, logs, JSON report.

### Step 2: Offline Analysis
```bash
# IP Conversations
tshark -r artifacts/demo.pcap -q -z conv,ip

# HTTP Requests
tshark -r artifacts/demo.pcap -Y "http.request" \
  -T fields -e ip.src -e ip.dst -e http.request.uri

# TCP Handshakes (SYN)
tshark -r artifacts/demo.pcap -Y "tcp.flags.syn==1 && tcp.flags.ack==0"
```

### Step 3: Modifications (exercises)
- **T1:** Stop a backend and observe lb behaviour (502/errors)
- **T2:** Add delay on a link in the topology and measure latency
- **T3:** Modify the number of HTTP requests and observe distribution

### Step 4: Report
Complete `docs/REPORT_TEMPLATE.md` with your conclusions.

---


## Troubleshooting (Top 10)

| Problem | Solution |
|---------|----------|
| `mn: command not found` | Run `make setup` |
| `Permission denied` | Use `sudo` or run as root |
| OVS does not start | `sudo systemctl restart openvswitch-switch` |
| Port 8080 occupied | `sudo ss -lntp \| grep 8080` + `kill` PID |
| pcap empty | Verify that the demo ran completely; re-run |
| tshark missing | `sudo apt install tshark` |
| Mininet "dirty" | `sudo mn -c` + `make clean` |
| Leftover processes | `sudo pkill -f backend_server` |
| DNS not working | Use IP addresses directly in lab |
| ab missing | `sudo apt install apache2-utils` |

---


## Project Evaluation — What to Bring

1. **README.md** clear: how to install, start, test, clean
2. **Demo plan:** steps + commands + expected output
3. **pcap Capture** (1-2 files) + short interpretation (3-5 lines)
4. **report.json** from harness (`python/exercises/ex_14_02.py`)
5. **Answers** to 3-5 defence questions

---


## Bibliography & Standards

- Kurose, J. F., & Ross, K. W. (2017). *Computer Networking: A Top-Down Approach* (7th ed.). Pearson.
- RFC 791 (IP), RFC 793 (TCP), RFC 768 (UDP), RFC 2616/7230 (HTTP/1.1)
- Lantz, B., et al. (2010). *A network in a laptop: Rapid prototyping for SDN*. HotNets.

---


**Note:** The kit is designed for **reproducibility** and audit (artefacts + explicit commands), not for maximum performance.
