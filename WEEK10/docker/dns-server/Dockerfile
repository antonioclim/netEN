FROM python:3.11-alpine

RUN pip install --no-cache-dir dnslib

WORKDIR /app
COPY dns_server.py .

EXPOSE 5353/udp

CMD ["python3", "dns_server.py", "--port", "5353", \
     "--a", "myservice.lab.local=10.10.10.10", \
     "--a", "api.lab.local=10.10.10.20", \
     "--a", "web.lab.local=172.20.0.10"]
