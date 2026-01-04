# Laboratory 12: Email & RPC Experiments

> **Course:** Computer Networks  
> **Week:** 12 of 14  
> **Duration:** 2 hours  
> **Author:** Revolvix&Hypotheticalandrei

---

## Objectives

After completeing this laboratory, you will be able to:
1. Run and analyse a completee SMTP session
2. Capture and interpret email traffic with tshark
3. Implement and test JSON-RPC calls
4. Compare JSON-RPC vs XML-RPC performance
5. Identify and resolve common errors

---

## Prerequisites

- Python 3.8+
- Wireshark/tshark installed
- Starterkit extracted
- TCP/HTTP knowledge from previous weeks

---

## Step 0: Environment Setup

### 0.1 Starterkit Structure

```
s12_starterkit/
├── Makefile              # Automation
├── README.md             # Documentation
├── requirements.txt      # Python dependencies
├── src/
│   ├── email/           # SMTP server/client
│   │   ├── smtp_server.py
│   │   └── smtp_client.py
│   └── rpc/
│       ├── jsonrpc/     # JSON-RPC implementation
│       └── xmlrpc/      # XML-RPC implementation
├── exercises/           # Self-contained exercises
├── scripts/             # Shell scripts
└── docs/                # HTML presentations
```

### 0.2 Install Dependencies

```bash
cd s12_starterkit

# Check Python
python3 --version

# Install dependencies
make setup

# Verify installation
make verify
```

**Expected output:**
```
✓ Python 3.x detected
✓ tshark available
✓ All dependencies installed
✓ Environment ready
```

---

## Step 1: Educational SMTP Server

### 1.1 Start Server

Open **Terminal 1**:

```bash
python src/email/smtp_server.py --port 1025 --verbose
```

**Expected output:**
```
[INFO] SMTP Server starting on localhost:1025
[INFO] Verbose mode enabled
[INFO] Waiting for connections...
```

### 1.2 What the Server Does

- Listens on port 1025 (non-privileged, does not require sudo)
- Implements essential SMTP commands (EHLO, MAIL FROM, RCPT TO, DATA, QUIT)
- Displays completee conversation in verbose mode
- Stores messages in memory (for demonstration)

### 1.3 Available Options

| Option | Description | Default |
|--------|-------------|---------|
| `--port` | Listening port | 1025 |
| `--host` | Bind address | localhost |
| `--verbose` | Display conversation | False |
| `--maildir` | Storage directoryy | ./mailbox |

---

## Step 2: SMTP Client

### 2.1 Send Simple Email

In **Terminal 2**:

```bash
python src/email/smtp_client.py \
    --server localhost \
    --port 1025 \
    --from alice@test.local \
    --to bob@test.local \
    --subject "Test SMTP Laboratory" \
    --body "This is a test message for the networks laboratory."
```

**Expected output:**
```
[INFO] Connecting to localhost:1025
[INFO] EHLO sent, server capabilities: SIZE, 8BITMIME
[INFO] MAIL FROM accepted
[INFO] RCPT TO accepted
[INFO] DATA accepted
[INFO] Message queued successsfully (ID: abc123)
[INFO] Connection closed
```

### 2.2 Verify on Server

In Terminal 1, you will see:

```
[CLIENT] Connected from 127.0.0.1:54321
[RECV] EHLO localhost
[SEND] 250-smtp.test.local Hello localhost
[SEND] 250-SIZE 10485760
[SEND] 250 8BITMIME
[RECV] MAIL FROM:<alice@test.local>
[SEND] 250 OK
[RECV] RCPT TO:<bob@test.local>
[SEND] 250 OK
[RECV] DATA
[SEND] 354 Start mail input; end with <CRLF>.<CRLF>
[RECV] From: alice@test.local
[RECV] To: bob@test.local
[RECV] Subject: Test SMTP Laboratory
[RECV] 
[RECV] This is a test message for the networks laboratory.
[RECV] .
[SEND] 250 OK id=msg_001
[RECV] QUIT
[SEND] 221 Bye
[CLIENT] Disconnected
```

