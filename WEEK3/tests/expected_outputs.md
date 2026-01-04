# Expected outputs — Week 3

This file documents representative outputs for the examples. Exact timestamps and ephemeral ports will vary.

## ex01_udp_broadcast.py
Receiver:
- should print a line indicating it is listening on `0.0.0.0:<port>`
- should print source IP and source port for each received datagram
- should exit cleanly after `--count` datagrams (if specified)

Sender:
- should print destination address and port for each datagram sent
- should exit cleanly after `--count` datagrams (if specified)

## ex02_udp_multicast.py
Receiver:
- should print the multicast group and port
- should confirm it joined the multicast group on the selected interface (where applicable)

Sender:
- should print the multicast group and port and the number of datagrams sent

## ex03_tcp_tunnel.py
- should report the listen address and the forward target
- should log accepted connections and forward bytes in both directions
