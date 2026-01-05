# Lab 9 – Practical Guide: Pseudo-FTP Server Implementation and Testing

## What We Will Accomplish

In this lab session you will put into practice the concepts studied in lecture and Seminar, building step by step a functional environment for file transfer. You will configure the pseudo-FTP server, test basic commands, capture and analyse network traffic, and experiment with multi-client scenarios using Docker.

### Expected Deliverables

At the end of the lab, you will have:
1. A functional pseudo-FTP server, tested locally
2. Traffic captures (.pcap) with documented analyses
3. Docker-orchestrated environment for concurrent testing
4. Optional: Mininet topology for advanced simulations
5. Completed reflective note

---

## Time Structure (estimates)

| Step | Activity | Duration |
|------|----------|----------|
| 0 | Environment setup | 10 min |
| 1 | Endianness and Framing | 15 min |
| 2 | Pseudo-FTP Server | 10 min |
| 3 | Interactive Client | 15 min |
| 4 | Wireshark Capture | 20 min |
| 5 | Docker Multi-Client | 15 min |
| 6 | Mininet (optional) | 20 min |
| 7 | Verification and submission | 10 min |
| **Total** | | **~2h** |

---

## Step 0: Working Environment Setup

### 0.1 Working directory structure

```
starterkit_s9/
├── README.md
├── Makefile
├── requirements.txt
├── python/
│   ├── demos/
│   │   └── ex_9_02_pseudo_ftp.py
│   └── exercises/
│       └── ex_9_01_endianness.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── scripts/
│   ├── setup.sh
│   ├── verify.sh
│   └── capture.sh
├── server-files/
│   ├── document.txt
│   └── sample.bin
├── client-files/
└── pcap/
```

### 0.2 Installing dependencies

```bash
# Navigate to Starter Kit directory
cd starterkit_s9

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python --version    # >= 3.8
docker --version    # >= 20.10
tshark --version    # >= 3.0
```

### 0.3 Quick verification

```bash
make verify
```

**Expected output**:
```
[✓] Python 3.10.12 installed
[✓] Docker 24.0.5 available
[✓] tshark 4.0.3 ready
[✓] All dependencies satisfied
[✓] Server files present
[✓] Environment ready!
```

### 0.4 Possible problems

| Problem | Solution |
|---------|----------|
| `pip: command not found` | Install Python: `sudo apt install python3-pip` |
| `docker: permission denied` | Add user to docker group: `sudo usermod -aG docker $USER` |
| `tshark: command not found` | Install: `sudo apt install tshark` |

**Step 0 Checklist**:
- [ ] The starterkit_s9 directory exists and contains all files
- [ ] `make verify` returns all green checks
- [ ] Terminal available for commands

---

## Step 1: Endianness and Binary Framing

### 1.1 Running the demo

```bash
cd python/exercises
python ex_9_01_endianness.py
```

### 1.2 Expected output

```
╔══════════════════════════════════════════════════════════════╗
║           ENDIANNESS AND FRAMING DEMONSTRATION               ║
╚══════════════════════════════════════════════════════════════╝

═══ Part 1: Endianness ═══

Test number: 0x12345678 (305419896 in decimal)

Big Endian (Network Byte Order):
  Bytes representation: 12 34 56 78
  MSB (Most Significant Byte) first
  Used in: network protocols, network format

Little Endian (Host Byte Order on x86):
  Bytes representation: 78 56 34 12
  LSB (Least Significant Byte) first
  Used in: Intel/AMD processors, ARM (configurable)

═══ Part 2: Packing with struct ═══

pack('>I', 0x12345678) = b'\x12\x34\x56\x78'  # Big Endian
pack('<I', 0x12345678) = b'\x78\x56\x34\x12'  # Little Endian
pack('!I', 0x12345678) = b'\x12\x34\x56\x78'  # Network (= Big)

═══ Part 3: Custom Protocol Header ═══

Header structure (16 bytes):
┌────────────┬────────────┬────────────┬────────────┐
│ Magic (4B) │ Length(4B) │ CRC-32(4B) │ Flags (4B) │
└────────────┴────────────┴────────────┴────────────┘

Example header:
  Magic:  0x46545043 ("FTPC")
  Length: 0x00000100 (256 bytes)
  CRC-32: 0xABCD1234
  Flags:  0x00000001 (compressed)

Resulting bytes: 46 54 50 43 00 00 01 00 AB CD 12 34 00 00 00 01
```

### 1.3 Experimentation

Modify the following in the script and observe the results:

```python
# Change the test number
TEST_NUMBER = 0xDEADBEEF

# Try with negative numbers
SIGNED_NUMBER = -1

# Test strings of different lengths
TEST_STRING = "Computer Networks"
```

