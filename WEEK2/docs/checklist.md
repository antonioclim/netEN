# Teaching Staff Checklist – Week 2

**OSI/TCP-IP Architectural Models & Socket Programming**

---

## Before Lecture/Seminar

### One Day Before

- [ ] Verify classroom equipment functioning (projector, network)
- [ ] Update slides if necessary
- [ ] Verify links in materials (none are broken)
- [ ] Prepare VM/container with working environment for demonstrations

### 30 Minutes Before

- [ ] Open presentation on main screen
- [ ] Start demonstration VM
- [ ] Verify that `make verify` passes in VM
- [ ] Open terminal for live demo
- [ ] Open Wireshark/tshark prepared for capture
- [ ] Open `theory.html` in browser for interactive diagrams

### Demo Environment Verification

```bash
cd starterkit_s2
make verify
make clean
```

---

## During Lecture (2h)

### Part I: Fundamentals (0:00 – 0:25)

- [ ] Lecture 1 recap (protocol, stack, encapsulation) — 5 min
- [ ] Introduction: Why architectural models? — 10 min
- [ ] Analogy with building architecture
- [ ] Layer concept and services — 10 min
- [ ] **Control question**: "What would happen without standards?"

### Part II: The OSI Model (0:25 – 1:00)

- [ ] Present the 7 layers — 20 min
  - [ ] Physical Layer: bit, cable, signal
  - [ ] Data Link Layer: frame, MAC, CRC
  - [ ] Network Layer: packet, IP, routing
  - [ ] Transport Layer: segment, port, TCP/UDP
  - [ ] Upper layers: 5-6-7 more briefly
- [ ] OSI diagram (`fig-osi-straturi.png`) — visualisation
- [ ] Encapsulation with diagram (`fig-osi-incapsulare.png`) — 5 min
- [ ] Horizontal/vertical communication (`fig-osi-comunicare.png`) — 5 min
- [ ] **Control questions**: 
  - [ ] "What PDU does the Transport layer have?"
  - [ ] "Which layer handles MAC?"

### Part III: The TCP/IP Model (1:00 – 1:25)

- [ ] Introduction: practical vs theoretical model — 5 min
- [ ] The 4 TCP/IP layers — 10 min
- [ ] OSI vs TCP/IP comparison (`fig-osi-vs-tcpip.png`) — 5 min
- [ ] Why do we use both models? — 5 min
- [ ] **Control question**: "When do we use UDP instead of TCP?"

### Part IV: Link to Practice (1:25 – 1:40)

- [ ] Socket API as interface — 5 min
- [ ] Seminar preview: what we will implement — 5 min
- [ ] Quick demo (optional, if time permits):
  ```bash
  make demo-tcp
  ```
- [ ] Present kit structure

### Part V: Recap (1:40 – 1:45)

- [ ] Summary on 5 main points
- [ ] Final questions
- [ ] Announce seminar requirements

---

## During Seminar (2h)

### Phase 0: Preparation (0:00 – 0:10)

- [ ] Verify all students have access to VM/environment
- [ ] Run `make verify` collectively
- [ ] Resolve setup problems

### Phase 1: Mininet Warm-up (0:10 – 0:25)

- [ ] Demonstration `make mininet-cli`
- [ ] Students explore: `nodes`, `net`, `pingall`
- [ ] **Verification**: everyone has functional ping

### Phase 2: TCP Lab (0:25 – 1:00)

- [ ] TCP server demo — explain parameters
- [ ] Capture demo — explain BPF filter
- [ ] Students run client themselves
- [ ] Capture analysis — identify handshake
- [ ] **Verification**: students can identify SYN, SYN-ACK, ACK

### Phase 3: UDP Lab (1:00 – 1:25)

- [ ] UDP server demo
- [ ] Interactive client — explain application protocol
- [ ] Compare TCP vs UDP capture
- [ ] **Verification**: students can explain overhead difference

### Phase 4: Templates (1:25 – 1:50)

- [ ] Explain TCP template
- [ ] Individual/pair work time
- [ ] Assistance with problems
- [ ] **Verification**: functional template demonstrated

### Phase 5: Extension (1:50 – 2:00, if time permits)

- [ ] Extended topology demo with router
- [ ] Discussion about communication between subnets

### Finalisation

- [ ] Announce deliverables (what needs to be submitted)
- [ ] Environment cleanup: `make clean`

---

## After Lecture/Seminar

### Immediately After

- [ ] Note observations for future improvements
- [ ] Verify materials are updated in repository
- [ ] Reply to questions received via email/forum

### Weekly

- [ ] Verify received deliverables
- [ ] Feedback on completed templates
- [ ] Prepare next week's materials

---

## Frequently Asked Student Questions

| Question | Brief Answer |
|----------|--------------|
| "Why doesn't the server work?" | Check port: `lsof -i :9999`, `make clean` |
| "Capture is empty" | Check interface and filter: `-i lo` vs `-i eth0` |
| "Connection refused" | server is not running. Check `jobs`, restart |
| "When do I use TCP vs UDP?" | TCP = reliability (web, email); UDP = speed (streaming, gaming) |
| "What does L7, L3 mean?" | References to OSI layers: L7=Application, L3=Network |

---

## Common Pitfalls to Avoid

1. **Assuming everyone has environment configured** — always collective verification at start
2. **Demos that don't work** — test beforehand in exactly the same configuration
3. **Too much theory without practice** — intersperse questions and mini-exercises
4. **Ignoring stuck students** — allocate time for individual assistance
5. **Rushing through capture** — TCP handshake is the key concept, dedicate time

---

## Auxiliary Resources

- `theory.html` — for interactive diagrams in lecture
- `seminar.html` — dashboard for seminar
- `lab.html` — step-by-step guide for independent students
- Wireshark sample captures: [https://wiki.wireshark.org/SampleCaptures](https://wiki.wireshark.org/SampleCaptures)

---

*Revolvix&Hypotheticalandrei*
