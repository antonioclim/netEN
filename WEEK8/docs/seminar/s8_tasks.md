# Seminar 8 – Practical Tasks
## HTTP Server + Reverse Proxy

---

## Preparation

### Dependency check

```bash
# Check Python
python3 --version

# Check curl
curl --version

# Check tcpdump (requires sudo)
which tcpdump

# (Optional) Check Docker
docker --version
```

### Directory structure

```bash
cd starterkit_s8
chmod +x scripts/*.sh scenarios/*/*.sh
./tests/smoke_test.sh
```

---

## Part I: HTTP Server (45 min)

### Task 1.1: Run demo server (10 min)

**Objective**: Understanding the minimal HTTP server operation.

```bash
# Terminal 1: Start the server
cd python/demos
python3 demo_http_server.py --host 127.0.0.1 --port 8080 --www ../exercises/www

# Terminal 2: Tests with curl
curl -v http://127.0.0.1:8080/
curl -v http://127.0.0.1:8080/index.html
curl -v http://127.0.0.1:8080/hello.txt
curl -v http://127.0.0.1:8080/not-found
```

**Questions:**
1. What status code do you receive for `/`? Why?
2. What status code do you receive for `/not-found`?
3. What header indicates the server that responded?

---

### Task 1.2: TCP handshake capture (15 min)

**Objective**: Visualising the three-way handshake in real traffic.

```bash
# Terminal 1: Capture
sudo tcpdump -i lo port 8080 -nn -c 20

# Terminal 2: Server (if not already running)
python3 demo_http_server.py --port 8080

# Terminal 3: Client
curl http://127.0.0.1:8080/
```

**What you need to observe:**
- SYN packet (flag [S])
- SYN-ACK packet (flag [S.])
- ACK packet (flag [.])
- Data packets (flag [P.])
- FIN packets (flag [F.])

**Complete:**
```
Handshake:
  1. Client → Server: SYN, Seq=_____
  2. Server → Client: SYN-ACK, Seq=_____, Ack=_____
  3. Client → Server: ACK, Seq=_____, Ack=_____

Observations:
_________________________________________________
_________________________________________________
```

---

### Task 1.3: HTTP server exercise implementation (20 min)

**Objective**: Completing the HTTP server from the exercises.

Open the file `python/exercises/ex_01_http_server.py` and complete the sections marked with `# TODO`.

```python
# In ex_01_http_server.py

def handle_client(conn, addr, www_root, backend_id):
    """
    TODO 1: Read the request from the client
    Hint: use read_until() from utils
    """
    raw = # TODO: call read_until
    
    """
    TODO 2: Parse the request
    Hint: use parse_http_request() from utils
    """
    req = # TODO: call parse_http_request
    
    """
    TODO 3: Validate the method (only GET and HEAD allowed)
    Hint: if the method is not valid, send 405
    """
    if req.method not in ("GET", "HEAD"):
        # TODO: send 405 response
        pass
    
    """
    TODO 4: Map target to file path
    Hint: use safe_map_target_to_path()
    """
    filepath, error = # TODO: call safe_map_target_to_path
    
    # Rest of the implementation...
```

**Verification:**
```bash
python3 ex_01_http_server.py --selftest
```

---

## Part II: Reverse Proxy (45 min)

### Task 2.1: Demo reverse proxy (10 min)

**Objective**: Understanding the client → proxy → backend flow.

```bash
# Terminal 1: Backend A
python3 python/demos/demo_http_server.py --port 8001 --id backend-A

# Terminal 2: Backend B
python3 python/demos/demo_http_server.py --port 8002 --id backend-B

# Terminal 3: Reverse Proxy
python3 python/demos/demo_reverse_proxy.py --listen-port 8080 \
    --backends 127.0.0.1:8001,127.0.0.1:8002

# Terminal 4: Client (test round-robin)
for i in 1 2 3 4; do
    curl -s -D - http://127.0.0.1:8080/ -o /dev/null | grep X-Backend
done
```