### 1.4 Control question

> What would happen if the server uses Big Endian and the client Little Endian for the Length field, without conversion?

**Answer**: If the server sends Length = 256 (0x00000100 in BE), the client reading in LE will interpret it as 0x00010000 = 65536. It will wait for 65536 bytes instead of 256, blocking the transfer.

**Step 1 Checklist**:
- [ ] Script runs without errors
- [ ] I understand the difference between Big/Little Endian
- [ ] I experimented with different values

---

## Step 2: Starting the Pseudo-FTP Server

### 2.1 Starting the server

```bash
cd ../demos
python ex_9_02_pseudo_ftp.py --mode server --port 9021
```

### 2.2 Expected output

```
╔══════════════════════════════════════════════════════════════╗
║             PSEUDO-FTP SERVER v1.0                           ║
╚══════════════════════════════════════════════════════════════╝

[2025-01-01 10:00:00] [INFO] Server configuration:
  - Host: 0.0.0.0
  - Port: 9021
  - Files directory: ./server-files
  - Max connections: 10

[2025-01-01 10:00:00] [INFO] Server started, listening on 0.0.0.0:9021
[2025-01-01 10:00:00] [INFO] Press Ctrl+C to stop
```

### 2.3 Verifying the server (separate terminal)

```bash
# Check that the server is listening
netstat -tlnp | grep 9021
# or
ss -tlnp | grep 9021
```

**Expected output**:
```
tcp   LISTEN  0       10       0.0.0.0:9021      0.0.0.0:*    users:(("python",pid=1234,fd=3))
```

### 2.4 Code analysis (key fragments)

**Header structure**:
```python
HEADER_FORMAT = '>4sIII'  # magic(4s), length(I), crc(I), flags(I)
HEADER_SIZE = 16
MAGIC = b'FTPC'
```

**Sending a message**:
```python
def send_message(sock, payload, compressed=False):
    crc = zlib.crc32(payload) & 0xffffffff
    flags = 1 if compressed else 0
    header = struct.pack(HEADER_FORMAT, MAGIC, len(payload), crc, flags)
    sock.sendall(header + payload)
```

**Step 2 Checklist**:
- [ ] Server starts without errors
- [ ] Port 9021 is in LISTEN state
- [ ] I understood the header structure

---

## Step 3: Interactive Client

### 3.1 Starting the client (new terminal)

```bash
python ex_9_02_pseudo_ftp.py --mode client --host localhost --port 9021
```

### 3.2 Interactive session

Enter commands in the indicated order:

```
pseudo-ftp> AUTH admin:secret123
[OK] Authentication successful. Welcome, admin!

pseudo-ftp> PWD
[OK] Current directory: /

pseudo-ftp> LIST
[OK] Directory listing:
  document.txt    1024 bytes   2025-01-01 09:00
  sample.bin      2048 bytes   2025-01-01 09:00

pseudo-ftp> GET document.txt
[OK] Transfer complete: 1024 bytes
    CRC-32: 0xA1B2C3D4
    Saved to: ./client-files/document.txt

pseudo-ftp> PUT test_upload.txt
[INFO] Reading local file: test_upload.txt
[OK] Upload complete: 512 bytes
    CRC-32: 0xE5F6A7B8

pseudo-ftp> QUIT
[OK] Session closed. Goodbye!
```

### 3.3 Verifying transfers

```bash
# Check downloaded file
ls -at ../client-files/
cat ../client-files/document.txt

# Verify integrity
md5sum ../server-files/document.txt ../client-files/document.txt
```

**Expected output**:
```
d41d8cd98f00b204e9800998ecf8427e  ../server-files/document.txt
d41d8cd98f00b204e9800998ecf8427e  ../client-files/document.txt
```

### 3.4 Testing errors

Test the following scenarios:

```
# Wrong authentication
pseudo-ftp> AUTH wrong:credentials
[ERROR] Authentication failed

# Command without authentication (restart client)
pseudo-ftp> LIST
[ERROR] Not authenticated. Use AUTH first.

# Non-existent file
pseudo-ftp> GET nonexistent.txt
[ERROR] File not found: nonexistent.txt

# Unknown command
pseudo-ftp> INVALID
[ERROR] Unknown command: INVALID
```

**Step 3 Checklist**:
- [ ] Authentication works
- [ ] GET downloads file correctly
- [ ] PUT uploads file to server
- [ ] Errors are handled appropriately

---

## Step 4: Wireshark/tshark Capture and Analysis

### 4.1 Preparing capture (new terminal)

