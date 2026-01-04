# Traffic Captures – Week 11

## Description

This directory contains example traffic captures for FTP, DNS protocol analysis and load balancing scenarios.

## Generating captures

### DNS Capture
```bash
# Run DNS client + capture
tshark -i any -f "udp port 53" -w pcap/dns_query.pcap -c 10 &
python3 ../python/exercises/ex_11_03_dns_client.py --query google.com --type A
```

### Load Balancer Capture
```bash
# Start stack + capture
make demo-nginx
tshark -i any -f "tcp port 8080" -w pcap/lb_traffic.pcap -c 50 &
for i in {1..20}; do curl -s http://localhost:8080/; done
```

### FTP Capture
```bash
# FTP demo + capture
cd ../docker/ftp_demo
docker compose up -d
tshark -i any -f "tcp port 2121 or tcp portrange 30000-30009" -w ../pcap/ftp_session.pcap -c 30 &
```

## Analysing captures

### Reading with tshark
```bash
tshark -r dns_query.pcap -T fields -e dns.qry.name -e dns.a
tshark -r lb_traffic.pcap -q -z io,stat,0.5
```

### Reading with Wireshark
```bash
wireshark ftp_session.pcap
```

## Notes

- Captures are regenerated on each `make capture` run
- Large `.pcap` files are excluded from Git (see `.gitignore`)
- For advanced analysis, use `tshark -r file.pcap -V`

---
*Revolvix&Hypotheticalandrei*
