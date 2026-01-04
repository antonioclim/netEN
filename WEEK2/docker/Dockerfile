# ============================================================
# Dockerfile - Starterkit Week 2: Socket Programming
# Computer Networks - ASE Bucharest, CSIE
# ============================================================
# Lightweight image for running TCP and UDP scenarios
# Revolvix&Hypotheticalandrei
# ============================================================

FROM python:3.11-slim-bullseye

LABEL maintainer="ASE CSIE - Computer networks"
LABEL description="Environment for TCP and UDP socket laboratory work"
LABEL week="2"

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Network tools
    netcat-openbsd \
    net-tools \
    iproute2 \
    iputils-ping \
    tcpdump \
    tshark \
    curl \
    # Utilities
    procps \
    less \
    vim-tiny \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd -m -s /bin/bash student \
    && mkdir -p /app /app/pcap /app/logs \
    && chown -R student:student /app

WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY --chown=student:student seminar/python/ /app/python/
COPY --chown=student:student scripts/ /app/scripts/

# Permissions for scripts
RUN chmod +x /app/scripts/*.sh 2>/dev/null || true

# Switch to non-root user
USER student

# Exposed ports for TCP/UDP
EXPOSE 8080/tcp 8081/tcp 9000/udp 9001/udp

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.close(); print('OK')" || exit 1

# Default entrypoint - interactive shell
CMD ["/bin/bash"]
