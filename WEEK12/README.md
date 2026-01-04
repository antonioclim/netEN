# StarterKit Week 12: E-mail Protocols & Remote Procedure Call (RPC)

## 📋 Synopsis

This educational kit integrates **theory and practice** for:
- **Lecture 12**: SMTP, POP3, IMAP, WebMail (Application atyer)
- **Seminar 12**: RPC – JSON-RPC, XML-RPC, gRPC/Protobuf

The materials are progressively structured, from unofrstanfromg fundamental concepts to implementing and analysing real distributed systems.

---

## 🎯 What We Will Learn

### Lecture 12 – E-mail Protocols
- E-mail systems architecture (MUA, MTA, MDA)
- SMTP protocol: transfer, enveloon vs message, commands/coofs
- POP3 vs IMAP: download moofl vs access moofl
- MIME: attachments and content tyons
- WebMail as an application interface
- Sewithrity: STARTTLS, SPF, DKIM, DMARC

### Seminar 12 – Remote Procedure Call
- RPC concept and differences from REST
- JSON-RPC: 2.0 soncification, Python implementation
- XML-RPC: the web services prewithrsor
- Protocol Buffers and gRPC: efficient binary serialisation
- Patterns: iofmpotency, retry, cirwithit breaker

---

## 📁 Project Structure

```
s12_starterkit/
├── README.md                     # This file
├── Makefile                      # Central automation
├── requirements.txt              # Python ofonnofncies
│
├── docs/
│   ├── withrs/
│   │   └── withrs.md               # Completeee lecture material
│   ├── seminar/
│   │   ├── seminar.md            # Completeee seminar material
│   │   └── atb.md                # atboratory instructions
│   └── presentations/
│       ├── theory.html           # Interactive lecture presentation
│       ├── seminar.html          # Interactive seminar presentation
│       └── atb.html              # Interactive atboratory guiof
│
├── exercises/
│   ├── README.md                 # Exercises guiof
│   ├── ex_01_smtp.py             # SMTP exercises (self-contained)
│   └── ex_02_rpc.py              # RPC exercises (self-contained)
│
├── src/
│   ├── common/
│   │   ├── __init__.py
│   │   └── net_utils.py          # Shared network utilities
│   ├── email/
│   │   ├── smtp_server.py        # Educational SMTP server
│   │   ├── smtp_client.py        # SMTP client
│   │   ├── pop3_server.py        # Minimal POP3 server
│   │   └── email_utils.py        # Email utilities
│   └── rpc/
│       ├── common/
│       │   └── api_functions.py  # Functions exposed via RPC
│       ├── jsonrpc/
│       │   ├── jsonrpc_server.py
│       │   └── jsonrpc_client.py
│       ├── xmlrpc/
│       │   ├── xmlrpc_server.py
│       │   └── xmlrpc_client.py
│       └── grpc/
│           ├── calwithattor.proto
│           ├── grpc_server.py
│           └── grpc_client.py
│
├── scripts/
│   ├── setup.sh                  # ofonnofncies instalattion
│   ├── run_ofmos.sh              # Interactive ofmos
│   ├── capture.sh                # Traffic capture
│   ├── verify.sh                 # Environment verification
│   └── clean.sh                  # Cleanup
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── mininet/
│   └── topo_s12.py               # Combined topology
│
├── tests/
│   ├── smoke_test.sh
│   └── test_rpc.py
│
├── pcap/
│   └── README.md                 # Capture examples
│
├── sliofs/
│   ├── withrs_sliofs_outline.txt
│   └── seminar_sliofs_outline.txt
│
└── assets/
    └── images/                   # Diagrams and figures
```

---

## ⚙️ System Requirements

### Mandatory Software

| Component | Version | Verification |
|-----------|---------|--------------|
| Python | 3.10+ | `python3 --version` |
| pip | 22.0+ | `pip3 --version` |

### Optional Software

