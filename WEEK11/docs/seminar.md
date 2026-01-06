# Seminar 11: Load Balancing and Reverse Proxy

## Overview

**Week**: 11 of 14  
**Duration**: 2 hours seminar  
**Syllabus topic**: Distributed applications with Nginx, load balancing, reverse proxy for Docker Compose containers

---

## 1. What We Will Learn

This seminar explores distributed architectures using:
- **Reverse Proxy** – intermediary between clients and backend servers
- **Load Balancing** – distributing load across multiple instances
- **Docker Compose** – container orchestration for development and testing
- **Nginx** – industrial solution for proxy and load balancing

## 2. Why It Matters

Modern applications run on multiple servers for:
- **Scalability** – handling increased traffic
- **Availability** – continuous operation even if a server fails
- **Performance** – optimal resource distribution

---

## 3. Fundamental Concepts

### 3.1 Reverse Proxy

**Definition**: An intermediary server that receives requests from clients and forwards them to backend servers.

```
┌──────────┐         ┌──────────────┐         ┌──────────┐
│  Client  │ ──────► │ Reverse Proxy│ ──────► │ Backend  │
│          │ ◄────── │   (Nginx)    │ ◄────── │ Servers  │
└──────────┘         └──────────────┘         └──────────┘
```

**Advantages**:
- Hides internal infrastructure structure
- Terminates TLS connections (SSL offloading)
- Cache for static content
- Compression (gzip/brotli)
- Rate limiting and DDoS protection

### 3.2 Load Balancing

**Definition**: The technique of distributing requests across multiple servers to optimise resource usage.

```
                                    ┌─────────┐
                              ┌────►│Backend 1│
                              │     └─────────┘
┌────────┐    ┌────────────┐  │     ┌─────────┐
│ Client │───►│Load Balancer├─┼────►│Backend 2│
└────────┘    └────────────┘  │     └─────────┘
                              │     ┌─────────┐
                              └────►│Backend 3│
                                    └─────────┘
```

### 3.3 Load Balancing Algorithms

| Algorithm | Description | Use Case |
|-----------|-------------|----------|
| **Round Robin** | Circular rotation: 1→2→3→1→... | Identical backends |
| **Weighted Round Robin** | Rotation with weights (2:1:1) | Servers with different capacities |
| **Least Connections** | Chooses server with fewest active connections | Requests with variable duration |
| **IP Hash** | Hash of client IP → same server | Sticky sessions, local state |
| **Random** | Random selection | Simplicity, good statistical distribution |
| **Least Time** | Combines active connections + response time | Optimal performance (Nginx Plus) |

### 3.4 Health Checks and Failover

**Passive Health Check**:
- Monitors backend responses
- Marks a server as "down" after N consecutive failures
- Retries after a timeout

**Active Health Check** (Nginx Plus):
- Sends periodic verification requests
- Detects problems before affecting users

```nginx
upstream backend_pool {
    server backend1:80 max_fails=3 fail_timeout=30s;
    server backend2:80 max_fails=3 fail_timeout=30s;
    server backend3:80 backup;  # used only when others are down
}
```

---

## 4. Demo: Load Balancer in Python

### 4.1 Demo Architecture

We will build a didactic Python load balancer to understand the internal mechanisms.

**Relevant files**:
- `python/exercises/ex_11_01_backend.py` – simple HTTP server
- `python/exercises/ex_11_02_loadbalancer.py` – load balancer

### 4.2 Simple HTTP Backend

```python
# Response structure
f"Backend {self.id} | Host: {hostname} | Time: {timestamp} | Request #{count}"
```

**Starting 3 backends**:
```bash
python3 ex_11_01_backend.py --id 1 --port 8081 &
python3 ex_11_01_backend.py --id 2 --port 8082 --delay 0.1 &
python3 ex_11_01_backend.py --id 3 --port 8083 --delay 0.2 &
```

### 4.3 Python Load Balancer

**Implemented features**:
- Algorithms: round_robin, least_conn, ip_hash
- Passive failover with max_fails and fail_timeout
- Thread-safe for concurrent requests
- Integrated load generator

**Starting**:
```bash
python3 ex_11_02_loadbalancer.py \
    --backends localhost:8081,localhost:8082,localhost:8083 \
    --port 8080 \
    --algorithm round_robin
```

### 4.4 Testing

```bash
# Round Robin
for i in {1..6}; do curl -s http://localhost:8080/; echo; done
# Output: Backend 1, 2, 3, 1, 2, 3

# IP Hash (sticky sessions)
for i in {1..5}; do curl -s http://localhost:8080/; echo; done
# Output: Backend X, X, X, X, X (same for all requests from the same IP)
```

---

## 5. Demo: Nginx Load Balancer (Docker)

