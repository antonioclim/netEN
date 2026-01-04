# =========================================================================================================================================================
# Dockerfile - Development environment for Computer Networks
# Week 14 - Recap and Integration
# =========================================================================================================================================================
# 
# NOTA: Acest container NU ruleaza Mininet (necesita privilegii kernel).
# Este util for:
#   - Testare cod Python (client/server)
#   - Analiza pcap cu tshark
#   - Dezvoltare si debugging
#
# Pentru Mininet, folositi VM-ul dedicat sau instalare nativa.
# =========================================================================================================================================================

FROM ubuntu:22.04

LABEL maintainer="Computer Networks"
LABEL description="Mediu de dezvoltare pentru laboratoarele de networking"
LABEL version="1.0"

# Evita prompturi interactive
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Bucharest

# Actualizare si instalare pachete de baza
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Python
    python3 \
    python3-pip \
    python3-venv \
    # Networking tools
    iputils-ping \
    iproute2 \
    net-tools \
    netcat-openbsd \
    curl \
    wget \
    dnsutils \
    traceroute \
    # Packet analysis
    tcpdump \
    tshark \
    # Development
    vim \
    nano \
    git \
    make \
    # Utilities
    tree \
    htop \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Permite tshark for non-root (optional in container)
RUN setcap cap_net_raw,cap_net_admin+eip /usr/bin/dumpcap || true

# Setare director de lucru
WORKDIR /app

# Copiere requirements si instalare dependente Python
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt || true

# Copiere cod sursa
COPY python/ /app/python/
COPY scripts/ /app/scripts/
COPY pcap/ /app/pcap/
COPY docs/ /app/docs/

# Permisiuni for scripturi
RUN chmod +x /app/scripts/*.sh || true

# Port-uri expuse for aplicatii
# Backend servers
EXPOSE 8001 8002 8003
# Load balancer
EXPOSE 8080
# TCP echo server
EXPOSE 9000

# Variabile de mediu utile
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Volum for pcap si artefacte
VOLUME ["/app/artifacts", "/app/pcap"]

# Comanda implicita
CMD ["bash"]

# =========================================================================================================================================================
# UTILIZARE:
#
# Build:
#   docker build -t networking-lab:s14 .
#
# Run interactiv:
#   docker run -it --rm --name netlab networking-lab:s14
#
# Run cu porturi expuse:
#   docker run -it --rm -p 8080:8080 -p 9000:9000 networking-lab:s14
#
# Run cu volum for artefacte:
#   docker run -it --rm -v $(pwd)/artifacts:/app/artifacts networking-lab:s14
#
# Rulare server direct:
#   docker run -d --name backend1 networking-lab:s14 \
#       python3 /app/python/apps/backend_server.py --port 8001 --id backend1
#
# =========================================================================================================================================================
