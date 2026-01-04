# CLI cheatsheet (Week 1)

This kit is designed for Linux CLI-only environments. All commands below are safe to run on a minimal VM.

## Addressing and routes
```bash
ip -br a
ip r
ip neigh
```

## Sockets and ports
```bash
ss -lntup
ss -lunp
```

## Connectivity and latency
```bash
ping -c 4 1.1.1.1
ping -c 4 "${H1_IP:-10.0.1.11}"
```

## Name resolution
```bash
getent hosts example.com
resolvectl status 2>/dev/null || true
```

## TCP and UDP quick tests (netcat)
TCP server:
```bash
nc -l -p 9090
```

TCP client:
```bash
printf "hello\n" | nc 127.0.0.1 9090
```

UDP listener:
```bash
nc -u -l -p 9091
```

UDP sender:
```bash
printf "ping\n" | nc -u 127.0.0.1 9091
```

## Capture with tcpdump
Capture ICMP, TCP and UDP:
```bash
sudo tcpdump -i any -w artifacts/demo.pcap icmp or tcp or udp
```

Inspect quickly:
```bash
sudo tcpdump -nn -r artifacts/demo.pcap | head
```

## Inspect with tshark (optional)
```bash
tshark -r artifacts/demo.pcap -q -z conv,tcp | head -n 40
```

## iperf3 (optional, if installed)
Server:
```bash
iperf3 -s -p 9090
```

Client:
```bash
iperf3 -c 127.0.0.1 -p 9090
```
