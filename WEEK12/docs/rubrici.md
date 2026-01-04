# Evaluation Rubrics — Week 12

## Email Protocols (SMTP, POP3, IMAP) and RPC (JSON-RPC, XML-RPC, gRPC)

---

## 1. Weekly Evaluation Structure

| Component | Weight | Description |
|-----------|--------|-------------|
| Active participation | 10% | Attendance, questions, involvement in discussions |
| Laboratory exercises | 40% | Completeing steps from lab.html + captures |
| Graded exercises | 30% | Solving ex_01_smtp.py and ex_02_rpc.py |
| Team project contribution | 20% | Incremental artefact (email/RPC module) |

---

## 2. Detailed Rubric — Laboratory Exercises (40 points)

### 2.1 Educational SMTP Server (10 points)

| Criterion | Excellent (10p) | Satisfactory (6-9p) | Insufficient (<6p) |
|-----------|-----------------|---------------------|-------------------|
| Server startup | Server started correctly on port 1025, active log | Started with minor configuredion errors | Does not start or major errors |
| Send email | Email sent successsfully, correct headers | Email sent with incompletee headers | Failed to send |
| Mailbox verification | Correct listing, content viewed | Partial listing | Cannot access mailbox |
| tshark capture | Completee capture, SMTP dialogue identified | Partial capture | No valid capture |

### 2.2 RPC Servers (15 points)

| Criterion | Excellent (15p) | Satisfactory (9-14p) | Insufficient (<9p) |
|-----------|-----------------|----------------------|-------------------|
| JSON-RPC server | Started, all methods functional | Started, some methods problematic | Does not start |
| JSON-RPC client | Successsful calls, batch functional | Simple calls successsful | Call failures |
| XML-RPC server | Started, introspection functional | Started, without introspection | Does not start |
| RPC benchmark | Run, results correctly interpreted | Run, superficial interpretation | Benchmark not completeed |

### 2.3 Captures and Analysis (15 points)

| Criterion | Excellent (15p) | Satisfactory (9-14p) | Insufficient (<9p) |
|-----------|-----------------|----------------------|-------------------|
| SMTP capture | Completee session: EHLO→DATA→QUIT | Partial capture | No capture |
| JSON-RPC capture | HTTP Request/Response identified | Only request or response | No capture |
| Interpretation | Correct explanations of fields | Superficial explanations | No interpretation |
| Wireshark filters | Correct filters applied and documented | Partially correct filters | No filters |

---

## 3. Detailed Rubric — Graded Exercises (30 points)

### 3.1 Exercise 1: Extended SMTP Client (★☆☆) — 5 points

| Criterion | Score |
|-----------|-------|
| Manual `MAIL FROM` command implementation | 2p |
| Manual `RCPT TO` command implementation | 1p |
| Response code validation (250, 354, etc.) | 2p |

### 3.2 Exercise 2: New RPC Method (★★☆) — 5 points

| Criterion | Score |
|-----------|-------|
| New method definition in server | 2p |
| Parameter and return documentation | 1p |
| Client test with correct output | 2p |

### 3.3 Exercise 3: RPC Error Handling (★★☆) — 5 points

| Criterion | Score |
|-----------|-------|
| Try-except implementation in server | 2p |
| Correct JSON-RPC error code return | 2p |
| Test with invalid input | 1p |

### 3.4 Exercise 4: Protocol Comparison (★★★) — 7 points

| Criterion | Score |
|-----------|-------|
| JSON-RPC benchmark (100 calls) | 2p |
| XML-RPC benchmark (100 calls) | 2p |
| Comparative table with metrics | 2p |
| Argued conclusion | 1p |

### 3.5 Exercise 5: Email with Attachments (★★★) — 4 points

| Criterion | Score |
|-----------|-------|
| MIME multipart message construction | 2p |
| Correctly base64 encoded attachment | 1p |
| Send and verification | 1p |

### 3.6 Challenge Exercise: Email Relay (★★★★) — 4 points

