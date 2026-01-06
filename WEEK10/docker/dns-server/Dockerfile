FROM python:3.11-alpine

RUN pip install --no-cache-dir dnslib

WORKDIR /app
COPY dns_server.py .

EXPOSE 5353/udp

CMD ["python3", "dns_server.py", "--port", "5353"]