### 2.3 List Messages

```bash
python src/email/smtp_client.py --list
```

---

## Step 3: SMTP Traffic Capture

### 3.1 Start Capture

In **Terminal 3** (before sending email):

```bash
sudo tshark -i lo -f "port 1025" -Y smtp -V 2>&1 | head -100
```

Or save to file:

```bash
sudo tshark -i lo -f "port 1025" -w smtp_capture.pcap
```

### 3.2 Send Email (in another terminal)

```bash
python src/email/smtp_client.py \
    --server localhost --port 1025 \
    --from sender@demo.local \
    --to receiver@demo.local \
    --subject "Captured Email" \
    --body "This email was captured with tshark"
```

### 3.3 Capture Analysis

Stop tshark (Ctrl+C) and analyse:

```bash
# Display SMTP conversation
tshark -r smtp_capture.pcap -Y smtp -T fields \
    -e frame.number -e smtp.req.command -e smtp.response.code

# Follow TCP stream
tshark -r smtp_capture.pcap -z "follow,tcp,ascii,0"
```

**What to observe:**
- Command sequence (EHLO → MAIL FROM → RCPT TO → DATA → QUIT)
- Response codes (220, 250, 354, 221)
- Difference between envelope (MAIL FROM) and headers (From:)

---

## Step 4: JSON-RPC Server

### 4.1 Start Server

In **Terminal 1**:

```bash
python src/rpc/jsonrpc/jsonrpc_server.py --port 8000 --verbose
```

**Output:**
```
[INFO] JSON-RPC 2.0 Server starting on http://localhost:8000
[INFO] Available methods: add, subtract, multiply, divide, echo, system.listMethods
[INFO] Press Ctrl+C to stop
```

### 4.2 Available Methods

| Method | Parameters | Description |
|--------|------------|-------------|
| `add` | a, b | Returns a + b |
| `subtract` | a, b | Returns a - b |
| `multiply` | a, b | Returns a * b |
| `divide` | a, b | Returns a / b |
| `echo` | message | Returns the received message |
| `system.listMethods` | - | Lists available methods |

---

## Step 5: JSON-RPC Client

### 5.1 Demo Mode

```bash
python src/rpc/jsonrpc/jsonrpc_client.py --demo
```

**Output:**
```
=== JSON-RPC 2.0 Demo ===

1. Single call: add(2, 3)
   Result: 5

2. Single call: subtract(10, 4)
   Result: 6

3. Named params: divide(dividend=20, divisor=4)
   Result: 5.0

4. Batch request: [add(1,2), multiply(3,4), divide(10,2)]
   Results: [3, 12, 5.0]

5. Error handling: divide(10, 0)
   Error: -32603 Division by zero

6. Method not found: unknown_method()
   Error: -32601 Method not found
```

### 5.2 Individual Calls

```bash
# Simple call
python src/rpc/jsonrpc/jsonrpc_client.py \
    --method add --params 42 23

# With named parameters
python src/rpc/jsonrpc/jsonrpc_client.py \
    --method divide --kwargs '{"dividend": 100, "divisor": 5}'
```

### 5.3 Batch Requests

```bash
python src/rpc/jsonrpc/jsonrpc_client.py --batch \
    "add,1,2" "multiply,3,4" "subtract,10,5"
```

---

## Step 6: XML-RPC Server

### 6.1 Start Server

In **Terminal 2**:

```bash
python src/rpc/xmlrpc/xmlrpc_server.py --port 8001
```

### 6.2 Test Client

```bash
# Demo mode
python src/rpc/xmlrpc/xmlrpc_client.py --demo

# Introspection
python src/rpc/xmlrpc/xmlrpc_client.py --list-methods
```

**Introspection output:**
```
Available methods:
- add(a, b): Returns the sum of a and b
- subtract(a, b): Returns the difference a - b
- multiply(a, b): Returns the product of a and b
- divide(a, b): Returns the quotient a / b
- system.listMethods(): Lists all available methods
- system.methodHelp(method): Returns help for a method
```

---

## Step 7: RPC Benchmark

