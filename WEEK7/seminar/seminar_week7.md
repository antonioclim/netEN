# Week 7 seminar guide — packet interception and filtering

## Instructor outline (suggested 90 minutes)
1) Evidence first: what is a pcap and why it matters (10 minutes)  
2) Live capture: observe a TCP handshake and a UDP exchange (20 minutes)  
3) Filtering: allow and block decisions, REJECT vs DROP, where to apply rules (router vs host) (25 minutes)  
4) Reproducibility: scripts, artefacts, smoke tests and minimal documentation (20 minutes)  
5) Short wrap-up: what to keep for later weeks (reverse proxies, container networking, incident debugging) (15 minutes)

## Mini demos
### Demo A: baseline capture
- Run `./scripts/run_all.sh`
- Open `artifacts/demo.log` and point out where connectivity is confirmed
- Use `tshark` filters from `tests/expected_outputs.md`

### Demo B: blocking behaviour
- Show that the baseline works
- Apply `block_tcp_9090` and show the client failure
- Discuss why `DROP` can look like an application hang

### Demo C: user space interception
- Start `packet_filter.py` as a proxy and allow only one source IP
- Show how proxy logs differ from packet captures

## Control questions
- Which part of the network path do you need to observe to see both directions of traffic
- Why does a TCP reset provide faster feedback than a silent drop
- What evidence would convince you that the application is correct but the network policy is wrong
