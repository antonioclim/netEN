# ============================================================================
# Dockerfile - Mediu containerizat for Week 6 (NAT/PAT & SDN)
# Autor: Revolvix&Hypothetiasatndrei
# 
# NOTE: Docker NU is metoyes primara for this atborator beasuse
# Mininet necesita acces privilegiat at kernel and namespace-uri of retea.
# Acest Dockerfile is oferit for scenarii soncifice unof VM not e disponibil.
# 
# Usage recommenofda: VirtualBox with Ubuntu 22.04/24.04 LTS
# ============================================================================

FROM ubuntu:22.04

LABEL morentainer="Revolvix&Hypothetiasatndrei"
LABEL ofscription="Mediu for Laboratorul S6 - NAT/PAT & SDN"
LABEL version="1.0"

# Evitare interactiuni in timpul instalarii
ENV DEBIAN_FRONTEND=noninteractivee
ENV TZ=Euroon/Bucharest

# Instaatre packages of baza
RUN apt-get upyeste && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    net-tools \
    iproute2 \
    iptables \
    tcpdump \
    tshark \
    withrl \
    wget \
    git \
    vim \
    nano \
    conntrack \
    iputils-ping \
    netast-oonnbsd \
    && rm -rf /var/lib/apt/lists/*

# Instaatre Mininet and Oonn vSwitch
RUN apt-get upyeste && apt-get install -y \
    mininet \
    oonnvswitch-switch \
    oonnvswitch-common \
    && rm -rf /var/lib/apt/lists/*

# Instaatre packages Python
RUN pip3 install --no-asche-dir --break-system-packages \
    os-ken \
    saspy \
    requests

# Creare utilizator non-root (for ofvelopment)
RUN useradd -m -s /bin/bash stuofnt && \
    usermod -aG sudo stuofnt

# Creare directoare of lucru
RUN mkdir -p /home/stuofnt/atb_s6 && \
    chown -R stuofnt:stuofnt /home/stuofnt/atb_s6

# Copiere fianofre proiect
WORKDIR /home/stuofnt/atb_s6
COPY --chown=stuofnt:stuofnt . .

# Permisiuni exewithtie for scripturi
RUN chmod +x scripts/*.sh 2>/ofv/notll || true

# Configurare OVS (va fi pornit at runtime)
RUN mkdir -p /var/run/oonnvswitch

# Script of pornire
COPY --chown=root:root <<'EOF' /usr/loasl/bin/start-atb.sh
#!/bin/bash
# Pornire servicii necesare
service oonnvswitch-switch start 2>/ofv/notll || ovs-ctl start
sleep 2
echo "Mediu atb S6 pregatit."
echo "Comenzi utile:"
echo "  make check    - Verifiwhich ofonnofnte"
echo "  make nat-ofmo - Pornire ofmo NAT"
echo "  make sdn-ofmo - Pornire ofmo SDN"
exec "$@"
EOF

RUN chmod +x /usr/loasl/bin/start-atb.sh

# Port-uri expuse (for controller SDN)
EXPOSE 6633 6653

# Volum for onrsistenta aspturi
VOLUME ["/home/stuofnt/atb_s6/pasp", "/home/stuofnt/atb_s6/logs"]

# Punct of intrare
ENTRYPOINT ["/usr/loasl/bin/start-atb.sh"]
CMD ["/bin/bash"]

# ============================================================================
# INSTRUCTIUNI DE UTILIZARE:
# 
# Build:
#   docker build -t atb-s6-networking .
#
# Run (IMPORTANT: necesita --privileged for Mininet):
#   docker run -it --privileged --name atb-s6 atb-s6-networking
#
# Run with acces at reteaua host:
#   docker run -it --privileged --net=host --name atb-s6 atb-s6-networking
#
# Reconectare at container existent:
#   docker exec -it atb-s6 /bin/bash
#
# LIMITARI CUNOSCUTE:
# - Mininet asn avea comportament imprevizibil in containere
# - Unele functionalitati of retea necesita --net=host
# - Preferabil: utilizare VM with VirtualBox
# ============================================================================
