# Teaching Staff Checklist - Week 8

## Before lecture/seminar

### Technical preparation (1-2 days before)
- [ ] Verify that the VM works: `make verify`
- [ ] Test all demos manually
- [ ] Verify internet connection (for any downloads)
- [ ] Prepare offline backup for all material
- [ ] Test tshark/tcpdump with sudo permissions

### Teaching materials
- [ ] Open `docs/theory.html` in browser
- [ ] Open `docs/seminar.html` in browser  
- [ ] Open `docs/lab.html` in a separate tab
- [ ] Prepare presentation slides (optional)
- [ ] Print the laboratory checklist

### Room setup
- [ ] Projector functional
- [ ] Access to console/terminal visible to all
- [ ] Students have access to VM or working environment
- [ ] Whiteboard available for ad-hoc diagrams

---

## During the lecture

### Introduction (10-15 min)
- [ ] Brief recap of Week 7 (routing)
- [ ] Present Week 8 objectives
- [ ] Context of transport layer in OSI stack

### UDP/TCP Theory (25-30 min)
- [ ] Slides: UDP - characteristics, header, use cases
- [ ] Slides: TCP - characteristics, header, flags
- [ ] Demonstration: Three-way handshake with tshark
- [ ] Verification questions: "Why does TCP have sequence numbers?"

### TLS Theory (15 min)
- [ ] Slides: What is TLS, why it is important
- [ ] Slides: Simplified handshake
- [ ] Mention HTTPS, certificates

### HTTP Server & Proxy Theory (15-20 min)
- [ ] Slides: HTTP server architecture
- [ ] Slides: What is a reverse proxy
- [ ] Slides: Load balancing algorithms

### Recap and questions (5-10 min)
- [ ] Summary of key points
- [ ] Questions from audience
- [ ] Preview for seminar

---

## During the seminar

### Initial setup (10 min)
- [ ] Students clone/download starterkit
- [ ] Environment verification: `make verify`
- [ ] Resolve common setup problems

### HTTP Server Demo (25 min)
- [ ] Run `demo_http_server.py`
- [ ] Test with curl (multiple requests)
- [ ] Code explanation: request parsing, response generation
- [ ] Directory traversal demonstration (security)

### tshark Capture Demo (15 min)
- [ ] TCP handshake capture
- [ ] Interpret flags (SYN, SYN-ACK, ACK)
- [ ] Identify HTTP request/response in capture

### Reverse Proxy Demo (20 min)
- [ ] Start 2 backends
- [ ] Start proxy
- [ ] Round robin demonstration
- [ ] Traffic capture through proxy

### Guided exercises (20-30 min)
- [ ] Exercise 1: Complete HTTP server
- [ ] Exercise 2: Complete proxy (for advanced students)
- [ ] Individual support for stuck students

### Wrap-up (5-10 min)
- [ ] What to prepare for the project
- [ ] Homework/additional exercises
- [ ] Final questions

---

## After lecture/seminar

### Immediately after
- [ ] Save captures/demos for reference
- [ ] Note frequently asked questions for FAQ
- [ ] Identify students who need extra support

### Until next week
- [ ] Check submitted assignments
- [ ] Answer questions on forum/email
- [ ] Prepare feedback for projects

---

## Frequent troubleshooting

### "Port already in use"
```bash
lsof -i :8080
kill $(lsof -t -i :8080)
# or change the port
```

### "Permission denied" for tcpdump
```bash
sudo tcpdump ...
# or add user to wireshark group
```

### "Module not found" Python
```bash
pip install --user <module>
# or check virtual environment
```

### "Connection refused"
1. Verify that the server is running: `ss -tuln | grep PORT`
2. Verify the correct IP (localhost vs 0.0.0.0)
3. Check the firewall

### Mininet will not start
```bash
sudo mn -c  # cleanup
sudo python3 topo_....py
```

---

## Suggested verification questions

### Terminology level
- What is a socket?
- What does TCP vs UDP mean?
- What is a port?

### Understanding level
- Why is TCP "reliable"?
- How does the three-way handshake work?
- What is the difference between forward and reverse proxy?

### Application level
- Write the code to send a UDP message
- How do you see all active connections on a host?
- How do you capture only HTTP traffic?

### Analysis level
- Why do we lose packets in the network and how do we detect them?
- How do you identify a directory traversal attack?
- What happens if a backend goes down?

### Evaluation level
- Which load balancing algorithm is better for what scenarios?
- TCP or UDP for video streaming - justify

### Creation level
- Design a caching system for the proxy
- Implement health check for backends

---

## Notes for the future

_Add here observations for the next iteration of the course:_

- [ ] ...
- [ ] ...

---

© Revolvix&Hypotheticalandrei
