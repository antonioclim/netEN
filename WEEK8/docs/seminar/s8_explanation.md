# Seminar 8 — Transport Layer and HTTP: Practical Notes

This seminar connects transport-layer concepts (TCP ports, sockets and connection establishment) with an application-layer case study:
a minimal HTTP/1.1 server and a reverse proxy implementing round-robin load balancing.

The emphasis is on **observability**: you should be able to justify what you see in the terminal, in logs and in packet captures.

---

## 1. Transport layer concepts used in this laboratory

### 1.1 Ports and sockets
A **port** identifies a transport-layer endpoint on a host. A **socket** pairs an IP address and a port (plus a protocol, typically TCP or UDP).
Servers listen on a well-defined port and clients connect from an ephemeral port.

### 1.2 TCP connection establishment (three-way handshake)
A TCP connection is established via:

1. **SYN** (client → server)
2. **SYN/ACK** (server → client)
3. **ACK** (client → server)

In packet captures, these three segments are typically the first packets in a flow (ignoring retransmissions).
The handshake allocates state at both endpoints and negotiates initial sequence numbers.

### 1.3 TCP streams and message boundaries
TCP provides a **byte stream**, not message boundaries.
HTTP/1.1 therefore requires explicit framing rules:
- the end of headers is marked by `\r\n\r\n`
- the body length is commonly determined by `Content-Length` (or chunked transfer encoding in more advanced servers)

---

## 2. HTTP/1.1 structure relevant to the exercises

### 2.1 Request format
An HTTP/1.1 request begins with a request line:

`METHOD SP PATH SP VERSION`

followed by headers (key-value pairs) and an optional body.

Example:

```
GET /hello.txt HTTP/1.1
Host: localhost:8080
User-Agent: curl/8.x
Accept: */*
```

### 2.2 Response format
An HTTP response begins with a status line:

`VERSION SP STATUS_CODE SP REASON`

followed by headers and an optional body.

You should always see a valid status line such as `HTTP/1.1 200 OK` or `HTTP/1.1 404 Not Found`.

---

## 3. Reverse proxy concepts used in this laboratory

A **reverse proxy** accepts client connections and forwards the request to one of multiple backend servers.
The proxy can implement:
- load balancing (round-robin in this kit)
- header insertion (for example `X-Forwarded-For`)
- observability and correlation (`X-Request-ID`)

### 3.1 Two TCP connections
In the proxy scenario there are **two distinct TCP connections**:

1. client → proxy (to port `8888`)
2. proxy → backend (to port `9001` or `9002`)

This should be visible using `ss -tnp` and in captures.

---

## 4. What to observe in the provided demos

### 4.1 Demo 1: HTTP server (port 8080)
- Request parsing, header handling, file serving
- Status codes and response headers

### 4.2 Demo 2: Reverse proxy (port 8888)
- Backend alternation (A, B, A, B…)
- Response identification via `X-Served-By` or `X-Backend`
- Client metadata propagation via `X-Forwarded-For` (visible in backend logs)

---

## 5. Suggested analysis questions

1. Which fields in the TCP header are essential for reliability?
2. Why does an HTTP parser need `Content-Length`?
3. Why do we expect two TCP flows in the proxy scenario?
4. What limitations does round-robin have compared with least-connections or latency-aware balancing?
