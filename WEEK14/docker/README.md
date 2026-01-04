# Docker Setup for Computer Networks - Week 14

## Overview

This folder contains Docker configuration for running demonstrations and exercises.

**IMPORTANT**: Docker is an **ALTERNATIVE** to Mininet, not a complete replacement. Use:
- **Mininet** for: layer 2/3 simulation, switches, routing, complex topologies
- **Docker** for: rapid application testing, development, simple demos

## When to Use Docker vs Mininet

| Criterion | Docker | Mininet |
|-----------|--------|---------|
| Installation | Simple, cross-platform | Linux only |
| Startup | ~10 seconds | ~5 seconds |
| Layer 2 (MAC, ARP) | Limited | Complete |
| Custom routing | Limited | Complete |
| Packet capture | Yes (tcpdump) | Yes (tcpdump, Wireshark) |
| Performance | Container overhead | Native performance |
| Reproducibility | Excellent | Good |

## Requirements

- Docker Engine 20.10+
- Docker Compose 2.0+
- ~2GB disk space
- ~1GB RAM

## Structure

```
docker/
├── Dockerfile          # Base image for all services
├── docker-compose.yml  # Multi-container orchestration
└── README.md           # This file
```

## Quick Usage

### 1. Build image

```bash
cd docker/
docker build -t networking-lab:s14 ..
```

### 2. Start complete infrastructure

```bash
docker-compose up -d
```

This starts:
- 2 backend servers (app1, app2)
- 1 load balancer (lb)
- 1 interactive client
- 1 TCP echo server

### 3. Check status

```bash
docker-compose ps
docker-compose logs -f
```

### 4. Access client container

```bash
docker-compose exec client bash
```

### 5. Tests from client container

```bash
# Test HTTP through load balancer
curl http://172.21.0.10:8080/
curl http://172.21.0.10:8080/health
curl http://172.21.0.10:8080/lb-status

# Test TCP echo
python3 /app/python/apps/tcp_echo_client.py --host 172.20.0.20 --port 9000

# Capture traffic
tcpdump -i any -w /app/artifacts/capture.pcap &
curl http://172.21.0.10:8080/
kill %1
```

### 6. Tests from host

```bash
# Ports are exposed: 8080 (LB), 9000 (echo)
curl http://localhost:8080/
curl http://localhost:8080/lb-status
```

### 7. Shutdown

```bash
docker-compose down
# Or with volume deletion
docker-compose down -v
```

## Network Topology

```
                     HOST
                       │
                       │ port mapping
                       │ 8080, 9000
                       ▼
    frontend_net (172.21.0.0/24)
    ┌─────────────────────────────────────┐
    │                                     │
    │  client                  lb         │
    │  172.21.0.2              172.21.0.10│
    │                          │          │
    └──────────────────────────┼──────────┘
                               │
    backend_net (172.20.0.0/24)│
    ┌──────────────────────────┼──────────┐
    │                          │          │
    │  app1         app2       lb    echo │
    │  172.20.0.2   172.20.0.3      172.20.0.20
    │  :8001        :8001           :9000 │
    │                                     │
    └─────────────────────────────────────┘
```

## Debugging

### Check logs per service

```bash
docker-compose logs app1
docker-compose logs app2
docker-compose logs lb
```

### Network inspection

```bash
docker network inspect docker_backend_net
docker network inspect docker_frontend_net
```

### Access any container

```bash
docker-compose exec app1 bash
docker-compose exec lb bash
```

### Connectivity test from lb

```bash
docker-compose exec lb bash
ping 172.20.0.2   # app1
ping 172.20.0.3   # app2
curl http://172.20.0.2:8001/health
```

## Common Modifications

### Adding a new backend server

In `docker-compose.yml`, add:

```yaml
  app3:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: netlab-app3
    hostname: app3
    command: python3 /app/python/apps/backend_server.py --port 8001 --id app3
    networks:
      backend_net:
        ipv4_address: 172.20.0.4
```

And modify the load balancer:
```yaml
  lb:
    command: >
      python3 /app/python/apps/lb_proxy.py
      --listen-port 8080
      --backends 172.20.0.2:8001,172.20.0.3:8001,172.20.0.4:8001
```

### Rebuild after code changes

```bash
docker-compose build
docker-compose up -d
```

## Limitations

1. **Does not fully simulate layer 2** - ARP, broadcast, switching are simplified
2. **Does not support custom routing** - routing between subnets is automatic
3. **Cannot control delay/bandwidth** - like in Mininet with `tc`
4. **tcpdump sees aggregated traffic** - not per-interface like in Mininet

## Recommended Exercises with Docker

1. **Load balancing verification**: Send 100 requests and verify distribution
2. **Health check behaviour**: Stop a backend and observe redistribution
3. **Latency measurement**: Measure RTT client → lb → backend
4. **Capture analysis**: Capture traffic and analyse with tshark

## Resources

- [Docker Networking Guide](https://docs.docker.com/network/)
- [Docker Compose Networking](https://docs.docker.com/compose/networking/)
- [Mininet vs Docker](https://mininet.org/)

---
*Revolvix&Hypotheticalandrei*
