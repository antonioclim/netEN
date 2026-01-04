# =============================================================================
# FINAL DOCUMENTS — Week 12
# Email Protocols and RPC
# =============================================================================

## ALIGNMENT MAP

### Syllabus Topic → Lecture Sections → Seminar Sections → Kit Artefacts

| Syllabus Topic | Lecture | Seminar | Kit Artefacts |
|----------------|---------|---------|---------------|
| **Lecture 12: SMTP, POP3, IMAP, WebMail** | theory.html slides 1-28 | - | src/email/, docs/curs/curs.md |
| Email architecture (MUA/MTA/MDA) | Section 1 (slides 4-7) | - | smtp_server.py (simplified MTA implementation) |
| SMTP protocol | Section 2 (slides 8-13) | Lab Steps 1-3 | smtp_client.py, smtp_server.py |
| POP3 protocol | Section 3 (slides 14-17) | - | smtp_server.py (mailbox listing) |
| IMAP protocol | Section 4 (slides 18-21) | - | docs/curs.md (theory) |
| MIME and formatting | Section 5 (slides 22-24) | Exercise 5 | ex_01_smtp.py |
| Security (SPF/DKIM/DMARC) | Section 6 (slides 25-28) | - | docs/curs.md |
| **Seminar 12: RPC concepts, framework** | - | seminar.html | src/rpc/ |
| RPC concept | - | Tabs 1-2 | docs/seminar.md |
| JSON-RPC 2.0 | - | Tabs 3-4, Steps 4-5 | jsonrpc_server.py, jsonrpc_client.py |
| XML-RPC | - | Tabs 5-6, Step 6 | xmlrpc_server.py, xmlrpc_client.py |
| gRPC/Protobuf | - | Tab 7 | calculator.proto (introduction) |
| Protocol comparison | - | Tab 8, Step 7 | benchmark_rpc.sh |

---

## DECISION LOG (15 Bullet Points)

### Architecture and Structure

1. **Strict email vs RPC separation** — We kept separate directoryies `src/email/` and `src/rpc/` for pedagogical clarity, allowing students to focus on one topic at a time.

2. **Python without external frameworks for RPC** — We implemented JSON-RPC and XML-RPC using only `http.server` and standard libraries to demonstrate basic concepts without abstractions.

3. **Docker optional, not mandatory** — Docker configuredion is included but all demos also run without Docker, respecting the lightweight setup requirement in VirtualBox.

4. **Mininet only for demonstration topology** — We included a basic topology (`topo_email_rpc_base.py`) for visualisation, but main exercises do not depend on Mininet.

### Educational Content

5. **Envelope vs Headers explicitly highlighted** — This is one of the most frequent confusions, so we dedicated specific slides and exercises to this concept.

6. **Email security (SPF/DKIM/DMARC) included** — Although not explicitly appearing in the syllabus, it is essential for understanding modern email and protection against spoofing.

7. **JSON-RPC batch requests demonstrated** — Advanced but important feature for efficiency in real applications, included in exercises.

8. **gRPC only as introduction** — The protocol is complex and requires additional tooling; we included `.proto` and explanations, but completee implementation is marked as bonus.

### Technical Implementation

9. **Simplified educational SMTP server** — Our implementation accepts any email without real authentication to allow free experimentation, but we clearly document differences from production servers.

10. **Configurable logging in all servers** — `--verbose` / `--quiet` flag to control output level, useful both for debugging and for clean benchmarks.

11. **RPC error handling according to specification** — Standard JSON-RPC error codes (-32700, -32600, etc.) are implemented and documented.

12. **Pre-generated .pcap captures included** — `pcap/` folder contains examples for students who cannot run tshark locally.

### Evaluation and Exercises

13. **Graded exercises ★ to ★★★★** — Clear progression from simple (new RPC method) to complex (email relay), allowing differentiation by level.

14. **Email relay challenge** — Optional advanced exercise for students who want to deepen their understanding of email routing protocols.

15. **Detailed rubrics for self-evaluation** — Includes checklist and scores by criteria, allowing students to evaluate their progress before submission.

---

## ASSUMPTIONS LIST (8 Points)

1. **Python 3.10+ available** — Code tested on Python 3.10-3.12; earlier versions may have minor incompatibilities in type hints.

2. **Ports 1025, 8000, 8001 available** — Demos use these ports; if occupied, they can be modified via environment variables.

3. **Terminal/bash access** — Shell scripts assume a Unix-like environment (Linux, macOS, WSL on Windows).

4. **Internet connection optional** — Demos work offline on localhost; connection is only needed for package installation and MX lookups.

5. **tshark/Wireshark optional** — Captures can be made with tcpdump as alternative; pre-generated .pcap files are included.

6. **Docker optional** — All functionalities are available without Docker; containers only simplify multi-service deployment.

7. **gRPC not mandatory** — The syllabus requirement is "RPC concepts"; gRPC is included as advanced bonus, JSON-RPC and XML-RPC cover basic requirements.

8. **Emails do not leave localhost** — The educational SMTP server does not do external relay; all emails remain in local mailbox for safety.

---

*Document generated for Week 12 — Email Protocols and RPC*
*Revolvix&Hypotheticalandrei*
