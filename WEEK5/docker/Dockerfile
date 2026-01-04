# Dockerfile — Week 5 Starterkit
# =====================================
# Minimal container for the Python exercises (no Mininet).
#
# Build:   docker build -t starterkit-s5 docker/
# Run:     docker run --rm -it -v "$PWD/artifacts:/work/artifacts" starterkit-s5

FROM python:3.11-slim

LABEL maintainer="ASE-CSIE"
LABEL description="Week 5 starterkit - IP Addressing"
LABEL version="1.0"

# environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TERM=xterm-256color

# installation unelte de baza
RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    iproute2 \
    net-tools \
    tcpdump \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Directorul de lucru
WORKDIR /app

# Copiere cod
COPY python/ ./python/
COPY docs/ ./docs/
COPY README.md ./

# Permisiuni executabile
RUN chmod +x python/exercises/*.py 2>/dev/null || true
RUN chmod +x python/apps/*.py 2>/dev/null || true

# verification la build
RUN python3 -c "import ipaddress; print('Python OK')"

# Punct de input implicit
ENTRYPOINT ["/bin/bash"]

# Comanda implicita
CMD ["-c", "echo 'Starterkit S5 - Utilizare: python python/exercises/ex_5_01_cidr_flsm.py --help'"]
