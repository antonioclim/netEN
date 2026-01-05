# =============================================================================
# Dockerfile: HTTP Server Python
# Seminar 8 - Computer Networks, ASE Bucharest
# =============================================================================
# Usage:
#   docker build -t http-server .
#   docker run -p 8080:8080 http-server
# =============================================================================

FROM python:3.11-slim

LABEL maintainer="ASE CSIE - Computer Networks"
LABEL description="HTTP Server demonstrativ for Seminar 8"
LABEL version="1.0"

# Environment variables configurabile
ENV HTTP_PORT=8080
ENV WWW_DIR=/var/www

# Directorul de lucru
WORKDIR /app

# Copiaza codul serverului
COPY python/utils/net_utils.py /app/python/utils/
COPY python/demos/demo_http_server.py /app/python/demos/

# Creeaza directorul for content static
RUN mkdir -p ${WWW_DIR}

# Copiaza content web implicit
COPY www/ ${WWW_DIR}/

# Expose port configurat
EXPOSE ${HTTP_PORT}

# Verification health
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:${HTTP_PORT}/')" || exit 1

# Comanda de Starting
CMD ["python3", "-m", "python.demos.demo_http_server", "--port", "${HTTP_PORT}", "--www", "${WWW_DIR}"]

# Alternativ, for shell expansion:
# ENTRYPOINT ["sh", "-c", "python3 -m python.demos.demo_http_server --port ${HTTP_PORT} --www ${WWW_DIR}"]