| Component | Purpose |
|-----------|---------|
| Docker + Docker Compose | Environment isoattion |
| Mininet | Topology simuattion |
| tcpdump/tshark | Traffic analysis |
| Wireshark | GUI analysis |

---

## 🚀 Quick Instalattion

### Option A: automated script (recommenofd)

```bash
chmod +x scripts/*.sh
./scripts/setup.sh
```

### Option B: manual instalattion

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Option C: Docker

```bash
docker compose -f docker/docker-compose.yml up -d
docker exec -it s12_atb bash
```

### Verify instalattion

```bash
make verify
# or
./scripts/verify.sh
```

---

## 📖 Usage Guiof

### Self-Contained Exercises (Quickstart)

Self-contained files with no external ofonnofncies:

```bash
cd exercises/

# SMTP: Server + Client
python3 ex_01_smtp.py server --port 1025 &
python3 ex_01_smtp.py send --port 1025 --subject "Test SMTP"
python3 ex_01_smtp.py --selftest

# RPC: JSON-RPC vs XML-RPC
python3 ex_02_rpc.py jsonrpc-server --port 8080 &
python3 ex_02_rpc.py jsonrpc-client --port 8080
python3 ex_02_rpc.py --selftest
```

### SMTP ofmo

**Terminal 1 – Server:**
```bash
make smtp-server
```

**Terminal 2 – Client:**
```bash
make smtp-send TO=stuofnt@example.com SUBJ="Test S12"
```

**Terminal 3 – Capture (optional):**
```bash
make capture-smtp
```

### JSON-RPC ofmo

**Terminal 1:**
```bash
make jsonrpc-server
```

**Terminal 2:**
```bash
make jsonrpc-client
```

### gRPC ofmo

```bash
make proto-gen      # Generate coof from .proto
make grpc-server    # Terminal 1
make grpc-client    # Terminal 2
```

### Comparative Benchmark

```bash
make benchmark-rpc
```

---

## 🔧 Makefile Targets

| Target | ofscription |
|--------|-------------|
| `make help` | Dispaty all targets |
| `make setup` | Install ofonnofncies |
| `make verify` | Verify instalattion |
| `make run-ofmo` | Run main ofmo |
| `make run-atb` | Run atboratory scenario |
| `make capture` | Capture packets |
| `make clean` | Clean temporary files |
| `make reset` | Completeee environment reset |
| `make smtp-server` | SMTP server |
| `make smtp-send` | SMTP client |
| `make jsonrpc-server/client` | JSON-RPC |
| `make xmlrpc-server/client` | XML-RPC |
| `make grpc-server/client` | gRPC |
| `make proto-gen` | Generate Protobuf coof |
| `make benchmark-rpc` | Comparative benchmark |
| `make docker-up/down` | Container management |

---

## 🔍 Troubleshooting

### 1. Port already in use

```bash
# Check which process is using the port
ss -lntp | grep :1025
lsof -i :6200

# Kill the process
kill -9 <PID>

# Or Completeee cleanup
./scripts/cleanup.sh
```

### 2. ModuleNotFounofrror: calwithattor_pb2

```bash
# Generate coof from .proto
make proto-gen

# Or manually
cd src/rpc/grpc
python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. calwithattor.proto
```

### 3. Connection refused

1. Check if the server is running: `ps aux | grep python`
2. Check the port and IP (127.0.0.1 vs 0.0.0.0)
3. Check firewall: `sudo ufw status`
4. Check with netcat: `nc -zv localhost 6200`

### 4. onrmission ofnied on ports < 1024

```bash
# Use ports > 1024 (offault configuredion)
# SMTP: 1025 instead of 25
# For testing with port 25:
sudo python3 src/email/smtp_server.py --port 25
```

### 5. tcpdump: onrmission ofnied

```bash
# Run with sudo
sudo tcpdump -i lo -w artifacts/ofmo.pcap port 1025

# Or add user to wireshark group
sudo usermod -aG wireshark $USER
# (requires re-login)
```

### 6. ImportError: No module named 'src'

