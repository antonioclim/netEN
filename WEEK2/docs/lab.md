# Laboratory 2: Step-by-Step Guide

**Practical exercises for Week 2**

---

## Step 0: Environment Preparation

### 0.1 System Verification

```bash
# Navigate to the kit directory
cd starterkit_s2

# Automatic verification
make verify
```

**Expected output**:
```
[VERIFY] Working environment verification...
  Python3:    Python 3.10.12
  Mininet:    2.3.0
  tshark:     TShark (Wireshark) 3.6.2
  tcpdump:    tcpdump version 4.99.1
  
  ✓ ex_2_01_tcp.py
  ✓ ex_2_02_udp.py
  ✓ topo_2_base.py
[VERIFY] ✓ Complete
```

### 0.2 If Dependencies Are Missing

```bash
make setup
```

### 0.3 Previous Sessions Cleanup

```bash
sudo mn -c
make clean
```

---

## Step 1: Quick TCP Demo

### 1.1 Start server (Terminal 1)

```bash
make tcp-server
```

**Expected output**:
```
[TCP-server] Starting on 0.0.0.0:9090...
[14:30:00.123][server] TCP on 0.0.0.0:9090 | mode=threaded
[14:30:00.124][server] Waiting for connections... (Ctrl+C to stop)
```

### 1.2 Send Message (Terminal 2)

```bash
make tcp-client MSG="Hello server"
```

**Expected output**:
```
[TCP-client] Sending to 127.0.0.1:9090...
[14:30:05.456][client] RX 16B in 1.2ms: b'OK: HELLO server'
```

### 1.3 Observe server Log

In Terminal 1, appears:
```
[14:30:05.455][MAIN] New connection: 127.0.0.1:54321
[14:30:05.456][Worker-54321] RX   12B from 127.0.0.1:54321: b'Hello server'
[14:30:05.456][Worker-54321] TX   16B to 127.0.0.1:54321: b'OK: HELLO server'
```

### 1.4 Stop server

In Terminal 1: `Ctrl+C`

---

## Step 2: Quick UDP Demo

### 2.1 Start UDP server (Terminal 1)

```bash
make udp-server
```

### 2.2 Interactive client (Terminal 2)

```bash
make udp-client
```

**Interactive session**:
```
[UDP-client] Interactive client to 127.0.0.1:9091...
> ping
PONG (RTT: 0.5ms)

> upper:hello world
HELLO WORLD (RTT: 0.6ms)

> exit
--- Stats: sent=2, received=2, timeouts=0 ---
```

---

## Step 3: Complete Demo with Capture

### 3.1 Run Complete Demo

```bash
make demo-all
```

This target:
1. Starts TCP server
2. Starts tcpdump capture for TCP
3. Sends TCP messages
4. Stops capture and TCP server
5. Repeats for UDP

### 3.2 TCP Capture Analysis

```bash
make analyze-tcp
```

**Expected output**:
```
[ANALYZE] TCP capture analysis...

  Frame | Source IP    | port | Dest IP      | port | Flags
  ------|--------------|------|--------------|------|------
  1     127.0.0.1     45678  127.0.0.1     9090  ··········S·
  2     127.0.0.1     9090   127.0.0.1     45678 ·······A··S·
  3     127.0.0.1     45678  127.0.0.1     9090  ·······A····
  ...

[ANALYZE] TCP handshake (SYN, SYN-ACK, ACK) identifiable in the first 3 packets
```

### 3.3 UDP Capture Analysis

```bash
make analyze-udp
```

**Observation**: UDP has no handshake - just direct request and response.

---

## Step 4: Mininet Laboratory

### 4.1 Start Topology

```bash
make mininet-cli
```

### 4.2 Exploration

```
mininet> nodes
mininet> net
mininet> pingall
```

### 4.3 TCP server in Mininet

