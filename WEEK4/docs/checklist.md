# Checklist Week 4 – Custom Text and Binary Protocols

> **Course:** Computer Networks  
> **Week:** 4  
> **Topic:** Implementation of custom text and binary protocols over TCP and UDP

---

## ✅ Before the activity (24-48h in advance)

### Infrastructure preparation

- [ ] Verify functional VM/container with Python 3.8+
- [ ] Test `python3 --version` and `pip3 --version`
- [ ] Install packages: `pip3 install --break-system-packages pyshark`
- [ ] Verify sudo access for tshark/tcpdump
- [ ] Test Wireshark GUI (if used)
- [ ] Verify free ports: 5400, 5401, 5402
  ```bash
  netstat -tlnp | grep -E '5400|5401|5402'
  ```

### Materials preparation

- [ ] Starterkit S4 downloaded and extracted
- [ ] Execute `make setup` without errors
- [ ] Test `make verify` - all checks pass
- [ ] Run smoke test: `./tests/smoke_test.sh`
- [ ] Slides loaded and tested on projector
- [ ] theory.html, seminar.html, lab.html tested in browser
