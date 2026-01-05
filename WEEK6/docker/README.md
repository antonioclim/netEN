# Docker for Week 6 - NAT/PAT & SDN

## ⚠️ Important Note

**Docker is NOT the recommended method for this laboratory.**

Mininet requires privileged access to the Linux kernel and network namespaces, which makes containerisation problematic. We recommend using a virtual machine (VirtualBox + Ubuntu 22.04/24.04).

## When to use Docker?

- You already have experience with Docker and privileged containers
- You cannot run VirtualBox
- You want to quickly test Python code (without complex Mininet topologies)
- You have native Linux as your host operating system

## Known limitations

1. **Mininet in containers**: May exhibit unpredictable behaviour
2. **macOS/Windows**: Very limited functionality (Docker Desktop does not fully support network namespaces)
3. **Network mode**: Requires `--privileged` and usually `--net=host`

## Usage

### Build

```bash
cd docker/
docker build -t lab-s6-networking ..
```

### Run (interactive mode)

```bash
docker run -it --privileged --net=host --name lab-s6 lab-s6-networking
```

### With docker-compose

```bash
# Build
docker-compose build

# Run interactive
docker-compose run --rm lab-s6

# Stop
docker-compose down -v
```

## Recommended alternative: VirtualBox

1. Download [VirtualBox](https://www.virtualbox.org/)
2. Download [Ubuntu 22.04 LTS](https://ubuntu.com/download/desktop) or [Ubuntu Server](https://ubuntu.com/download/server)
3. Create VM with:
   - 2-4 GB RAM
   - 20 GB disk
   - Network: NAT or Bridged
4. In the VM, run: `make setup`

---

*Revised 2025-01*
