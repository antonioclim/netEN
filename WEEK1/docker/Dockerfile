# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV HOME=/home/lab
WORKDIR /work

# Create home directory for non-root user (pip cache, etc.)
RUN mkdir -p /home/lab && chmod 777 /home/lab

# Install system dependencies
RUN apt-get update -y \
  && apt-get install -y --no-install-recommends \
     iproute2 iputils-ping netcat-openbsd tcpdump \
  && rm -rf /var/lib/apt/lists/*

# Pre-install Python dependencies during build (as root)
# This avoids permission issues when running as non-root user
RUN pip install --no-cache-dir python-docx scapy dpkt || true

# At runtime, ensure artifacts dir exists and run the demo
CMD ["bash", "-lc", "mkdir -p /work/artifacts && bash scripts/run_all.sh --quick --no-capture && bash tests/smoke_test.sh"]