| Criterion | Score |
|-----------|-------|
| Functional relay server implementation | 2p |
| Forwarding to destination | 1p |
| Logging and debugging | 1p |

---

## 4. Rubric — Team Project Contribution (20 points)

### Option A: Email Notifications Module

| Criterion | Excellent (20p) | Good (14-19p) | Satisfactory (10-13p) | Insufficient (<10p) |
|-----------|-----------------|---------------|----------------------|-------------------|
| Architecture | Separate module, clear API, documented | Functional module, partially documented API | Functional code but not modularised | Non-functional code |
| Functionality | Send notifications, templates, retry | Basic sending functional | Partial sending | Sending failure |
| Configurability | Configurable SMTP server, secured credentials | Partial configuredion | Hardcoded values | No configuredion |
| Testing | Unit tests, integration tests | Documented manual tests | Ad-hoc tests | No testing |
| Integration | Approved PR, functional CI/CD | PR created, review pending | Untested local code | No integration |

### Option B: Internal RPC API

| Criterion | Excellent (20p) | Good (14-19p) | Satisfactory (10-13p) | Insufficient (<10p) |
|-----------|-----------------|---------------|----------------------|-------------------|
| API design | Consistent RESTful/RPC, versioned | Functional API, partial versioning | Functional endpoints | Non-functional API |
| Documentation | Completee OpenAPI/Swagger | Completee manual documentation | Basic README | No documentation |
| Error handling | Standard error codes, clear messages | Partially handled errors | Generic errors | No handling |
| Performance | Response time <100ms, caching | Acceptable response time | Variable performance | Frequent timeout |
| Security | Authentication, rate limiting | Basic authentication | No authentication | Vulnerabilities |

---

## 5. Code Quality Evaluation Criteria

| Aspect | Maximum Score | Description |
|--------|---------------|-------------|
| Functionality | 40% | Code does what it should, no errors |
| Clarity | 20% | Readable code, descriptive variables, logical structure |
| Documentation | 15% | Docstrings, useful comments, README |
| Error handling | 15% | Try-except, input validation, clear messages |
| Style | 10% | PEP8, consistent formatting, organised imports |

---

## 6. Penalties

| Situation | Penalty |
|-----------|---------|
| Delay <24h | -10% |
| Delay 24-48h | -25% |
| Delay >48h | -50% |
| Plagiarism | -100% + reporting |
| Code that does not run | -30% minimum |
| Missing documentation | -15% |
| No Wireshark captures | -20% |

---

## 7. Bonuses

| Achievement | Bonus |
|-------------|-------|
| Fully functional gRPC implementation | +10% |
| Functional POP3 client implementation | +5% |
| TLS security for SMTP | +5% |
| Optimised JSON-RPC batch requests | +5% |
| Demonstrative video documentation | +5% |

---

## 8. Student Self-Evaluation Checklist

Before submission, check:

- [ ] All files are in the correct structure
- [ ] `make verify` runs without errors
- [ ] .pcap captures are attached
- [ ] README.md updated with personal observations
- [ ] Code is consistently formatted (black, flake8)
- [ ] All exercises have documented output
- [ ] Team project has separate commit

---

## 9. Link with Syllabus Competencies

| Syllabus Competency | Week 12 Activity | Verification |
|---------------------|------------------|--------------|
| Concurrent server implementation | Multi-client SMTP server | tshark capture with parallel sessions |
| Socket programming | Manual SMTP Client/Server | Functional code without high-level libraries |
| Traffic analysis | Wireshark captures for Email and RPC | Filters applied, interpretation |
| Distributed services | JSON-RPC, XML-RPC client-server | Benchmark and comparison |
| Docker and containerisation | Optional: services in containers | docker-compose up functional |

---

## 10. Feedback and Improvement

After evaluation, the instructor will provide:

1. **Detailed scoring** — for each rubric
2. **Specific comments** — what was good, what needs improvement
3. **Additional resources** — for students who want to deepen their knowledge
4. **Individual meeting** — upon request, for clarifications

---

*Document generated for Week 12 — Email Protocols and RPC*
*Revolvix&Hypotheticalandrei*
