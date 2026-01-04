# Week 7 cheatsheet — capture and filtering (CLI)

## Capture traffic (tcpdump)
Capture on all interfaces in the current namespace:

```bash
sudo tcpdump -i any -nn -U -w artifacts/demo.pcap tcp or udp
```

Quick live view for TCP port 9090:

```bash
sudo tcpdump -i any -nn tcp port 9090
```

UDP port 9091:

```bash
sudo tcpdump -i any -nn udp port 9091
```

Tip: use `-nn` to avoid DNS and service name resolution.

## Analyse captures (tshark)
Summary of conversations:

```bash
tshark -r artifacts/demo.pcap -q -z conv,tcp
```

Filter and print key fields:

```bash
tshark -r artifacts/demo.pcap -Y "tcp.port==9090" -T fields -e frame.time -e ip.src -e ip.dst -e tcp.flags -e tcp.len
```

Count packets matching a filter:

```bash
tshark -r artifacts/demo.pcap -Y "udp.port==9091" | wc -l
```

## Network checks
IP addresses and routes:

```bash
ip addr
ip route
```

Open sockets:

```bash
ss -lntup
```

Connectivity:

```bash
ping -c 2 10.0.7.100
```

## Filtering (iptables) — basic patterns
List rules:

```bash
sudo iptables -S
sudo iptables -L -n -v
```

Block TCP port 9090 on the FORWARD path (router or firewall node):

```bash
sudo iptables -I FORWARD 1 -p tcp --dport 9090 -j REJECT
```

Remove the first rule in FORWARD:

```bash
sudo iptables -D FORWARD 1
```

Flush FORWARD:

```bash
sudo iptables -F FORWARD
```

Be explicit while debugging: `REJECT` fails fast, `DROP` can look like a hang.

## Clean up
Mininet clean:

```bash
sudo mn -c
```

Remove Python artefacts:

```bash
find . -name "__pycache__" -type d -print -exec rm -rf {} +
find . -name "*.pyc" -type f -print -delete
```
