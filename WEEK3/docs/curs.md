# Week 3 lecture notes — UDP broadcast and multicast, TCP tunnelling

## Concepts
### UDP broadcast
Broadcast targets an entire L2 segment. At IP level it is typically `255.255.255.255` or a subnet broadcast address. It is simple but noisy and usually constrained to a local network.

### UDP multicast
Multicast targets a group address (IPv4: `224.0.0.0/4`). Receivers opt in by joining a group. This reduces unnecessary traffic compared with broadcast when you want one-to-many delivery to selected receivers.

### TCP tunnelling (port forwarding)
A TCP tunnel accepts connections on one side and forwards data to a target host and port on the other side. It is a practical way to bridge connectivity between subnets when direct routing is restricted or when you want a controlled entry point.

## Packet analysis
Use `tcpdump` or `tshark` to observe:
- UDP datagrams and their destination addresses
- IGMP membership reports for multicast groups
- TCP three-way handshake and payload framing

## Common pitfalls
- Binding to the wrong interface or address
- Firewalls blocking multicast or UDP
- Expecting broadcast to cross routers
- Forgetting to close sockets and leaving ports busy
