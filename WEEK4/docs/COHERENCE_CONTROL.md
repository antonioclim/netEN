# Coherence Control - Week 4

> **Course:** Computer Networks  
> **Week:** 4  
> **Topic:** Custom Text and Binary Protocols over TCP and UDP

---

## Alignment Map

### Course Syllabus Topic → Lecture Sections → Seminar Sections → Starterkit Artefacts

| Course Syllabus Topic | Lecture Sections | Seminar Sections | Starterkit Artefacts |
|---------------------|---------------|------------------|---------------------|
| **S4: Socket Programming: Implementation of Custom Text and Binary Protocols over TCP and UDP** | 3.1 Motivation for Custom Protocols | 4.1 Environment Preparation | `/README.md`, `/scripts/setup.sh` |
| | 3.2 TEXT Protocols | 4.2 TEXT Protocol Implementation | `/python/apps/text_proto_*.py` |
| | 3.2.1 The Framing Problem | 4.2.1 recv_until() | `/python/utils/io_utils.py` |
| | 3.3 BINARY Protocols | 4.3 BINARY Protocol Implementation | `/python/apps/binary_proto_*.py` |
| | 3.3.1 Struct Serialisation | 4.3.2 Pack/Unpack | `/python/utils/proto_common.py` |
| | 3.3.2 CRC32 Validation | 4.3.3 CRC32 | `zlib.crc32()` in code |
| | 3.4 UDP Sensor Protocol | 5.3 Mininet UDP Demo | `/python/apps/udp_sensor_*.py` |
| | | | `/mininet/scenario_udp_demo.py` |
| **Traffic Analysis (from S1)** | Reference in 3.2, 3.3 | 5.2 Capture and Analysis | `/docs/tcpdump_cheatsheet.md` |
| | | | `/docs/tshark_cheatsheet.md` |
| **Testing in Simulator (from S6)** | 3.5 Mininet Testing | 5.3 Mininet Experiment | `/mininet/scenario_*.py` |
| | | | `/docs/mininet_cheatsheet.md` |

### Learning Objectives Mapping → Artefacts

| Objective | Taxonomic Level | Primary Artefact |
|----------|----------------|-------------------|
| Specify text protocol | Understanding | `Lecture.md` §3.2, `theory.html` slides 6-11 |
| Specify binary protocol | Understanding | `Lecture.md` §3.3, `theory.html` slides 12-18 |
| Implement recv_until/recv_exact | Application | `io_utils.py`, Exercises, templates |
| Serialisation with struct | Application | `proto_common.py`, `seminar.html` code tab |
| CRC32 Validation | Application | All protocols, `lab.html` step 3 |
| Custom traffic analysis | Analysis | Cheatsheets, `lab.html` step 4, `seminar.html` |
| Evaluate TEXT vs BINARY | Evaluation | Exercise 2, `theory.html` slide 24 |
| Design hybrid protocol | Creation | Challenge Exercise, team project |

---

## Decision Log

### Modifications and Motivations

1. **Unified BINARY protocol structure (14-byte header)**
   - *Decision:* Fixed header with MAGIC, VERSION, TYPE, PAYLOAD_LEN, SEQUENCE, CRC32
   - *Motivation:* Provides extensibility (versioning), easy debugging (magic), message correlation (sequence), integrity (CRC)
   - *Source:* Consolidation from S4v2 and S4v3 archives

2. **TEXT framing with "<LEN> <PAYLOAD>\n"**
   - *Decision:* Length-prefixed + newline terminator
   - *Motivation:* Self-describing, testable with netcat, allows payload with spaces
   - *Rejected alternative:* Newline only (payload cannot contain \n)

3. **recv_until() and recv_exact() as separate functions**
   - *Decision:* Two distinct functions in io_utils.py
   - *Motivation:* Pedagogical clarity - students understand the difference between reading until delimiter vs exact reading

4. **CRC32 with zlib (not crc32c or custom)**
   - *Decision:* zlib.crc32() available in standard library
   - *Motivation:* Zero external dependencies, acceptable performance, wide compatibility
   - *Note:* Mask & 0xFFFFFFFF for unsigned result

5. **UDP sensor protocol with fixed 23-byte format**
   - *Decision:* Rigid format vs variable length
   - *Motivation:* Demonstrates difference from TCP, simple parsing for embedded devices

6. **Three separate Mininet scenarios**
   - *Decision:* scenario_arp_demo.py, scenario_tcp_demo.py, scenario_udp_demo.py
   - *Motivation:* Conceptual isolation, independent running, focus on one protocol at a time
   - *Rejected alternative:* Single large script with all demos

7. **Docker Compose with 3 services (server, client, monitor)**
   - *Decision:* Multi-container orchestration vs single container
   - *Motivation:* Simulates real architecture, allows capture from separate container

8. **Exercises graded on 6 levels**
   - *Decision:* From understanding (Ex1) to creation (Challenge)
   - *Motivation:* Progressive difficulty, addresses all Bloom taxonomy levels

9. **HTML with same visual style for all 3 files**
    - *Motivation:* Independent quick reference, printable, reusable in other weeks

10. **One-command demo (make demo or scripts/run_all.sh)**
    - *Motivation:* One-command experience, consistency between weeks

---

## Project Context

### Assumptions
- Single-user VM lab environment (Mininet requires root)
- Target student profile: 3rd year, familiar with Python basics
- Lab duration: 2 hours, week 4 of 14
- A team project in progress where the custom protocol will be integrated
- HTML files are tested on recent Chrome/Firefox

### Constraints
- S4 topic "Socket Programming: Implementation of Custom Text and Binary Protocols over TCP and UDP" remains unchanged
- 2h Lecture + 2h Seminar per week
- Code comments are in English (standard programming convention)

---

## Artefacts Directory

```
starterkit_s4/
│
├── Makefile                          # make help, demo, test, clean
├── README.md                         # Quick setup + troubleshooting
│
├── docs/
│   ├── curs.md                       # Lecture (theory)
│   ├── seminar.md                    # Seminar (guided implementation)
│   ├── lab.md                        # Lab (experimental steps)
│   ├── rubrici.md                    # Weekly evaluation criteria
│   └── [cheatsheets...]
│
├── python/                           # All Python code
├── mininet/                          # Network scenarios
├── scripts/                          # Automation
├── tests/                            # Validation
└── docker/                           # Containerisation
```

---

## Quality Checklist

### Completeness
- [x] All mandatory artefacts present
- [x] README with quickstart, troubleshooting and reset
- [x] Makefile with standard targets
- [x] Scripts executable (chmod +x)
- [x] Tests runnable non-interactively

### Linguistic Consistency
- [x] All student-facing text in British English
- [x] No Oxford comma in lists
- [x] Code comments in English
- [x] Technical terms consistent (serialize/serialise, etc.)

### Functional Validation
- [x] All Python files pass py_compile
- [x] Scripts have proper shebangs and error handling
- [x] Demo runs end-to-end
- [x] Tests validate expected outputs

### Didactic Coherence
- [x] Learning objectives map to artefacts
- [x] Progressive difficulty in exercises
- [x] Theory-practice alignment
- [x] Troubleshooting covers common pitfalls

---

**Document Type:** Coherence Control and Decision Log  
**Audience:** Teaching Staff and Maintainers  
**Licence:** MIT  
**Authors:** Hypotheticalandrei and Revolvix  
**Institution:** ASE-CSIE, Bucharest
