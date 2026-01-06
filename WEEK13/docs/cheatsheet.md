# CLI cheatsheet for Week 13

## Network inspection

Use `ip a`, `ip r`, `ss -lntup` and `ping -c 3 <ip>` to validate interfaces, routes and reachability.

## Capture traffic

Use `tcpdump -i <iface> -w artifacts/demo.pcap` or `tshark -i <iface> -w artifacts/demo.pcap` if available.

## Quick sockets and ports

Use `nc -l -p 9090` for a TCP listener and `nc -u -l -p 9091` for UDP.

## Throughput

Use `iperf3 -s -p 9090` and `iperf3 -c <ip> -p 9090` if `iperf3` is installed.
