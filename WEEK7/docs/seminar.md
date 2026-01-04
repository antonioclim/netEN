# Seminar 6 – NAT/PAT and SDN in a simulated topology

**Course:** Computer Networks  
**Programme:** Business Informatics (ASE-CSIE)  
**Week:** 6  
**Format:** Hands-on seminar (CLI-only)  

## What you will learn

By the end of this seminar, you will be able to:

1. Configure NAT and PAT (NAT overload) using `iptables` on a Linux router
2. Explain what changes NAT introduces to packet headers and why it is widely used
3. Run a Mininet topology and validate basic connectivity with `ping` and `ip route`
4. Capture and inspect traffic using `tcpdump` and `tshark` (where available)
5. Explain the SDN control plane and data plane split, then run a minimal OpenFlow example

## Prerequisites

- A Linux VM (Ubuntu 20.04+ recommended) with `sudo` access
- Python 3 installed
- Mininet installed (required for topology demos)
- Open vSwitch installed (required for SDN demos)
- Optional: `tcpdump` and `tshark` for traffic analysis

## Quickstart

From the kit root:

```bash
make setup
make demo
make test
```

The demo writes its outputs to `artifacts/`:

- `artifacts/demo.log`
- `artifacts/validation.txt`
- optionally `artifacts/demo.pcap` (if capture is enabled and permitted)

## Practical workflow

### Part A: NAT and PAT

1. Start the NAT topology
2. Verify routes, then verify that private hosts can reach the outside segment
3. Inspect NAT rules and counters
4. Capture traffic on the router-facing interfaces and compare pre-NAT and post-NAT headers

Suggested CLI commands:

```bash
ip -br a
ip r
sudo iptables -t nat -S
sudo iptables -t nat -L -n -v
sudo tcpdump -i any -nn -c 30
```

### Part B: SDN (minimal OpenFlow)

1. Start the SDN topology
2. Start the controller
3. Validate that flows are installed and that traffic is forwarded

Suggested CLI commands:

```bash
sudo ovs-vsctl show
sudo ovs-ofctl -O OpenFlow13 dump-flows s1
```

## Student deliverable and success criteria

Deliver a short report that includes:

- Evidence of NAT being applied (rules and counters)
- A brief explanation of what addresses and ports are translated, and where
- One capture excerpt or a `tshark` filter result that highlights the translation
- Evidence of SDN flows being installed (controller output or `dump-flows`)
