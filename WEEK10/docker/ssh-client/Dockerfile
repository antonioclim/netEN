FROM python:3.11-alpine

RUN pip install --no-cache-dir paramiko

WORKDIR /app
COPY paramiko_client.py .

CMD ["python3", "/app/paramiko_client.py"]
