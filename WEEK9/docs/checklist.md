# Teaching Staff Checklist – Week 9

## Before the Session (24-48h)

### Materials Verification

- [ ] The S9 starterkit is updated and functional
- [ ] All files in `server-files/` are present and uncorrupted
- [ ] `make verify` passes on the presentation machine
- [ ] Software versions match (Python 3.8+, Docker 20.10+)
- [ ] HTML presentations load correctly (theory.html, seminar.html, lab.html)

### Infrastructure Verification

- [ ] The lab VM starts in less than 2 minutes
- [ ] Docker daemon is running and has pre-built images
- [ ] Wireshark/tshark works on the loopback interface
- [ ] Internet connection is available (for pip/docker pull if needed)
- [ ] Projector/screen sharing works

### Pedagogical Preparation

- [ ] I have reviewed the material and identified difficult points
- [ ] I have prepared verification questions for key moments
- [ ] I have identified which exercises I will demonstrate live
- [ ] I have solutions for all exercises (including challenge)
- [ ] I have prepared examples of common mistakes for live debugging

### Logistics Preparation

- [ ] Attendance list prepared
- [ ] I know the distribution by groups/teams for the semester project
- [ ] I have checked if there are students with late work to catch up

---

## During the Session

### Opening (5 min)

- [ ] Greeting and objectives presentation
- [ ] Brief recap of previous week (L4 Transport → L5/L6)
- [ ] Announcement of weekly artefact for team project

### Theoretical Lecture (if applicable) (40-50 min)

- [ ] Slides display correctly
- [ ] Live demos work (or I have backup video)
- [ ] Question breaks at each major section
- [ ] Interactive mini-quiz in the middle of presentation

### Seminar/Lab (60-90 min)

**Phase 1: Setup (10 min)**
- [ ] All students have access to starterkit
- [ ] `make verify` passes on at least 80% of machines
- [ ] Quick resolution of common setup problems

**Phase 2: Guided Demonstration (20 min)**
- [ ] Endianness demo executed and explained
- [ ] Server started, client connected
- [ ] AUTH → LIST → GET sequence demonstrated

**Phase 3: Individual/Pair Work (40-50 min)**
- [ ] Students work on steps 3-5 from lab.html
- [ ] I circulate among students for support
- [ ] I note frequent problems for final discussion

**Phase 4: Collective Debugging (10 min)**
- [ ] I address 2-3 identified frequent problems
- [ ] I demonstrate debugging techniques (tshark, logs)

### Closing (5-10 min)

- [ ] Recap "What We Learned"
- [ ] Announcement of artefact submission deadline (if any)
- [ ] Final questions
- [ ] Quick feedback (what went well / what can be improved)

---

## After the Session

### Immediately (same day)

- [ ] I note technical problems encountered for remediation
- [ ] I update FAQ if new questions appeared
- [ ] I save interesting screenshots for future sessions

### Within 24-48h

- [ ] I check submissions (if there is a deadline)
- [ ] I respond to questions received by email/forum
- [ ] I update materials with corrections if needed

### Weekly

- [ ] I synchronise with other instructors about progress
- [ ] I check alignment with semester project
- [ ] I prepare teaser for next week

---

## Verification Questions for Students

### Understanding Level (can be asked anytime)

1. What is the difference between a TCP connection and an application-level session?
2. Why do we use Big Endian for network protocols?
3. What role does the CRC-32 field play in our protocol?

### Application Level (after demo)

4. What tshark command do we use to filter only packets with payload?
5. How do we verify that the server is listening on the correct port?
6. What happens if we send a command without being authenticated?

### Analysis Level (during lab)

7. Analysing the capture, can you identify the authentication moment?
8. How many bytes does our protocol header have and why?
9. What do you observe in the size difference between the original and compressed file?

### Synthesis Level (for advanced students)

10. How would you modify the protocol to support encryption?
11. What disadvantages does our single-channel approach have (compared to FTP with two)?

---

## Pitfalls and Quick Solutions

| Pitfall | Sign | Quick Solution |
|---------|------|----------------|
| Docker does not start | "Cannot connect to Docker daemon" | `sudo systemctl start docker` |
| Port occupied | "Address already in use" | `sudo lsof -i :9021 && kill <PID>` |
| tshark permissions | "Permission denied" | `sudo usermod -aG wireshark $USER` |
| Wrong Python | ImportError for struct | `python3` instead of `python` |
| Missing files | FileNotFoundError | Check you are in the correct directory |

---

## Notes for Continuous Improvement

### What Worked Well

(Complete after each session)

### What Needs Adjustments

(Complete after each session)

### Suggestions from Students

(Complete from feedback)
