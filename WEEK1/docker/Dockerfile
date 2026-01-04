# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV HOME=/home/lab
WORKDIR /work

# Create home directory for non-root user
RUN mkdir -p /home/lab && chmod 777 /home/lab

RUN apt-get update -y \
  && apt-get install -y --no-install-recommends \
     iproute2 iputils-ping netcat-openbsd tcpdump \
  && rm -rf /var/lib/apt/lists/*

# Pre-install common dependencies during build (as root)
RUN pip install --no-cache-dir python-docx scapy dpkt || true

# At runtime, just run the demo (dependencies already installed)
CMD ["bash", "-lc", "bash scripts/run_all.sh --quick --no-capture && bash tests/smoke_test.sh"]