**Questions:**
1. In what order are the backends selected?
2. What header shows which backend processed the request?
3. What header is added by the proxy (original client identification)?

---

### Task 2.2: Proxy capture in tcpdump (15 min)

**Objective**: Visualising the two TCP connections.

```bash
# Terminal 1: Capture
sudo tcpdump -i lo '(port 8080 or port 8001)' -nn

# Other terminals: server + proxy + client (as above)
```

**Complete the table:**

| Connection | Source IP:Port | Destination IP:Port | Role |
|------------|----------------|---------------------|------|
| 1 | | | Client → Proxy |
| 2 | | | Proxy → Backend |

**Question**: Why does the proxy use an ephemeral port (>49152) for the connection to the backend?

---

### Task 2.3: Reverse proxy exercise implementation (20 min)

**Objective**: Completing the proxy from the exercises.

Open `python/exercises/ex_02_reverse_proxy.py` and complete:

```python
def handle_client(conn, addr, balancer):
    """
    TODO 1: Read request from client
    """
    raw = # TODO
    
    """
    TODO 2: Select backend (round-robin)
    Hint: balancer.next() returns the next Backend
    """
    backend = # TODO
    
    """
    TODO 3: Add proxy headers
    Hint: X-Forwarded-For with the client IP
    """
    forwarded = rebuild_request_with_proxy_headers(raw, addr[0])
    
    """
    TODO 4: Connect to backend and send request
    Hint: socket.create_connection((backend.host, backend.port))
    """
    with socket.create_connection(...) as upstream:
        upstream.sendall(forwarded)
        response = recv_http_response(upstream)
    
    """
    TODO 5: Send the response back to the client
    """
    conn.sendall(response)
```

---

## Part III: nginx Reverse Proxy (30 min) - Optional

### Task 3.1: nginx configuration (15 min)

**Objective**: Configuring nginx as a reverse proxy.

1. Check the configuration in `nginx/nginx.conf`
2. Modify ports if necessary

```bash
# Start the Python backends
python3 python/demos/demo_http_server.py --port 8001 --id backend-A &
python3 python/demos/demo_http_server.py --port 8002 --id backend-B &

# Test the nginx configuration
sudo nginx -t -c $(pwd)/nginx/nginx.conf

# Start nginx
sudo nginx -c $(pwd)/nginx/nginx.conf

# Test
curl http://localhost/
```

---

### Task 3.2: Docker Compose (15 min)

**Objective**: Complete orchestration with Docker.

```bash
# Build and start
docker-compose up -d

# Check
docker-compose ps

# Test
curl http://localhost/

# Logs
docker-compose logs -f nginx

# Stop
docker-compose down
```

---

## Final Verification

### Checklist

- [ ] I ran the HTTP server and observed responses for different requests
- [ ] I captured and identified the TCP three-way handshake in tcpdump
- [ ] I observed the difference between HTTP 200 and 404
- [ ] I ran the reverse proxy and observed round-robin
- [ ] I identified the two TCP connections (client→proxy, proxy→backend)
- [ ] I completed at least one exercise (ex_01 or ex_02)
- [ ] (Optional) I configured nginx as a reverse proxy
- [ ] (Optional) I used Docker for orchestration

### Verification questions

1. What HTTP header indicates the body length?
2. Why is it important to check for directory traversal?
3. What role does the X-Forwarded-For header have?
4. How many TCP connections are involved in a request through a reverse proxy?
5. What load balancing algorithm did we use?

---

## Homework

### Assignment 1: Extend HTTP server (Medium)
Add POST method support to the HTTP server. The request body should be saved to a file.

### Assignment 2: Health Check (Advanced)
Implement a health check mechanism in the reverse proxy: if a backend does not respond, it should be temporarily removed from rotation.

### Assignment 3: Logging (Easy)
Add logging in Apache Combined Log Format:
```
IP - - [timestamp] "METHOD /path HTTP/1.1" status bytes
```

---

*Material for Seminar 8, Computer Networks, ASE Bucharest*
