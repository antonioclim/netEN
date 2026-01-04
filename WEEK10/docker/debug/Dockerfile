FROM alpine:3.19

# Install diagnostic tools
RUN apk add --no-cache \
    bash \
    curl \
    wget \
    bind-tools \
    openssh-client \
    lftp \
    tcpdump \
    nmap \
    netcat-openbsd \
    iputils \
    iproute2 \
    python3 \
    py3-pip

# Install Python tools
RUN pip3 install --no-cache-dir --break-system-packages \
    requests \
    paramiko \
    dnspython

# Welcome script
RUN echo '#!/bin/sh' > /etc/profile.d/welcome.sh && \
    echo 'echo ""' >> /etc/profile.d/welcome.sh && \
    echo 'echo "╔═══════════════════════════════════════════════════════════════╗"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "║        DEBUG CONTAINER - Week 10                              ║"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "╠═══════════════════════════════════════════════════════════════╣"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "║  Useful commands:                                             ║"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "║    dig web                     - Docker implicit DNS          ║"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "║    dig @dns-server -p 5353 myservice.lab.local                ║"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "║    curl http://web:8000        - HTTP test                    ║"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "║    ssh labuser@ssh-server      - SSH (password: labpass)      ║"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "║    lftp -u labftp,labftp ftp-server:2121                      ║"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "║    tcpdump -i any port 80      - Traffic capture              ║"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "╚═══════════════════════════════════════════════════════════════╝"' >> /etc/profile.d/welcome.sh && \
    echo 'echo ""' >> /etc/profile.d/welcome.sh && \
    chmod +x /etc/profile.d/welcome.sh

WORKDIR /root

CMD ["/bin/sh", "-l"]