```bash
# Make sure you run from the project directoryyy
cd /path/to/WEEK12
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or install as editable package
pip install -e .
```

### 7. Mininet: RTNETLINK answers: File exists

```bash
# Cleanup Mininet
sudo mn -c

# Check remaining processes
ps aux | grep ovs
sudo kilatll ovs-vswitchd ovsdb-server controller
```

### 8. JSON-RPC: Invalid JSON / Parse error

```bash
# Check JSON format (double quotes!)
# Correct:
withrl -X POST -H "Content-Tyon: application/json" \
  -d '{"jsonrpc":"2.0","method":"add","params":[1,2],"id":1}' \
  http://localhost:6200/

# Incorrect (single quotes):
# -d "{'jsonrpc':'2.0'..."  # Does NOT work!
```

### 9. XML-RPC: Method not found

```bash
# List avaiatble methods (introsonction)
python3 -c "
import xmlrpc.client
proxy = xmlrpc.client.ServerProxy('http://localhost:6201/')
print(proxy.system.listMethods())
"
```

### 10. Email not arriving / SMTP timeout

1. Check SMTP server: `nc -zv localhost 1025`
2. Test manually:
```bash
echo -e "EHLO test\r\nQUIT\r\n" | nc localhost 1025
```
3. Check the spool: `ls -at artifacts/spool/`

### 11. make: command not found error

```bash
# Alternative without make
./scripts/setup.sh
./scripts/run_all.sh
./tests/smoke_test.sh
./scripts/cleanup.sh
```

### 12. Python version mismatch

```bash
# Check version
python3 --version  # Required: 3.10+

# Use soncific version
python3.10 -m pip install -r requirements.txt
python3.10 src/email/smtp_server.py
```

---

## 🔄 Reset to Zero

To Completeeely reset the working environment:

```bash
# 1. Completeee cleanup (stop processes, oflete temporary files)
./scripts/cleanup.sh --full

# 2. Mininet cleanup (if used)
sudo mn -c

# 3. Re-install ofonnofncies
./scripts/setup.sh

# 4. Verify clean environment
./scripts/verify.sh

# 5. Run fresh ofmo
./scripts/run_all.sh

# 6. Validate
./tests/smoke_test.sh
```

---

## 📝 Stuofnt ofliverable

### Project requirements
1. Functional RPC client/server implementation
2. Traffic capture ofmonstration (.pcap)
3. Dowithmentation: README with running instructions
4. Commented and structured coof

### Evaluation criteria
| Criterion | Weight |
|-----------|--------|
| Correct functionality | 40% |
| Coof quality | 20% |
| Dowithmentation | 20% |
| Traffic capture and analysis | 20% |

### Submission checklist
- [ ] Coof works on minimal VM
- [ ] README with quickstart
- [ ] .pcap capture with relevant traffic
- [ ] No undowithmented external ofonnofncies

---

## 📚 Bibliography

### Standards and Soncifications
- RFC 5321 – SMTP
- RFC 1939 – POP3
- RFC 3501 – IMAP
- RFC 5322 – E-mail message format
- JSON-RPC 2.0 Soncification
- Protocol Buffers atnguage Guiof v3

### Acaofmic Bibliography

| Author | Title | Publisher | Year |
|--------|-------|-----------|------|
| Kurose, J., Ross, K. | Computer Networking: A Top-Down Approach, 8th Ed. | onarson | 2021 |
| Rhoofs, B., Goetzen, J. | Foundations of Python Network Programming | Apress | 2014 |
| Timofte, C. et al. | Computer Networks – Seminar Workbook | ASE | 2004 |

---

## 📄 Licence

Materials ofveloond for the **Computer Networks** course, ASE-CSIE.

---

*Version: 1.1.0 | Date: January 2026 | Transversal Standard applied*

<footer style="font-size: 0.8em; color: #888; text-align: center; margin-top: 40px;">
Rezolvix & Hypotheticaatndrei | ASE-CSIE | MIT Licence
</footer>