```bash
cd ../pcap
# Start capture on loopback interface
tshark -i lo -f "tcp port 9021" -w session_capture.pcap &
TSHARK_PID=$!
echo "tshark running with PID: $TSHARK_PID"
```

### 4.2 Generating traffic

In a separate terminal, start the server and client, execute some commands (AUTH, LIST, GET, QUIT).

### 4.3 Stopping capture

```bash
kill $TSHARK_PID
sleep 1
ls -at session_capture.pcap
```

### 4.4 Analysing the capture

**General view**:
```bash
tshark -r session_capture.pcap | head -30
```

**Example output**:
```
    1   0.000000    127.0.0.1 → 127.0.0.1    TCP 74 58294 → 9021 [SYN] Seq=0
    2   0.000012    127.0.0.1 → 127.0.0.1    TCP 74 9021 → 58294 [SYN, ACK]
    3   0.000018    127.0.0.1 → 127.0.0.1    TCP 66 58294 → 9021 [ACK]
    4   0.001234    127.0.0.1 → 127.0.0.1    TCP 98 58294 → 9021 [PSH, ACK] Len=32
    5   0.001456    127.0.0.1 → 127.0.0.1    TCP 82 9021 → 58294 [PSH, ACK] Len=16
```

**Extracting packets with payload**:
```bash
tshark -r session_capture.pcap -Y "tcp.len > 0" \
    -T fields -e frame.number -e tcp.srcport -e tcp.dstport -e tcp.len
```

**Hexadecimal view**:
```bash
tshark -r session_capture.pcap -Y "tcp.len > 0" -x | head -50
```

### 4.5 Identifying protocol elements

Search in hexadecimal output:

| Element | Hex value | Meaning |
|---------|-----------|---------|
| Magic bytes | `46 54 50 43` | "FTPC" in ASCII |
| Length | `00 00 00 XX` | Payload length |
| TCP Handshake | SYN, SYN-ACK, ACK | First 3 packets |
| Termination | FIN, FIN-ACK, ACK | Last packets |

### 4.6 Saving the analysis

```bash
# Create a text report
tshark -r session_capture.pcap > analysis_report.txt
echo "=== Statistics ===" >> analysis_report.txt
tshark -r session_capture.pcap -z io,stat,1 >> analysis_report.txt
```

**Step 4 Checklist**:
- [ ] .pcap file was generated
- [ ] I identified the TCP handshake (SYN, SYN-ACK, ACK)
- [ ] I found magic bytes "FTPC" in payload
- [ ] I saved the analysis report

---

## Step 5: Multi-Client Testing with Docker

### 5.1 Checking Docker configuration

```bash
cd ../docker
cat docker-compose.yml
```

**Expected structure**:
```yaml
version: '3.8'
services:
  ftp-server:
    build: .
    ports:
      - "9021:9021"
    volumes:
      - ../server-files:/data
    command: python /app/ex_9_02_pseudo_ftp.py --mode server
    
  client-1:
    build: .
    depends_on:
      - ftp-server
    command: python /app/client_test.py --host ftp-server --tasks get
    
  client-2:
    build: .
    depends_on:
      - ftp-server
    command: python /app/client_test.py --host ftp-server --tasks put
    
  client-3:
    build: .
    depends_on:
      - ftp-server
    command: python /app/client_test.py --host ftp-server --tasks mixed
```

### 5.2 Starting orchestration

```bash
# Build images
docker compose build

# Start all services
docker compose up
```

### 5.3 Expected output

```
[+] Running 4/4
 ✔ Container docker-ftp-server-1  Created
 ✔ Container docker-client-1-1    Created
 ✔ Container docker-client-2-1    Created
 ✔ Container docker-client-3-1    Created

ftp-server-1  | [INFO] Server started on 0.0.0.0:9021
client-1-1    | [INFO] Connecting to ftp-server:9021...
client-2-1    | [INFO] Connecting to ftp-server:9021...
client-3-1    | [INFO] Connecting to ftp-server:9021...
ftp-server-1  | [INFO] Client connected from 172.18.0.3
ftp-server-1  | [INFO] Client connected from 172.18.0.4
ftp-server-1  | [INFO] Client connected from 172.18.0.5
client-1-1    | [OK] AUTH successful
client-2-1    | [OK] AUTH successful
client-3-1    | [OK] AUTH successful
client-1-1    | [OK] GET document.txt completed (1024 bytes)
client-2-1    | [OK] PUT test_from_client2.txt completed (512 bytes)
client-3-1    | [OK] LIST completed
client-3-1    | [OK] GET sample.bin completed (2048 bytes)
client-1-1    | [INFO] All tasks completed. Disconnecting.
client-2-1    | [INFO] All tasks completed. Disconnecting.
client-3-1    | [INFO] All tasks completed. Disconnecting.
```

