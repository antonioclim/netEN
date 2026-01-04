# Lecture 5: Network Layer — IPv4 and IPv6 Addressing, Subnetting and VLSM

## 1. What we will learn and why it matters

### Learning outcomes
By the end of this lecture you should be able to:
- Distinguish IPv4 and IPv6 addressing, including public, private and special-purpose ranges
- Explain the role of the network layer in the TCP/IP stack and how it relates to the data link layer
- Compute CIDR parameters for a given network, including network address, broadcast address, host range and subnet mask
- Apply VLSM to design an addressing plan that meets a set of constraints

### Why it matters
Addressing is the foundation for routing, access control, troubleshooting and reproducible lab setups. If the addressing plan is inconsistent, every higher-level activity becomes harder, slower and less reliable.

## 2. Addressing essentials

### 2.1 IPv4 structure
IPv4 uses 32 bits, typically written as dotted decimal. CIDR notation expresses the prefix length, for example `10.0.5.0/24`.

Key derived values:
- Network address
- Broadcast address (IPv4 only)
- First usable host, last usable host
- Total hosts and usable hosts

### 2.2 Private and special-purpose ranges
Common private IPv4 blocks:
- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`

Special-purpose examples:
- Loopback `127.0.0.0/8`
- Link-local `169.254.0.0/16`

### 2.3 IPv6 in one page
IPv6 uses 128 bits and does not use broadcast. The equivalent concepts use prefixes, multicast and neighbour discovery.

## 3. Subnetting and VLSM

### 3.1 Subnetting workflow
1. Start from the required number of subnets and hosts
2. Choose the smallest prefix that satisfies each requirement
3. Allocate subnets from largest to smallest (VLSM)
4. Document the plan and verify it with a calculator

### 3.2 Example
Given `10.0.5.0/24`, allocate:
- one /26 for servers
- two /27 for labs
- the remainder for point-to-point links

Use `python/apps/subnet_calc.py` to verify each allocation and to print a consistent summary.

## 4. Practical demonstration (CLI-first)
Run:
```bash
make demo
```

This produces:
- `artifacts/demo.log`
- `artifacts/validation.txt`

If Mininet is enabled for this week, the demo may also produce:
- `artifacts/demo.pcap`

## 5. What students must deliver
- A short addressing plan for the given scenario, written in `docs/` or submitted separately
- CLI evidence: the commands used and the outputs, saved under `artifacts/`
- A brief explanation of why each subnet size was chosen