### 7.1 Run Benchmark

```bash
make benchmark-rpc
```

Or manually:

```bash
python scripts/benchmark_rpc.py --iterations 1000
```

### 7.2 Typical Output

```
=== RPC Benchmark Results ===

Configuredion:
  Iterations: 1000
  Method: add(random_int, random_int)

JSON-RPC Results:
  Total time: 0.89s
  Throughput: 1123 calls/sec
  Average latency: 0.89ms
  Average request size: 67 bytes
  Average response size: 45 bytes

XML-RPC Results:
  Total time: 1.34s
  Throughput: 746 calls/sec
  Average latency: 1.34ms
  Average request size: 198 bytes
  Average response size: 156 bytes

Comparison:
  JSON-RPC is 1.51x faster
  JSON-RPC requests are 66% smaller
  JSON-RPC responses are 71% smaller
```

### 7.3 Results Interpretation

| Metric | JSON-RPC | XML-RPC | Difference |
|--------|----------|---------|------------|
| Throughput | Higher | Lower | JSON ~50% faster |
| Payload | Small | Large | XML ~3x larger |
| Parsing | Fast | Slow | JSON parsing native in Python |

---

## Step 8: RPC Traffic Capture

### 8.1 JSON-RPC Capture

```bash
# Terminal 3
sudo tshark -i lo -f "port 8000" -Y "http.request or http.response" \
    -T fields -e frame.number -e http.request.method \
    -e http.content_length -e http.response.code
```

### 8.2 XML-RPC Capture

```bash
sudo tshark -i lo -f "port 8001" -Y "http contains methodCall" -V
```

### 8.3 What to Compare

1. **Payload size**: `http.content_length`
2. **XML vs JSON structure**: Follow TCP stream for each
3. **HTTP overhead**: Headers are identical, only body differs

---

## Step 9: Final Exercises

### Exercise 1: Multi-recipient SMTP (★★☆)

Modify the send command for 3 recipients:

```bash
python src/email/smtp_client.py \
    --server localhost --port 1025 \
    --from alice@test.local \
    --to bob@test.local carol@test.local david@test.local \
    --subject "Multi-recipient test" \
    --body "This goes to three people"
```

**Verify:** How many RCPT TO commands appear in the conversation?

### Exercise 2: JSON-RPC Error Handling (★★☆)

Test error behaviour:

```bash
# Non-existent method
curl -X POST http://localhost:8000 \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"unknown","id":1}'

# Invalid JSON
curl -X POST http://localhost:8000 \
    -H "Content-Type: application/json" \
    -d 'not valid json'

# Wrong parameters
curl -X POST http://localhost:8000 \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"add","params":["a","b"],"id":1}'
```

**Document:** The error codes received for each case.

### Exercise 3: Batch Performance (★★★)

Compare:
- 100 individual calls
- 10 batches of 10 requests each

```bash
python exercises/ex_02_rpc.py --exercise batch-performance
```

### Exercise 4: Challenge - Email with Attachment (★★★★)

Extend `smtp_client.py` to send an attached file.

Hint: Use `email.mime` from the Python standard library.

---

## Final Checklist

- [ ] SMTP server started and tested
- [ ] Email sent and verified in log
- [ ] tshark capture completeed for SMTP
- [ ] JSON-RPC server functional
- [ ] JSON-RPC client tested (single, batch, errors)
- [ ] XML-RPC server started
- [ ] Benchmark run and interpreted
- [ ] Exercise 1 completeed
- [ ] Exercise 2 completeed

---

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Connection refused` | Server not running | Verify server is started on correct port |
| `Permission denied` (tshark) | Missing privileges | Use `sudo` or configure capabilities |
| `Port already in use` | Another process on port | Change port or stop existing process |
| `Module not found` | Missing dependencies | Run `make setup` |

### Useful Commands

```bash
# Check what's listening on a port
lsof -i :8000

# Stop process on port
kill $(lsof -t -i:8000)

# Check connectivity
nc -zv localhost 1025
```

---

*Document generated for educational use | Revolvix&Hypotheticalandrei*
