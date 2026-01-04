# Week 7 notes — why packet capture and filtering matter for software engineers

## 1) Packet capture is evidence
When a distributed system misbehaves, logs can be misleading or incomplete. Captures (pcaps) tell you what actually crossed the wire. This is valuable for:
- debugging timeouts (is there a SYN but no SYN-ACK)
- verifying what your client really sends (headers, framing, retries)
- distinguishing application issues from network issues (retransmissions, resets, ICMP errors)

## 2) Filtering makes policy explicit
Filtering is not only a security topic. It is an operational tool:
- limiting blast radius when a service misbehaves
- protecting fragile dependencies by blocking risky paths
- enforcing separation between environments (dev, test and prod)

A key engineering requirement is reproducibility: a rule should be:
- readable (what does it do and why)
- testable (how do we know it works)
- reversible (how do we undo it safely)

## 3) Common pitfalls
- interpreting a drop as an application bug (it may be a filter)
- forgetting that ICMP is needed for debugging (blocking all ICMP makes diagnosis harder)
- mixing host rules and router rules (apply them where the traffic actually passes)

## 4) Linking to the rest of the course
This week builds on socket programming and traffic observation and prepares you for service level topics such as reverse proxies, container networking and diagnosing real production incidents.
