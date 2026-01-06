#!/usr/bin/env python3
"""
EXERCISE 1: Completare Server HTTP
=====================================
Subject: Computer Networks, Week 8
Level: Intermediate
estimated time: 30 minutes

OBJECTIVES:
- Understanding the format HTTP request/response
- Implementing parsing HTTP requests
- Serving static files with security

INSTRUCTIONS:
1. Complete the functions marked with TODO
2. Run the tests: python3 -m pytest tests/test_ex01.py -v
3. Test manually: python3 ex01_http_server.py --port 8081

EVALUATION:
- Correct parsing request: 30%
- File serving: 30%
- Security (directory traversal): 20%
- HEAD method: 20%

© Revolvix&Hypotheticalandrei
"""

import socket
import os
import sys
import argparse
from pathlib import Path
from typing import Tuple, Dict, Optional

# ============================================================================
# CONSTANTS
# ============================================================================

CRLF = "\r\n"
DOUBLE_CRLF = "\r\n\r\n"

HTTP_STATUS = {
    200: "OK",
    400: "Bad Request",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    500: "Internal Server Error",
}

MIME_TYPES = {
    ".html": "text/html",
    ".htm": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".json": "application/json",
    ".txt": "text/plain",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".ico": "image/x-icon",
}

DEFAULT_TYPE = "application/octet-stream"


# ============================================================================
# TODO: IMPLEMENT THIS FUNCTION
# ============================================================================

def parse_request(raw_request: bytes) -> Tuple[str, str, str, Dict[str, str]]:
    """
    Parse an HTTP request and extract the components.
    
    Args:
        raw_request: Bytes received from the client
    
    Returns:
        Tuple with: (method, path, version, headers_dict)
        
    Exemple:
        >>> data = b'GET /index.html HTTP/1.1\\r\\nHost: localhost\\r\\n\\r\\n'
        >>> method, path, version, headers = parse_request(data)
        >>> method
        'GET'
        >>> path
        '/index.html'
        >>> headers['host']
        'localhost'
    
    HINT:
    1. Decodifica raw_request in string (utf-8)
    2. Separa pe linii (\\r\\n)
    3. Prima linie contine: METHOD PATH VERSION
    4. Restul liniilor sunt headers in format "Key: Value"
    5. Normalizeaza key-urile to lowercase
    
    Attention:
    - Tratati cazul cand request-ul este invalid (returnati error sensibila)
    - Header keys ar trebui sa fie case-insensitive
    """
    
    # TODO: Implement parsing request HTTP
    # 
    # steps sugerati:
    # 1. Decodifica bytes -> string
    # 2. Split pe CRLF For to obtain lines
    # 3. Parseaza prima linie (request line): method, path, version
    # 4. Parseaza headers (key: value)
    # 5. Returns tuple-ul
    
    raise NotImplementedError("TODO: Implement parse_request()")


# ============================================================================
# TODO: IMPLEMENT THIS FUNCTION
# ============================================================================

def is_safe_path(requested_path: str, docroot: str) -> bool:
    """
    Check if path ceruta este sigura (nu permite directory traversal).
    
    Args:
        requested_path: path ceruta de client (ex: "/images/../../../etc/passwd")
        docroot: Directorul radacina For files statice
    
    Returns:
        True if path este sigura, False altfel
    
    Exemple:
        >>> is_safe_path("/index.html", "/var/www")
        True
        >>> is_safe_path("/../etc/passwd", "/var/www")
        False
        >>> is_safe_path("/images/logo.png", "/var/www")
        True
    
    HINT:
    - use os.path.normpath() For to normalise path
    - use os.path.abspath() For to obtain absolute path
    - Verificati ca rezultatul este in interiorul docroot-ului
    
    SECURITATE:
    - this este o functie CRITICA For securitate
    - Atacatorii vor incerca ../../../etc/passwd
    - Trebuie sa preveniti ORICE ieandre din docroot
    """
    
    # TODO: Implement security check path
    #
    # steps sugerati:
    # 1. Normalizati requested_path (elimina .. and .)
    # 2. Construiti path completea: docroot + requested_path
    # 3. obtain absolute path For ambele
    # 4. Verificati ca path completea incepe cu docroot
    
    raise NotImplementedError("TODO: Implement is_safe_path()")


# ============================================================================
# TODO: IMPLEMENT THIS FUNCTION
# ============================================================================

