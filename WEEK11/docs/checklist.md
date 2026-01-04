# Instructor Checklist – Week 11

## Before Laboratory (1-2 days before)

### Technical Preparation

- [ ] Verify that `starterkit.zip` is available on the course platform
- [ ] Test all demos on the presentation machine
- [ ] Verify that Docker images are downloaded:
  ```bash
  docker pull nginx:alpine
  docker pull python:3.11-alpine
  ```
- [ ] Verify access to `ftp.gnu.org` for FTP demo
- [ ] Prepare demo VM with functional Mininet
- [ ] Ensure ports 80, 8080-8083 are free

### Materials Preparation

- [ ] Open `teoria/theory.html` for presentation
- [ ] Open `teoria/seminar.html` for seminar
- [ ] Prepare terminal with large font for demo
- [ ] Load backup slides (PDF) in case of technical problems

### Communication

- [ ] Announce to students to download starterkit before laboratory
- [ ] Remind system requirements (Docker, Python 3.10+)
- [ ] Publish link to laboratory documentation

---

## During Laboratory

### Introduction (5-10 minutes)

- [ ] Present week objectives
- [ ] Quick recap: TCP/UDP, HTTP, web servers
- [ ] Explain connection to team project

### Live Demo (20-30 minutes)

- [ ] Demonstrate `make setup` and `make verify`
- [ ] Show backend startup + Python LB
- [ ] Demonstrate Round Robin (visual in terminal)
- [ ] Show IP Hash and sticky sessions
- [ ] Demonstrate failover (stop a backend)
- [ ] Show Docker Nginx stack
- [ ] Visually compare Python LB vs Nginx

### Individual/Team Work (60-90 minutes)

- [ ] Monitor student progress
- [ ] Provide assistance for configuration problems
- [ ] Verify all have passed Steps 0-4
- [ ] Encourage experimentation with different parameters

### Control Questions

Ask these questions during laboratory:

1. "Why is passive FTP mode preferred in practice?"
2. "What happens if all backends fail?"
3. "When would you use least_conn instead of round_robin?"
4. "How does the load balancer detect that a backend has failed?"
5. "What role does TTL play in DNS?"

### Common Debugging

**Problem: "Port already in use"**
```bash
sudo lsof -i :8080
sudo kill <PID>
```

**Problem: "Docker permission denied"**
```bash
sudo usermod -aG docker $USER
# Or: sudo su - $USER
```

**Problem: "Mininet not found"**
```bash
sudo apt install mininet openvswitch-switch
sudo mn -c  # Clean old processes
```

---

## Recap (10-15 minutes)

### Key Points to Cover

- [ ] Difference round_robin vs least_conn vs ip_hash
- [ ] Passive failover: max_fails, fail_timeout
- [ ] Advantages of passive FTP mode
- [ ] DNS packet structure (header + question)
- [ ] SSH channels and port forwarding

### Connection to Project

- [ ] Explain weekly artefact (docker-compose + nginx)
- [ ] Clarify assessment criteria (rubrics)
- [ ] Set submission deadline

---

## After Laboratory

### Assessment

- [ ] Collect artefacts from each team
- [ ] Verify `docker compose up` functionality for each project
- [ ] Apply assessment rubric
- [ ] Note common problems for discussion at next lecture

### Feedback

- [ ] Note what worked well
- [ ] Identify points for improvement
- [ ] Update starterkit if needed

### Communication

- [ ] Publish solutions / answers to exercises
- [ ] Answer questions on forum/email
- [ ] Announce topic for next week (W12: SMTP, POP3, IMAP)

---

## Suggested Timing

| Segment | Duration | Cumulative |
|---------|----------|------------|
| Introduction + setup | 15 min | 0:15 |
| Live demo | 25 min | 0:40 |
| Individual work (Steps 2-5) | 45 min | 1:25 |
| Break | 10 min | 1:35 |
| Individual work (Steps 6-9) | 40 min | 2:15 |
| Recap + Q&A | 15 min | 2:30 |

---

## Quick Resources

### Frequent Commands

```bash
# Environment verification
make verify

# Start complete demo
make demo-all

# Cleanup
make clean

# Help
make help
```

### Useful Links

- Nginx Documentation: https://nginx.org/en/docs/
- Docker Compose: https://docs.docker.com/compose/
- Mininet Walkthrough: http://mininet.org/walkthrough/
- RFC 1035 (DNS): https://datatracker.ietf.org/doc/html/rfc1035

---

*Checklist for Week 11 – Computer Networks*  
*Revolvix&Hypotheticalandrei*
