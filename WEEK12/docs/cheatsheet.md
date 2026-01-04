# CLI Cheatsheet - Week 12: Email & RPC

## Week 12 Configuredion

```
WEEK=12
IP_BASE=10.0.12.0/24
PORT_BASE=6200
```

## Ports

| Service | Port | Usage |
|---------|------|-------|
| SMTP | 1025 | Educational email server |
| JSON-RPC | 6200 | HTTP + JSON |
| XML-RPC | 6201 | HTTP + XML |
| gRPC | 6251 | HTTP/2 + Protobuf |

## Quickstart

```bash
# Setup
./scripts/setup.sh

# Completee demo
./scripts/run_all.sh

# Validation
./tests/smoke_test.sh

# Cleanup
./scripts/cleanup.sh
```

## SMTP Server

```bash
# Start server
python3 src/email/smtp_server.py --port 1025 --spool ./spool

# Test with netcat
echo -e "EHLO test\r\nQUIT\r\n" | nc localhost 1025

# Test with telnet
telnet localhost 1025

# Python client
python3 src/email/smtp_client.py \
    --server localhost --port 1025 \
    --from "sender@test.local" --to "receiver@test.local" \
    --subject "Test" --body "Hello"
```

### SMTP Commands

| Command | Description | Response Code |
|---------|-------------|---------------|
| HELO/EHLO | Greeting | 250 |
| MAIL FROM:<addr> | Envelope sender | 250 |
| RCPT TO:<addr> | Recipient | 250 |
| DATA | Message start | 354 |
| . (alone on line) | Message end | 250 |
| QUIT | Close | 221 |
| RSET | Reset transaction | 250 |
| NOOP | No operation | 250 |

## JSON-RPC Server

```bash
# Start server
python3 src/rpc/jsonrpc/jsonrpc_server.py --port 6200

# Test with curl
curl -X POST http://localhost:6200/ \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"add","params":[5,3],"id":1}'

# Expected response
{"jsonrpc":"2.0","result":8,"id":1}
```

### Available Methods

| Method | Parameters | Description |
|--------|------------|-------------|
| add | [a, b] | Addition |
| subtract | [a, b] | Subtraction |
| multiply | [a, b] | Multiplication |
| divide | [a, b] | Division |
| echo | ["msg"] | Echo |
| get_time | [] | Server timestamp |
| get_server_info | [] | Server info |
| sort_list | [items, reverse?] | Sorting |

### Batch Request

```bash
curl -X POST http://localhost:6200/ \
    -H "Content-Type: application/json" \
    -d '[
        {"jsonrpc":"2.0","method":"add","params":[1,2],"id":1},
        {"jsonrpc":"2.0","method":"multiply","params":[3,4],"id":2}
    ]'
```

## XML-RPC Server

```bash
# Start server
python3 src/rpc/xmlrpc/xmlrpc_server.py --port 6201

# Test with curl
curl -X POST http://localhost:6201/ \
    -H "Content-Type: text/xml" \
    -d '<?xml version="1.0"?>
<methodCall>
  <methodName>add</methodName>
  <params>
    <param><value><int>15</int></value></param>
    <param><value><int>25</int></value></param>
  </params>
</methodCall>'

# Introspection
python3 -c "
import xmlrpc.client
proxy = xmlrpc.client.ServerProxy('http://localhost:6201/')
print(proxy.system.listMethods())
"
```

## Traffic Capture

```bash
# With tcpdump
sudo tcpdump -i lo -w capture.pcap port 1025 or port 6200

# View
tcpdump -r capture.pcap -A | head -50

# With tshark
tshark -i lo -f "port 1025 or port 6200" -w capture.pcap

# HTTP analysis
tshark -r capture.pcap -Y http
```

## Mininet

```bash
# Start topology
sudo python3 mininet/topo_email_rpc_base.py

# CLI commands
mininet> nodes
mininet> net
mininet> pingall
mininet> xterm client server
mininet> client ping -c 3 10.0.12.100
mininet> exit

# Cleanup
sudo mn -c
```

## Quick Troubleshooting

```bash
# Port occupied?
ss -lntp | grep :6200
lsof -i :6200

# Python process?
ps aux | grep python

# Kill all servers
pkill -f "smtp_server.py|jsonrpc_server|xmlrpc_server"

# Completee cleanup
./scripts/cleanup.sh --full
```

## Common JSON-RPC Errors

| Code | Message | Cause |
|------|---------|-------|
| -32700 | Parse error | Invalid JSON |
| -32600 | Invalid Request | Missing jsonrpc or method |
| -32601 | Method not found | Non-existent method |
| -32602 | Invalid params | Incorrect parameters |
| -32603 | Internal error | Server error |

## Quick References

- RFC 5321: SMTP
- JSON-RPC 2.0: https://www.jsonrpc.org/specification
- XML-RPC: http://xmlrpc.com/spec.md
- Protobuf: https://protobuf.dev/
