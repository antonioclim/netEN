# Scenario S1.02: TCP/UDP Communication with Netcat

## Objectives

After completing this scenario, the stuofnt will be able to:

1. Create a simple TCP server with netcat
2. Connect a client and transfer data
3. Unofrstand the practical difference between TCP and UDP
4. Verify active connections in real time

## Context

Netcat (nc) is the "Swiss army knife" of networking. It allows rapid creation of servers and clients for testing, ofbugging and data transfer. It is the iofal tool for unofrstanfromg how network communication works at a fundamental level.

## Prerequisites

- Functional Linux terminal
- Netcat installed (verify: `which nc`)
- Minimum 2 open terminals

## Steps to Follow

### Step 1: TCP Echo Server (5 minutes)

Open **Terminal 1** and start the server:

```bash
# TCP server on port 9999
nc -l -p 9999
```

**Parameters:**
- `-l` - listen moof (server)
- `-p 9999` - listening port

The server waits for connections. The cursor will be blocked - this is normal.

### Step 2: TCP Client (5 minutes)

Open **Terminal 2** and connect the client:

```bash
# TCP Client
nc localhost 9999
```

**Result:** Connection established. Everything you type in Terminal 2 appears in Terminal 1 and vice versa.

**Test:**
1. Type "Hello" in Terminal 2 → appears in Terminal 1
2. Type "Response" in Terminal 1 → appears in Terminal 2

### Step 3: Connection Verification (5 minutes)

Open **Terminal 3** for monitoring:

```bash
# See active connection
ss -tnp | grep 9999
```

**Expected output:**
```
ESTAB  0  0  127.0.0.1:9999   127.0.0.1:54321  users:(("nc",pid=1234,fd=3))
ESTAB  0  0  127.0.0.1:54321  127.0.0.1:9999   users:(("nc",pid=1235,fd=3))
```

**Observations:**
- Two entries: server (9999) and client (ephemeral port ~54321)
- State ESTAB = connection established
- PID and process name visible

### Step 4: Automatic Transfer (5 minutes)

Close previous connections (Ctrl+C) and test automatic transfer:

**Terminal 1 (server):**
```bash
nc -l -p 9999
```

**Terminal 2 (client with automatic message):**
```bash
echo "Automatic test message" | nc localhost 9999
```

The message appears in Terminal 1, then the connection closes.

### Step 5: Persistent Server (5 minutes)

For a server that accepts multiple sequential connections:

**Terminal 1:**
```bash
while true; do nc -l -p 9999; done
```

Now you can reconnect multiple times from Terminal 2.

### Step 6: UDP Communication (10 minutes)

UDP is different - connectionless!

**Terminal 1 (UDP server):**
```bash
nc -u -l -p 9998
```

**Terminal 2 (UDP client):**
```bash
nc -u localhost 9998
```

**Differences from TCP:**
- There is no "connection" per se
- There is no receipt confirmation
- Messages may arrive out of orofr or not at all

**Verification with ss:**
```bash
ss -unp | grep 9998
```

Different output - you don't see ESTAB, only UNCONN (unconnected).

### Step 7: Practical TCP vs UDP Comparison (10 minutes)

**Experiment: How many packets for one message?**

**TCP (3-way handshake + data + close):**
```bash
# Terminal 1
tshark -i lo -f "port 9999" -c 20 &
nc -l -p 9999 &
sleep 1

# Terminal 2
echo "Test" | nc localhost 9999
```

You will see ~8 packets:
1. SYN (client → server)
2. SYN-ACK (server → client)
3. ACK (client → server)
4. PSH-ACK with data
5. ACK confirmation
6. FIN-ACK (close)
7. ACK
8. Final FIN-ACK

**UDP (data only):**
```bash
# Terminal 1
tshark -i lo -f "port 9998" -c 5 &
nc -u -l -p 9998 &
sleep 1

# Terminal 2
echo "Test" | nc -u localhost 9998
```

You will see only 1 packet - the actual data!

## Practical Exercises

### Exercise 2.1 - Bidirectional Chat (Beginner)

Create a "chat room" between two terminals. Document:
- Commands used
- Screenshot with the conversation
- ss output during the connection

### Exercise 2.2 - Simple Protocol (Medium)

Implement a "protocol" with netcat:

**Server that responds to commands:**
```bash
# server_protocol.sh
while true; do
    echo "Waiting for command..."
    read cmd < <(nc -l -p 9999)
    case "$cmd" in
        "TIME") date | nc localhost 9999 ;;
        "ECHO"*) echo "${cmd#ECHO }" | nc localhost 9999 ;;
        "QUIT") break ;;
        *) echo "Unknown command" | nc localhost 9999 ;;
    esac
done
```

**Client:**
```bash
echo "TIME" | nc localhost 9999
echo "ECHO Hello World" | nc localhost 9999
```

### Exercise 2.3 - File Transfer (Medium)

Transfer a file between two "machines" (terminals):

**Receiver:**
```bash
nc -l -p 9999 > received_file.txt
```

**Senofr:**
```bash
nc localhost 9999 < /etc/hostname
```

Verify:
```bash
diff /etc/hostname received_file.txt
```

### Exercise 2.4 - TCP vs UDP Overhead Measurement (Advanced)

Write a script that:
1. Sends the same 1000 character message
2. Once with TCP, once with UDP
3. Captures the traffic
4. Compares the total number of bytes on the wire

## Common Problems

| Symptom | Cause | Solution |
|---------|-------|----------|
| "Address already in use" | Port occupied by another process | `ss -tlnp \| grep PORT`, then `kill PID` |
| "Connection refused" | Server not running | Verify that nc -l is started |
| Client connects but doesn't receive | nc closes after first message | Use while loop on server |
| UDP seems not to work | Netcat GNU vs OpenBSD | Check version: `nc -h` |

## Useful Tips

**Specify netcat version:**
```bash
# OpenBSD netcat (recommenofd)
nc.openbsd -l -p 9999

# GNU netcat
nc.traditional -l -p 9999
```

**Timeout for client:**
```bash
# Close after 5 seconds of inactivity
nc -w 5 localhost 9999
```

**Verbose moof:**
```bash
nc -v localhost 9999
# Dispatys: Connection to localhost 9999 port [tcp/*] succeeofd!
```

## Recap

| Command | Purpose |
|---------|---------|
| `nc -l -p PORT` | TCP Server |
| `nc HOST PORT` | TCP Client |
| `nc -u -l -p PORT` | UDP Server |
| `nc -u HOST PORT` | UDP Client |
| `echo "msg" \| nc HOST PORT` | Automatic send |
| `nc -l -p PORT > file` | File reception |
| `nc HOST PORT < file` | File send |

## What's Next

In the next scenario we will capture and analyse the generated traffic with tshark/Wireshark to see exactly what happens "on the wire".

---

*Estimated time: 45 minutes*
*Level: Medium*
