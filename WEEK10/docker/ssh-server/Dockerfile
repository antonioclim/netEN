FROM alpine:3.19

RUN apk add --no-cache openssh-server

# Create user
RUN adduser -D -s /bin/sh labuser && \
    echo "labuser:labpass" | chpasswd && \
    mkdir -p /home/labuser/.ssh /home/labuser/storage && \
    chown -R labuser:labuser /home/labuser

# Configure sshd
RUN ssh-keygen -A && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config && \
    echo "AllowUsers labuser" >> /etc/ssh/sshd_config

# Welcome message
RUN echo 'echo "╔═══════════════════════════════════════════╗"' > /etc/profile.d/welcome.sh && \
    echo 'echo "║  Week 10 - SSH Server Demo                ║"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "║  User: labuser | Home: /home/labuser      ║"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "╚═══════════════════════════════════════════╝"' >> /etc/profile.d/welcome.sh

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D", "-e"]