### 5.4 Verifying results

```bash
# Check files created on server
docker compose exec ftp-server ls -at /data

# Check logs individually
docker compose logs client-1
docker compose logs client-2
```

### 5.5 Cleanup

```bash
docker compose down -v
docker system prune -f
```

**Step 5 Checklist**:
- [ ] `docker compose build` succeeds
- [ ] All 3 clients connect
- [ ] Transfers are complete
- [ ] Cleanup performed

---

## Step 6: Mininet Topology (Optional)

### 6.1 Verifying Mininet

```bash
# Check installation
sudo mn --version

# Quick test
sudo mn --test pingall
```

### 6.2 Starting custom topology

```bash
cd ../mininet/topologies
sudo python topo_base.py
```

### 6.3 Commands in Mininet CLI

```
mininet> nodes
available nodes are: h1 h2 s1

mininet> h1 ifconfig
h1-eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>
    inet 10.0.0.1  netmask 255.0.0.0

mininet> h2 ifconfig
h2-eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>
    inet 10.0.0.2  netmask 255.0.0.0

mininet> pingall
*** Ping: testing ping reachability
h1 -> h2
h2 -> h1
*** Results: 0% dropped (2/2 received)
```

### 6.4 Running server in Mininet

```
mininet> h1 python /path/to/ex_9_02_pseudo_ftp.py --mode server --port 9021 &
mininet> h2 python /path/to/ex_9_02_pseudo_ftp.py --mode client --host 10.0.0.1 --port 9021
```

### 6.5 Adding latency

```
mininet> sh tc qdisc add dev s1-eth1 root netem delay 50ms
mininet> h1 ping -c 3 h2
PING 10.0.0.2: 64 bytes icmp_seq=1 ttl=64 time=100.2 ms
```

**Step 6 Checklist** (optional):
- [ ] Mininet starts correctly
- [ ] Ping between h1 and h2 works
- [ ] I tested the server between Mininet hosts
- [ ] I experimented with artificial latency

---

## Step 7: Final Verification and Submission

### 7.1 Complete smoke test

```bash
cd ..
make clean
make setup
make run-demo
make capture
make verify
```

**Expected output**:
```
=== Clean ===
[OK] Removed temporary files

=== Setup ===
[OK] Dependencies installed
[OK] Directories created

=== Run Demo ===
[OK] Server started
[OK] Client executed commands
[OK] Transfer verified

=== Capture ===
[OK] PCAP file generated (2.5 KB)

=== Verify ===
[✓] All checks passed!
```

### 7.2 Final checklist for submission

**Required artefacts**:
- [ ] `pcap/session_capture.pcap` - traffic capture
- [ ] `pcap/analysis_report.txt` - documented analysis
- [ ] `client-files/document.txt` - correctly downloaded file
- [ ] Screenshots with:
  - [ ] Server started output
  - [ ] Interactive client session
  - [ ] Docker compose logs
  - [ ] (optional) Mininet pingall

**Reflective note** (5-10 lines):
- What new things did I learn in this lab?
- What difficulties did I encounter and how did I solve them?
- How does this lab connect to other subjects or personal projects?

### 7.3 Reflective note template

```markdown
## Reflective Note - Lab 9

**Student**: [Surname First name]
**Group**: [Group]
**data**: [data]

### What I learned
[Describe 2-3 new concepts or techniques you assimilated]

### Difficulties encountered
[Mention problems and solutions found]

### Connections
[How it relates to other disciplines or projects]

### Additional observations
[Any other relevant comments]
```

---

## What We Learned

After completing this lab, you have gained practical experience in:

1. **Environment configuration**: Systematic setup for networking development and testing
2. **Protocol implementation**: Using struct for binary packets, CRC for integrity
3. **Network debugging**: Traffic capture and interpretation with tshark
4. **Containerisation**: Service orchestration with Docker Compose
5. **Simulation**: Optionally, using Mininet for virtual topologies

---

## How It Helps Us

The competencies from this lab are directly applicable in:

- **Backend development**: Implementing and testing microservices
- **DevOps**: CI/CD for distributed applications
- **Security**: Network traffic analysis and auditing
- **Embedded/IoT**: Custom protocols for devices

---

## Additional Resources

- tshark documentation: https://www.wireshark.org/docs/man-pages/tshark.html
- Docker Compose: https://docs.docker.com/compose/
- Mininet Walkthrough: http://mininet.org/walkthrough/
- Python struct module: https://docs.python.org/3/library/struct.html
