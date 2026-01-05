# Seminar 8 – Theoretical Explanations
## Internet Services: HTTP Server + Reverse Proxy

---

## Introduction

This seminar puts into practice the concepts from Lecture 8 (transport layer) and prepares the ground for the application layer. We will implement:

1. **Minimal HTTP server** – using TCP sockets
2. **Reverse Proxy** – for load balancing and backend abstraction

These implementations allow direct observation of the TCP handshake, HTTP structure and data flow between client, proxy and backend.

---

## 1. HTTP Protocol – Recap

### What is HTTP?

**HyperText Transfer Protocol** is an application layer protocol that:
- Runs over TCP (or QUIC for HTTP/3)
- Uses the **request-response** model
- Is **stateless** (each request is independent)
- Uses human-readable text format (HTTP/1.x)

### HTTP Request Structure

```http
GET /index.html HTTP/1.1
Host: www.example.com
User-Agent: curl/8.0
Accept: */*

```

**Components:**
1. **Request Line**: `METHOD SP REQUEST-TARGET SP HTTP-VERSION CRLF`
2. **Headers**: `Header-Name: Header-Value CRLF`
3. **Empty Line**: `CRLF` (separates headers from body)
4. **Body** (optional): data for POST/PUT

### HTTP Response Structure

```http
HTTP/1.1 200 OK
Date: Wed, 25 Dec 2024 10:00:00 GMT
Server: Apache/2.4
Content-Type: text/html; charset=utf-8
Content-Length: 1234

<!DOCTYPE html>
<html>...
```

**Components:**
1. **Status Line**: `HTTP-VERSION SP STATUS-CODE SP REASON-PHRASE CRLF`
2. **Headers**: similar to request
3. **Empty Line**: `CRLF`
4. **Body**: resource content

### important Status Codes

| Code | Category | Meaning |
|------|----------|---------|
| 200 | 2xx Success | OK – request processed successfully |
| 201 | 2xx Success | Created – resource created |
| 301 | 3xx Redirect | Moved Permanently |
| 400 | 4xx Client Error | Bad Request – invalid syntax |
| 404 | 4xx Client Error | Not Found – resource does not exist |
| 405 | 4xx Client Error | Method Not Allowed |
| 500 | 5xx Server Error | Internal Server Error |
| 502 | 5xx Server Error | Bad Gateway – upstream failed |

---

## 2. HTTP Server with Sockets

### Why implement from scratch?

Modern libraries (Flask, Django, Express) completely abstract the HTTP protocol. By implementing manually, we understand:

1. **What a real HTTP request looks like** (bytes on the wire)
2. **Why Content-Length is needed** (body delimitation)
3. **How the status line works** (200 OK, 404 Not Found)
4. **The process of serving static files**

### HTTP Server Algorithm

```
1. Create TCP socket (AF_INET, SOCK_STREAM)
2. Bind to (host, port)
3. Listen (accept connections)
4. Loop:
   a. Accept client connection → (conn, addr)
   b. Read request until CRLFCRLF
   c. Parse request line (METHOD, TARGET, VERSION)
   d. Validate (only GET/HEAD accepted)
   e. Map TARGET to file path
   f. Check directory traversal (security!)
   g. Read file or generate 404
   h. Build and send response
   i. Close connection
```

### Parsing HTTP Request

```python
def parse_http_request(raw: bytes) -> HttpRequest:
    text = raw.decode("iso-8859-1")  # HTTP/1.x: ISO-8859-1
    
    # Headers/body separator
    head, body = text.split("\r\n\r\n", 1)
    lines = head.split("\r\n")
    
    # Request line: "GET /path HTTP/1.1"
    method, target, version = lines[0].split()
    
    # Headers: "Key: Value"
    headers = {}
    for line in lines[1:]:
        key, value = line.split(":", 1)
        headers[key.strip().lower()] = value.strip()
    
    return HttpRequest(method, target, version, headers, raw)
```

### Building HTTP Response

```python
def build_response(status: int, body: bytes, content_type: str) -> bytes:
    reasons = {200: "OK", 404: "Not Found", ...}
    
    response = f"HTTP/1.1 {status} {reasons[status]}\r\n"
    response += f"Content-Type: {content_type}\r\n"
    response += f"Content-Length: {len(body)}\r\n"
    response += f"Connection: close\r\n"
    response += "\r\n"
    
    return response.encode("iso-8859-1") + body
```

### Security: Directory Traversal

**Problem**: A malicious client can request:
```
GET /../../../etc/passwd HTTP/1.1
```

**Solution**: Path normalisation and validation:
```python
def safe_path(target: str, www_root: str) -> str:
    # Decode %2e%2e → ..
    path = urllib.parse.unquote(target)
    
    # Normalise (resolves ../)
    normalized = os.path.normpath(path)
    
    # Absolute path
    full_path = os.path.join(www_root, normalized)
    
    # CRITICAL CHECK
    if not full_path.startswith(www_root):
        raise SecurityError("Directory traversal detected!")
    
    return full_path
```

