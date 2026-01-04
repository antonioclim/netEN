# ==============================================================================
# Dockerfile - Week 4 starter kit (Custom TCP and UDP protocols)
# ==============================================================================
# Purpose
# - Provide a minimal, reproducible container that can run the non-interactive demo
#   and write artefacts to /app/artifacts.
#
# Notes
# - Packet capture inside containers requires extra privileges and is not enabled by default.
# - This image is designed for CLI-only environments.
# ==============================================================================

FROM python:3.11-slim

WORKDIR /app
COPY . /app

# Minimal runtime tools for basic networking introspection and demo support
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       iproute2 iputils-ping netcat-openbsd procps \
    && rm -rf /var/lib/apt/lists/*

# Ensure scripts are runnable even if the zip did not preserve executable bits
RUN chmod +x /app/scripts/*.sh /app/tests/*.sh 2>/dev/null || true

# Non-root execution for safer defaults
RUN useradd -m -u 1000 netuser \
    && chown -R netuser:netuser /app
USER netuser

# Week 4 default ports (host side mapping is configured in docker-compose.yml)
EXPOSE 5400 5401 5402/udp

# Default: quick demo (no capture) then a quick smoke test
CMD ["bash","-lc","./scripts/run_all.sh --quick && ./tests/smoke_test.sh --quick"]
