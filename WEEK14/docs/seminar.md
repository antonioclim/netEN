# Seminar 14 — Team Project Evaluation

**Course:** Computer Networks / Networking  
**Week:** 14 (final)  
**Duration:** 120 minutes

---

## Objective

Seminar 14 is dedicated to **presenting and evaluating team projects**. According to the course syllabus, the project presentation is a **condition for exam access**.

### What You Demonstrate

1. The project **works** (reproducible execution from a clean environment)
2. You understand the **architecture** and can justify technical decisions
3. You can **diagnose** problems using the tools learned
4. You produce **verifiable evidence** (logs, captures, reports)

---

## Presentation Structure (7-10 minutes/team)

### 1. Introduction (1 min)
- What does the project do? (one sentence)
- What protocols/technologies does it use?

### 2. Live Demo (3-4 min)
- Start from clean environment (setup, run)
- Demonstrate main functionality
- Show a relevant pcap capture

### 3. Architecture (2 min)
- Simple diagram (components, flows)
- Justification of technical choices

### 4. Q&A (2-3 min)
- Defence questions (see below)

---

## Typical Defence Questions

### Level 1: Knowledge
- On what port does the server listen?
- What transport protocol do you use?
- What does HTTP code 502 mean?

### Level 2: Comprehension
- Explain the flow of a request from client to server
- What happens when `accept()` returns?
- Why did you choose TCP and not UDP?

### Level 3: Application
- Modify the timeout and show the effect
- Add a new endpoint and test it
- Change the IP and show what breaks

### Level 4: Analysis
- Why do you think `recv()` is blocking?
- Compare latency with and without proxy
- What do the retransmissions in the pcap indicate?

### Level 5: Evaluation
- Is your service vulnerable to DoS?
- How would you improve scalability?
- What would you do differently in production?

---

## Evaluation Rubric

### Criteria (total: 100 points → project grade)

| Criterion | Weight | Excellent (90-100%) | Good (70-89%) | Sufficient (50-69%) | Insufficient (<50%) |
|-----------|--------|---------------------|---------------|---------------------|---------------------|
| **Complexity** | 40% | Multi-component architecture, diverse protocols | Solid architecture, 2+ components | Basic functional implementation | Too simple/incomplete |
| **Functionality** | 30% | Works perfectly, edge cases handled | Works with minor issues | Partially works | Does not work |
| **Presentation/Q&A** | 20% | Clear explanations, correct answers | Most answers correct | Partial answers | Cannot explain |
| **Documentation** | 10% | Complete README, comments, examples | Good README, some comments | Minimal README | Missing |

### Signs of Success

**Complexity:**
- [ ] Multiple components (client, server, proxy/LB)
- [ ] Diverse protocols (TCP, HTTP, possibly TLS)
- [ ] Persistence or state (optional)

**Functionality:**
- [ ] Starts from clean environment in < 5 minutes
- [ ] Demonstrates main flow
- [ ] Handles errors (timeout, connection refused)

**Presentation:**
- [ ] Can explain each component
- [ ] Answers questions without reading from code
- [ ] Shows evidence (pcap, logs)

**Documentation:**
- [ ] README with installation/run steps
- [ ] Comments in code for complex parts
- [ ] Example of expected output

---

## Presentation Preparation

### Checklist Before Seminar

- [ ] Project starts from clean environment (new/cleaned VM)
- [ ] README updated with exact steps
- [ ] I have tested the demo at least 2 times
- [ ] I have prepared 1-2 relevant pcap captures
- [ ] I know how to answer the basic questions

### What to Bring

1. **Laptop** with prepared VM OR access to development environment
2. **README** clear (printable)
3. **Demo plan** (written steps)
4. **Captures** prepared (in case the demo fails)

### Quick Troubleshooting

| Problem | Quick Solution |
|---------|----------------|
| VM does not start | Use prepared captures |
| Port occupied | `sudo ss -lntp | grep <port>` + kill |
| Mininet dirty | `sudo mn -c` |
| OVS down | `sudo systemctl restart openvswitch-switch` |

---

## Seminar Proceedings

### Presentation Order
- Established at the beginning of the seminar (random or volunteers)
- Each team has 10-12 minutes (presentation + Q&A)

### Audience Role
- Listen actively
- Ask constructive questions
- Take notes for your own preparation

### Evaluation
- Teaching staff grades according to rubric
- Immediate oral feedback or at the end

---

## After the Seminar

### For Students
- Finalise documentation
- Prepare for the exam (70% of final grade)
- Reflect: what did you learn? what would you do differently?

### Final Deliverables
- Source code (repository or archive)
- Updated README
- Short report (optional, for bonus)

---

## Examples of Acceptable Projects

### Minimum Level
- TCP echo client-server with logging
- Simple HTTP server with 2-3 endpoints

### Medium Level
- Load balancer with 2 backends
- Multi-client chat with broadcast
- DNS proxy with cache

### Advanced Level
- Microservices with service discovery
- Simple VPN (TCP tunnel)
- SDN controller with custom policies

---

## Resources

- Starterkit W14 (example of structure)
- Kit documentation (docs/)
- Review questions (ex_14_01.py)