### 5.1 Docker Compose Structure

```yaml
# docker/nginx_compose/docker-compose.yml
services:
  lb:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - web1
      - web2
      - web3

  web1:
    image: nginx:alpine
    volumes:
      - ./web1/index.html:/usr/share/nginx/html/index.html:ro

  web2:
    image: nginx:alpine
    volumes:
      - ./web2/index.html:/usr/share/nginx/html/index.html:ro

  web3:
    image: nginx:alpine
    volumes:
      - ./web3/index.html:/usr/share/nginx/html/index.html:ro
```

### 5.2 Nginx Configuration

```nginx
# docker/nginx_compose/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend_pool {
        # Default algorithm: round_robin
        # least_conn;  # Uncomment for least connections
        # ip_hash;     # Uncomment for sticky sessions
        
        server web1:80 weight=1;
        server web2:80 weight=1;
        server web3:80 weight=1;
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

### 5.3 Running the Demo

```bash
cd docker/nginx_compose
docker compose up -d
# Testing
for i in {1..6}; do curl -s http://localhost/; done
# Stop
docker compose down
```

---

## 6. Comparison: Python LB vs Nginx

| Aspect | Python LB | Nginx |
|--------|-----------|-------|
| **Performance** | ~500-1000 req/s | ~50,000+ req/s |
| **Overhead** | Higher (interpretation) | Minimal (optimised C) |
| **Configurability** | Python code (flexible) | Declarative config file |
| **Ecosystem** | Didactic, experimentation | Production, CDN, cache |
| **Health checks** | Passive (manual implementation) | Active + passive (Nginx Plus) |
| **TLS termination** | Possible with ssl module | Native, optimised |

**Conclusion**: Python LB is excellent for learning and prototyping; Nginx for production.

---

## 7. Debugging and Troubleshooting

### 7.1 Connectivity Verification

```bash
# Test individual backend
curl -v http://localhost:8081/

# Verify open ports
ss -tlnp | grep -E "8080|8081|8082|8083"

# Docker logs
docker compose logs -f lb
```

### 7.2 Traffic Capture

```bash
# HTTP traffic to load balancer
sudo tshark -i lo -f "tcp port 8080" -Y "http"

# Traffic between LB and backends
sudo tshark -i lo -f "tcp port 8081 or tcp port 8082 or tcp port 8083"
```

### 7.3 Common Problems

| Problem | Cause | Solution |
|---------|-------|----------|
| "Connection refused" | Backend stopped | Check `ps aux | grep backend` |
| All requests to one backend | IP hash with single client | Test from different IPs |
| Timeouts | Slow backend | Increase `proxy_read_timeout` |
| 502 Bad Gateway | Backend unavailable | Check health checks |

---

## 8. Practical Exercises

### Exercise 1: Manual Round Robin
Start 3 backends, start LB with round_robin, send 9 requests and verify uniform distribution.

### Exercise 2: Failover Simulation
With LB running, stop a backend (Ctrl+C) and observe how traffic redistributes.

### Exercise 3: Weighted Load Balancing
Modify nginx.conf for `weight=3` on web1 and test the distribution (3:1:1).

### Exercise 4: Sticky Sessions
Configure `ip_hash` in Nginx and verify that requests from the same IP go to the same backend.

### Exercise 5: Benchmark
Compare Python LB vs Nginx performance using Apache Bench:
```bash
ab -n 1000 -c 10 http://localhost:8080/  # Python LB
ab -n 1000 -c 10 http://localhost:80/    # Nginx
```

### Exercise 6 (Challenge): Custom Algorithm
Implement a load balancing algorithm based on response time in `ex_11_02_loadbalancer.py`.

---

## 9. Expected Outcomes

After completing the seminar, you should be able to:
- Configure Nginx as reverse proxy and load balancer
- Explain the differences between load balancing algorithms
- Diagnose connectivity problems in distributed systems
- Dockerise multi-container applications with Docker Compose

---

## 10. Contribution to the Team Project

**Weekly artefact**: Add to your project:
1. `docker-compose.yml` with Nginx load balancer and at least 2 backends
2. `nginx.conf` with configured upstream
3. Health check script (`scripts/health_check.sh`)
4. Architecture diagram in README

---

## 11. Bibliography

| Reference | DOI/Link |
|-----------|----------|
| J. Kurose, K. Ross - Computer Networking, 8th Ed. | ISBN: 978-0135928615 |
| B. Rhodes, J. Goetzen - Foundations of Python Network Programming | DOI: 10.1007/978-1-4302-5855-1 |

**Online resources**:
- [Nginx Load Balancing Documentation](https://nginx.org/en/docs/http/load_balancing.html)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

*Document generated for Seminar 11 – Computer Networks*  
*Revolvix&Hypotheticalandrei*