def serve_file(path: str, docroot: str) -> Tuple[int, Dict[str, str], bytes]:
    """
    Serveste un file static de pe disc.
    
    Args:
        path: path ceruta (ex: "/index.html")
        docroot: Directorul radacina
    
    Returns:
        Tuple with: (status_code, headers_dict, body_bytes)
    
    Exemple:
        >>> status, headers, body = serve_file("/index.html", "./www")
        >>> status
        200
        >>> headers['content-type']
        'text/html'
    
    HINT:
    1. Verificati securitatea path cu is_safe_path()
    2. Daca path e "/" use "/index.html" implicit
    3. Determinati MIME type din extensie
    4. Cititi fianderul in mod binar ('rb')
    5. Returnati headers corespunzatoare
    
    CAZURI DE TRATAT:
    - 403: cale nesigura (directory traversal)
    - 404: file nu exista
    - 200: file gasit and servit
    """
    
    # TODO: Implement serving file
    #
    # steps sugerati:
    # 1. Normalizati path (if e "/" → "/index.html")
    # 2. Verificati securitatea cu is_safe_path()
    # 3. Construiti path completea
    # 4. Verificati if fianderul exista
    # 5. Determinati Content-Type din extensie
    # 6. Cititi continutul file
    # 7. Construiti headers (Content-Type, Content-Length)
    # 8. Returnati (status_code, headers, body)
    
    raise NotImplementedError("TODO: Implement serve_file()")


# ============================================================================
# TODO: IMPLEMENT THIS FUNCTION
# ============================================================================

def build_response(status_code: int, headers: Dict[str, str], body: bytes) -> bytes:
    """
    Build un response HTTP complete.
    
    Args:
        status_code: Codul de status HTTP (200, 404, etc.)
        headers: Dictionary with headers
        body: Continutul response in bytes
    
    Returns:
        Raspunsul HTTP complete ca bytes
    
    Exemple:
        >>> resp = build_response(200, {"Content-Type": "text/plain"}, b"Hello")
        >>> resp.startswith(b"HTTP/1.1 200 OK")
        True
    
    FORMAT:
        HTTP/1.1 {status_code} {status_text}\r\n
        Header1: Value1\r\n
        Header2: Value2\r\n
        \r\n
        {body}
    """
    
    # TODO: Implement building response HTTP
    #
    # steps sugerati:
    # 1. Construiti status line: "HTTP/1.1 {code} {text}\r\n"
    # 2. Adaugati fiecare header: "{Key}: {Value}\r\n"
    # 3. Adaugati linie goala: "\r\n"
    # 4. Convertiti totul to bytes and adaugati body
    
    raise NotImplementedError("TODO: Implement build_response()")


# ============================================================================
# TODO: IMPLEMENT THIS FUNCTION
# ============================================================================

def handle_request(raw_request: bytes, docroot: str) -> bytes:
    """
    Proceseaza un request HTTP complete and returneaza responseul.
    
    Args:
        raw_request: Request-ul HTTP in bytes
        docroot: Directorul radacina For files
    
    Returns:
        Raspunsul HTTP complete in bytes
    
    METODE SUPORTATE:
    - GET: returneaza fianderul complete (headers + body)
    - HEAD: returns headers only (no body)
    - Altele: returneaza 405 Method Not Allowed
    
    HINT:
    - use functiile implementate previous
    - For HEAD, apelati serve_file dar nu includeti body-ul in response
    """
    
    # TODO: Implement handler complete
    #
    # steps sugerati:
    # 1. Parsati request-ul
    # 2. Verificati metoda (GET, HEAD, altele)
    # 3. For GET/HEAD, apelati serve_file()
    # 4. For HEAD, setati body to b""
    # 5. Construiti and returnati responseul
    
    raise NotImplementedError("TODO: Implement handle_request()")


# ============================================================================
# COD FURNIZAT - NU MODIFICATI
# ============================================================================

def run_server(host: str, port: int, docroot: str):
    """
    starts serverul HTTP.
    Cod furnizat - nu necesita modificari.
    """
    docroot = os.path.abspath(docroot)
    
    if not os.path.isdir(docroot):
        print(f"[error] Directorul docroot nu exista: {docroot}")
        sys.exit(1)
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"[INFO] Server pornit pe http://{host}:{port}/")
        print(f"[INFO] Document root: {docroot}")
        print("[INFO] Press Ctrl+C For oprire")
        
        while True:
            client_socket, client_addr = server_socket.accept()
            print(f"[CONN] Conexiune from {client_addr[0]}:{client_addr[1]}")
            
            try:
                raw_request = client_socket.recv(4096)
                if raw_request:
                    response = handle_request(raw_request, docroot)
                    client_socket.sendall(response)
            except Exception as e:
                print(f"[error] {e}")
                error_response = build_response(
                    500, 
                    {"Content-Type": "text/plain"}, 
                    b"Internal Server Error"
                )
                client_socket.sendall(error_response)
            finally:
                client_socket.close()
                
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user")
    finally:
        server_socket.close()


def main():
    parser = argparse.ArgumentParser(description="Server HTTP simplu")
    parser.add_argument("--host", default="0.0.0.0", help="Adresa de bind")
    parser.add_argument("--port", type=int, default=8081, help="Portul de ascultare")
    parser.add_argument("--docroot", default="www", help="Directorul cu files statice")
    
    args = parser.parse_args()
    run_server(args.host, args.port, args.docroot)


if __name__ == "__main__":
    main()
