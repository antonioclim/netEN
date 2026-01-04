FROM python:3.11-alpine

RUN pip install --no-cache-dir pyftpdlib

WORKDIR /app
COPY ftp_server.py .

# Create FTP directoryy structure
RUN mkdir -p /home/ftp/uploads /home/ftp/downloads && \
    echo "Welcome to the FTP server - Week 10!" > /home/ftp/welcome.txt && \
    echo "Revolvix&Hypotheticalandrei" >> /home/ftp/welcome.txt

EXPOSE 2121
EXPOSE 30000-30009

CMD ["python3", "ftp_server.py"]