---

## 3. Reverse Proxy

### What is a Reverse Proxy?

A **reverse proxy** is an intermediary server that:
- Receives requests from clients
- Forwards them to one or more backends
- Returns the response to the client

```
┌────────┐         ┌─────────────┐         ┌───────────┐
│ Client │ ──────→ │ Rev. Proxy  │ ──────→ │ Backend A │
└────────┘         │             │         └───────────┘
                   │  (nginx,    │         ┌───────────┐
                   │   HAProxy)  │ ──────→ │ Backend B │
                   └─────────────┘         └───────────┘
```

### Why Reverse Proxy?

1. **Load Balancing** – distributes load between servers
2. **SSL Termination** – manages certificates centrally
3. **Caching** – reduces load on backend
4. **Security** – hides internal structure
5. **Compression** – reduces bandwidth

### Load Balancing Algorithms

| Algorithm | Description | When to use |
|-----------|-------------|-------------|
| Round-Robin | Sequential rotation | Identical backends |
| Weighted RR | With weights | Servers with different capacities |
| Least Connections | Least busy | Long sessions |
| IP Hash | Same client → same server | Session affinity |

### Round-Robin Implementation in Python

```python
class RoundRobinBalancer:
    def __init__(self, backends: List[Backend]):
        self.backends = backends
        self._index = 0
        self._lock = threading.Lock()
    
    def next(self) -> Backend:
        with self._lock:
            backend = self.backends[self._index]
            self._index = (self._index + 1) % len(self.backends)
            return backend
```

### Proxy Headers

When the proxy forwards the request to the backend, it adds informative headers:

| Header | Description |
|--------|-------------|
| `X-Forwarded-For` | Original client IP |
| `X-Forwarded-Proto` | Original protocol (http/https) |
| `X-Forwarded-Host` | Original host |
| `Via` | Proxy identifier (for debugging) |

**Request transformation example:**

```http
# Original request from client
GET /api/data HTTP/1.1
Host: myapp.com
User-Agent: curl/8.0

# Request forwarded to backend
GET /api/data HTTP/1.1
Host: backend-1:8001
User-Agent: curl/8.0
X-Forwarded-For: 192.168.1.100
X-Forwarded-Host: myapp.com
Via: ASE-S8-Proxy
Connection: close
```

---

## 4. Observation in tcpdump

### Simple HTTP server capture

```bash
# Terminal 1: Capture
sudo tcpdump -i lo port 8080 -nn -A

# Terminal 2: Server
python3 demo_http_server.py --port 8080

# Terminal 3: Client
curl http://127.0.0.1:8080/
```

**What we observe:**
1. **SYN** → SYN-ACK → ACK (three-way handshake)
2. **PSH-ACK** with HTTP request (GET / HTTP/1.1...)
3. **PSH-ACK** with response (HTTP/1.1 200 OK...)
4. **FIN** → ACK → FIN → ACK (connection closure)

### Reverse Proxy Capture

```bash
sudo tcpdump -i lo '(port 8080 or port 8001)' -nn
```

**What we observe:**
- **Connection 1**: Client (ephemeral port) → Proxy (8080)
- **Connection 2**: Proxy (ephemeral port) → Backend (8001)
- Two distinct TCP handshakes!

---

## 5. nginx as Reverse Proxy

### Minimal configuration

```nginx
http {
    upstream backend_pool {
        server 127.0.0.1:8001;
        server 127.0.0.1:8002;
    }
    
    server {
        listen 80;
        
        location / {
            proxy_pass http://backend_pool;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

### Testing nginx

```bash
# Start
sudo nginx -c /path/to/nginx.conf

# Test (observe backend alternation)
for i in {1..4}; do
    curl -s -D - http://localhost/ -o /dev/null | grep X-Backend
done

# Stop
sudo nginx -s stop
```

---

## 6. Docker for Orchestration

### Simple docker-compose.yml

```yaml
version: '3'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend-a
      - backend-b

  backend-a:
    build: .
    command: python3 demo_http_server.py --port 8000 --id backend-A
    
  backend-b:
    build: .
    command: python3 demo_http_server.py --port 8000 --id backend-B
```

### Useful commands

```bash
# Start stack
docker-compose up -d

# Logs
docker-compose logs -f

# Test
curl http://localhost/

# Stop
docker-compose down
```

---

## Summary

| Concept | Implementation | Observation |
|---------|----------------|-------------|
| HTTP Request | Parsing request line + headers | Text format, CRLF delimitation |
| HTTP Response | Status line + headers + body | Content-Length mandatory |
| HTTP Server | TCP socket + accept loop | One thread per client |
| Reverse Proxy | Forward + header modification | Two TCP connections |
| Load Balancing | Round-robin, least-conn | Thread-safe selection |
| Security | Path normalisation | Prevents directory traversal |

---

*Material for Seminar 8, Computer Networks, ASE Bucharest*
