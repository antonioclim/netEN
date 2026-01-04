# =============================================================================
# Dockerfile for Week 12 - Email and RPC Protocols
# =============================================================================
# Minimalist image for running demos and exercises
# 
# Build:   docker build -t s12-email-rpc .
# Run:     docker run -it --rm -p 1025:1025 -p 8000:8000 -p 8001:8001 s12-email-rpc
# =============================================================================

FROM python:3.11-slim-bookworm

LABEL maintainer="Revolvix&Hypotheticalandrei"
LABEL description="Week 12 - Email Protocols (SMTP/POP3/IMAP) and RPC (JSON-RPC/XML-RPC)"
LABEL version="1.0"

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install required system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Network utilities
    tshark \
    tcpdump \
    netcat-openbsd \
    curl \
    wget \
    dnsutils \
    iproute2 \
    iputils-ping \
    net-tools \
    # Editor and utilities
    vim-tiny \
    less \
    tree \
    # Build tools (for some Python packages)
    gcc \
    python3-dev \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -s /bin/bash student \
    && usermod -aG wireshark student 2>/dev/null || true

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY exercises/ ./exercises/
COPY Makefile .
COPY README.md .

# Permissions for scripts
RUN chmod +x scripts/*.sh 2>/dev/null || true

# Create output directories
RUN mkdir -p /app/pcap /app/mailbox /app/logs \
    && chown -R student:student /app

# Expose ports
# 1025 - Educational SMTP server
# 8000 - JSON-RPC server
# 8001 - XML-RPC server
# 50051 - gRPC server (optional)
EXPOSE 1025 8000 8001 50051

# Switch to non-root user
USER student

# Environment check on start
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.settimeout(1); s.connect(('localhost',1025)); s.close()" || exit 1

# Default command - interactive shell
CMD ["/bin/bash"]

# =============================================================================
# Usage:
#
# 1. Build image:
#    docker build -t s12-email-rpc .
#
# 2. Run interactively:
#    docker run -it --rm --name s12 \
#      -p 1025:1025 -p 8000:8000 -p 8001:8001 \
#      s12-email-rpc
#
# 3. Run SMTP server in background:
#    docker run -d --name smtp-server \
#      -p 1025:1025 \
#      s12-email-rpc python src/email/smtp_server.py
#
# 4. Run JSON-RPC server:
#    docker run -d --name jsonrpc-server \
#      -p 8000:8000 \
#      s12-email-rpc python src/rpc/jsonrpc/jsonrpc_server.py
#
# 5. Access shell in running container:
#    docker exec -it s12 /bin/bash
#
# 6. Capture traffic:
#    docker exec s12 tshark -i any -w /app/pcap/capture.pcap
# =============================================================================
