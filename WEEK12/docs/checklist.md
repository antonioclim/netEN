# Instructor Checklist – Week 12

## Email Protocols (SMTP, POP3, IMAP) & RPC (JSON-RPC, XML-RPC, gRPC)

---

## ☐ BEFORE LECTURE/SEMINAR

### Technical Preparation (30 min before)
- [ ] Verify VM/Docker container operation
- [ ] Run `make verify` in starterkit directoryy for environment validation
- [ ] Test educational SMTP server: `python3 src/email/smtp_server.py`
- [ ] Test RPC servers: `python3 src/rpc/jsonrpc/jsonrpc_server.py`
- [ ] Verify Wireshark/tshark installed and capture permissions
- [ ] Prepare multiple terminals (min. 3) for simultaneous demonstrations

### Pedagogical Preparation
- [ ] Recap content from S11 (DNS, SSH, FTP) – connection with SMTP
- [ ] Review key RFCs: RFC 5321 (SMTP), RFC 1939 (POP3), RFC 3501 (IMAP)
- [ ] Note 2-3 concrete industry examples (e.g. Gmail, Outlook, SendGrid)
- [ ] Prepare engagement questions for students
- [ ] Check evaluation rubrics and project criteria

### Materials
- [ ] Functional starterkit on demonstration machine
- [ ] HTML presentations accessible: theory.html, seminar.html, lab.html
- [ ] Word document with instructor notes available
- [ ] Pre-generated PCAP capture examples in /pcap (backup)

---

## ☐ DURING LECTURE (2h)

### Introduction (10 min)
- [ ] Contextualisation: "Why email protocols in the era of instant messaging?"
- [ ] Connection with previous weeks (TCP/S8, HTTP/S10, DNS/S11)
- [ ] Present objectives: what they will know and be able to do at the end

### Main Content – Email (50 min)
- [ ] Email architecture: MUA → MTA → MDA → MUA (diagram)
- [ ] **Key point**: Envelope vs Headers difference (source of spoofing)
- [ ] SMTP in detail: commands, response codes, completee session
- [ ] ⚠️ **Common pitfall**: students confuse MAIL FROM with Header From:
- [ ] Live demo: telnet session to educational SMTP server
- [ ] POP3 vs IMAP: comparative table, when to use each
- [ ] Email security: SPF, DKIM, DMARC – explain in simple terms

### Email Understanding Check (10 min)
- [ ] Question: "What happens if MAIL FROM differs from From: header?"
- [ ] Mini-quiz: identify the SMTP command for each action
- [ ] Question: "Why isn't POP3 suitable for multi-device access?"

### Break (10 min)

### Main Content – RPC (30 min)
- [ ] RPC concept: call local function, execution is remote
- [ ] JSON-RPC 2.0: request/response structure, standard error codes
- [ ] XML-RPC: verbose format, when it's still relevant (legacy)
- [ ] gRPC/Protobuf: performance advantages, streaming, microservices
- [ ] Comparative table: overhead, performance, use cases

### RPC Understanding Check (10 min)
- [ ] Question: "What's the difference between call and notification in JSON-RPC?"
- [ ] Question: "Why is gRPC faster than JSON-RPC?"

### Lecture Closing (10 min)
- [ ] Recap key points (max 5)
- [ ] Seminar preview: "You will implement and test practically"
- [ ] Homework: read RFC 5321 sections 3-4

---

## ☐ DURING SEMINAR (2h)

### Initial Setup (15 min)
- [ ] Verify all students have access to starterkit
- [ ] Run `make setup` on student machines
- [ ] Resolve environment issues (permissions, occupied ports)

### Experiment 1 – SMTP (30 min)
- [ ] Start SMTP server: `python3 src/email/smtp_server.py`
- [ ] Send email with client: `python3 src/email/smtp_client.py`
- [ ] Capture traffic: `make capture-smtp` (tshark in background)
- [ ] **Guided observation**: identify HELO, MAIL FROM, RCPT TO, DATA
- [ ] ⚠️ **Attention point**: verify that port 1025 is free

### Experiment 2 – JSON-RPC (25 min)
- [ ] Start server: `python3 src/rpc/jsonrpc/jsonrpc_server.py`
- [ ] Demo client: `python3 src/rpc/jsonrpc/jsonrpc_client.py --demo`
- [ ] Individual calls: add, subtract, multiply, divide
- [ ] Batch requests: demonstrate overhead reduction
- [ ] Capture and analysis: HTTP POST with JSON payload

### Experiment 3 – XML-RPC (20 min)
- [ ] Start server: `python3 src/rpc/xmlrpc/xmlrpc_server.py`
- [ ] Test with client: `python3 src/rpc/xmlrpc/xmlrpc_client.py`
- [ ] Introspection: system.listMethods()
- [ ] **Comparison**: observe XML vs JSON payload size

### Comparative Benchmark (15 min)
- [ ] Run: `make benchmark-rpc` or `scripts/benchmark_rpc.sh`
- [ ] Discuss results: why is JSON-RPC faster?
- [ ] Interpretation: serialisation/deserialisation overhead

### Individual Exercises (15 min)
- [ ] Exercise 1: Modify MAIL FROM and observe the difference
- [ ] Exercise 2: Add new method to RPC server
- [ ] Support for students encountering difficulties

### Seminar Closing (10 min)
- [ ] Collect feedback: what was clear, what wasn't
- [ ] Project reminder: notifications module or RPC API
- [ ] Preview S13: IoT and network security

---

## ☐ AFTER LECTURE/SEMINAR

### Immediately After (15 min)
- [ ] Save relevant PCAP captures for reference
- [ ] Note frequently asked questions from students
- [ ] Identify concepts that required additional explanations

### Within Next 48h
- [ ] Check progress on team projects
- [ ] Answer questions on forum/email
- [ ] Update materials if ambiguities appeared

### Evaluation Preparation
- [ ] Check rubrics for weekly contribution
- [ ] Prepare feedback for teams that delivered
- [ ] Note aspects for final evaluation

---

## Critical Attention Points

### Frequent Student Confusions
1. **Envelope vs Headers**: Many don't understand why they can be different
2. **POP3 deletes emails**: Not always, depends on configuredion
3. **RPC vs REST**: RPC is action-oriented, REST is resource-oriented
4. **gRPC requires HTTP/2**: Yes, it doesn't work on HTTP/1.1

### Anticipated Technical Issues
1. Port 25 blocked by ISP → we use 1025 in demo
2. Wireshark without permissions → run with sudo or configure group
3. Python 3.6+ required → check version at start
4. Firewall blocks traffic → temporarily disable or add exceptions

### Recommended Control Questions
- "What protocol does Gmail use when sending an email to Yahoo?"
- "How does the destination server verify the email isn't spoofed?"
- "Why does JSON-RPC use HTTP POST and not GET?"
- "In what situation would you use gRPC instead of REST?"

---

## Quick Access Resources

| Resource | Location |
|----------|----------|
| SMTP Server | `src/email/smtp_server.py` |
| SMTP Client | `src/email/smtp_client.py` |
| JSON-RPC Server | `src/rpc/jsonrpc/jsonrpc_server.py` |
| XML-RPC Server | `src/rpc/xmlrpc/xmlrpc_server.py` |
| Benchmark | `scripts/benchmark_rpc.sh` |
| Capture | `scripts/capture.sh` |
| Theory presentation | `docs/presentations/theory.html` |
| Seminar presentation | `docs/presentations/seminar.html` |
| Laboratory guide | `docs/presentations/lab.html` |

---

*Document generated for Week 12 – Computer Networks*
*Revolvix&Hypotheticalandrei*