```
mininet> h1 python3 -u seminar/python/exercises/ex_2_01_tcp.py server --bind 10.0.2.100 --port 9090 &
mininet> h2 python3 seminar/python/exercises/ex_2_01_tcp.py client --host 10.0.2.100 --port 9090 -m "Mininet Test"
```

### 4.4 Capture in Mininet

```
mininet> h1 tcpdump -i h1-eth0 -w /tmp/mininet_tcp.pcap 'tcp port 9090' &
mininet> h2 python3 seminar/python/exercises/ex_2_01_tcp.py client --host 10.0.2.100 --port 9090 -m "With capture"
mininet> kill %2
```

Analysis after exiting Mininet:
```bash
tshark -r /tmp/mininet_tcp.pcap -Y tcp
```

### 4.5 Exit and Cleanup

```
mininet> exit
```
```bash
sudo mn -c
```

---

## Step 5: Extended Topology (router)

### 5.1 Start

```bash
make mininet-extended
```

### 5.2 Verify Communication Between Subnets

```
mininet> h1 ping -c 2 10.0.2.3
mininet> h1 traceroute -n 10.0.2.3
```

### 5.3 server Between Subnets

```
mininet> h1 python3 -u seminar/python/exercises/ex_2_01_tcp.py server --bind 10.0.1.1 --port 9090 &
mininet> h3 python3 seminar/python/exercises/ex_2_01_tcp.py client --host 10.0.1.1 --port 9090 -m "Cross-subnet"
```

---

## Step 6: Exercises to Complete

### 6.1 TCP server Template

Open `seminar/python/templates/tcp_server_template.py` and complete:

```python
# TODO 1: Display client IP:port
print(f"Connected: {addr[0]}:{addr[1]}")

# TODO 2: Receive data
data = conn.recv(1024)

# TODO 3: Build response
response = b"OK: " + data.upper()

# TODO 4: Send response
conn.sendall(response)
```

**Test**:
```bash
python3 seminar/python/templates/tcp_server_template.py &
echo "test" | nc 127.0.0.1 12345
# Expected: OK: TEST
```

### 6.2 UDP server Template

Open `seminar/python/templates/udp_server_template.py` and complete the protocol:

```python
# TODO: Implement protocol
msg = data.decode('utf-8').strip()
if msg == "ping":
    response = b"PONG"
elif msg.startswith("upper:"):
    response = msg[6:].upper().encode()
else:
    response = b"UNKNOWN COMMAND"
```

---

## Step 7: Final Verification

### 7.1 Checklist

- [ ] `make verify` passes without errors
- [ ] `make demo-all` runs completely
- [ ] `make analyze-tcp` shows handshake (SYN, SYN/ACK, ACK)
- [ ] `make analyze-udp` shows direct request/response
- [ ] Mininet `pingall` = 0% dropped
- [ ] TCP template functional
- [ ] UDP template functional

### 7.2 Final Cleanup

```bash
make reset
```

---

## Expected Results

### TCP Capture (handshake)

```
1. client → server: SYN           (Connection initiation)
2. server → client: SYN-ACK       (Accept + acknowledgement)
3. client → server: ACK           (Final acknowledgement)
4. client → server: PSH-ACK       (Application data)
5. server → client: ACK           (Data acknowledgement)
6. server → client: PSH-ACK       (Response)
7. client → server: ACK           (Response acknowledgement)
...
n. FIN, FIN-ACK, ACK              (Connection close)
```

### UDP Capture

```
1. client → server: Datagram      (Request)
2. server → client: Datagram      (Response)
```

**Fundamental difference**: TCP has overhead for reliability, UDP is minimal but without guarantees.

---

## What-If: Modifications and Effects

| Modification | Effect |
|--------------|--------|
| `--mode iterative` for TCP server | Only one client at a time |
| port occupied | `Address already in use` |
| server stopped | `Connection refused` |
| Capture on wrong interface | Empty PCAP |
| Small timeout on client | Lost messages |
| Small recv buffer | Truncated data |

---

*Revolvix&Hypotheticalandrei*
