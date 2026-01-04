"""
Shared network utilities for Week 10.

This module contains small helpers used by exercises and scripts, kept minimal to support reproducibility.
"""

from __future__ import annotations

import json
import socket
import struct
import random
from typing import Dict, Tuple, Optional, Any, List

# ==============================================================================
# CONSTANTE
# ==============================================================================

CRLF = b"\r\n"
CRLFCRLF = b"\r\n\r\n"
DEFAULT_TIMEOUT = 5.0

# ==============================================================================
# FUNCTII CITIRE SOCKET
# ==============================================================================

def recv_exact(sock: socket.socket, n: int) -> bytes:
    """
    Citeste exact n bytes from socket.
    
    Aceasta function este necesara deoarece recv() poate returna
    mai putini bytes decat cei solicitati (fragmentare TCP).
    
    Args:
        sock: Socket conectat
        n: Numarul exact de bytes de citit
    
    Returns:
        Exact n bytes
    
    Raises:
        EOFError: Daca conexiunea se inchide inainte de a citi n bytes
    
    Example:
        >>> sock = socket.create_connection(("example.com", 80))
        >>> sock.send(b"GET / HTTP/1.1\\r\\nHost: example.com\\r\\n\\r\\n")
        >>> header_bytes = recv_exact(sock, 100)  # primii 100 bytes
    """
    chunks: List[bytes] = []
    remaining = n
    
    while remaining > 0:
        chunk = sock.recv(remaining)
        if not chunk:
            received = n - remaining
            raise EOFError(
                f"Conexiune inchisa dupa {received}/{n} bytes cititi"
            )
        chunks.append(chunk)
        remaining -= len(chunk)
    
    return b"".join(chunks)


def recv_until(
    sock: socket.socket,
    delimiter: bytes,
    max_size: int = 1024 * 1024
) -> bytes:
    """
    Citeste from socket pana intalneste delimiter-ul (inclusiv).
    
    Args:
        sock: Socket conectat
        delimiter: Secventa de bytes cautata (ex: b"\\r\\n\\r\\n")
        max_size: Limita for prevenirea DoS (default 1MB)
    
    Returns:
        Bytes cititi, inclusiv delimiter-ul
    
    Raises:
        EOFError: Daca conexiunea se inchide inainte de delimiter
        ValueError: Daca se depaseste max_size
    
    Example:
        >>> # Citeste headerele HTTP (pana la linie goala)
        >>> headers_raw = recv_until(sock, b"\\r\\n\\r\\n")
    """
    buffer = bytearray()
    
    while True:
        if len(buffer) > max_size:
            raise ValueError(
                f"Depasit limita de {max_size} bytes fara a gasi delimiter"
            )
        
        chunk = sock.recv(4096)
        if not chunk:
            raise EOFError(
                f"Conexiune inchisa dupa {len(buffer)} bytes, "
                f"fara a gasi delimiter"
            )
        
        buffer.extend(chunk)
        
        idx = buffer.find(delimiter)
        if idx != -1:
            return bytes(buffer[: idx + len(delimiter)])

# ==============================================================================
# PARSARE HTTP
# ==============================================================================

def parse_http_start_line(line: str) -> Dict[str, str]:
    """
    Parse prima linie fromtr-un mesaj HTTP.
    
    Pentru cereri: "GET /path HTTP/1.1"
    Pentru raspunsuri: "HTTP/1.1 200 OK"
    
    Args:
        line: Prima linie (without CRLF)
    
    Returns:
        Dict with componentele parsate
    
    Example:
        >>> parse_http_start_line("HTTP/1.1 200 OK")
        {'version': 'HTTP/1.1', 'status': '200', 'reason': 'OK'}
        
        >>> parse_http_start_line("GET /api/users HTTP/1.1")
        {'method': 'GET', 'path': '/api/users', 'version': 'HTTP/1.1'}
    """
    parts = line.split(" ", 2)
    
    if len(parts) < 2:
        return {"raw": line}
    
    # Raspuns HTTP (incepe with HTTP/)
    if parts[0].startswith("HTTP/"):
        return {
            "version": parts[0],
            "status": parts[1],
            "reason": parts[2] if len(parts) > 2 else ""
        }
    
    # Cerere HTTP
    return {
        "method": parts[0],
        "path": parts[1],
        "version": parts[2] if len(parts) > 2 else "HTTP/1.0"
    }


def parse_http_headers(raw: bytes) -> Tuple[str, Dict[str, str]]:
    """
    Parse blowithl de headere HTTP fromtr-un buffer.
    
    Args:
        raw: Buffer care contine headerele (inclusiv CRLFCRLF)
    
    Returns:
        Tuplu (start_line, dict_headere)
        Headerele sunt normalize la lowercase for consistenta
    
    Raises:
        ValueError: Daca buffer-ul nu contine CRLFCRLF
    
    Example:
        >>> raw = b"HTTP/1.1 200 OK\\r\\nContent-Type: text/html\\r\\n\\r\\n"
        >>> start, headers = parse_http_headers(raw)
        >>> start
        'HTTP/1.1 200 OK'
        >>> headers['content-type']
        'text/html'
    """
    if CRLFCRLF not in raw:
        raise ValueError("Buffer HTTP invalid: lipseste CRLFCRLF")
    
    header_block = raw.split(CRLFCRLF, 1)[0].decode("iso-8859-1")
    lines = header_block.split("\r\n")
    
    start_line = lines[0]
    headers: Dict[str, str] = {}
    
    for line in lines[1:]:
        if not line.strip():
            continue
        if ":" not in line:
            continue
        
        key, value = line.split(":", 1)
        # Normalizare: lowercase for compatibilitate
        headers[key.strip().lower()] = value.strip()
    
    return start_line, headers

# ==============================================================================
# PROBE SERVICII
# ==============================================================================

def tcp_connect(
    host: str,
    port: int,
    timeout: float = DEFAULT_TIMEOUT
) -> bool:
    """
    Verifica if un port TCP este deschis.
    
    Args:
        host: Adresa IP or hostname
        port: Numar port
        timeout: Timeout conexiune
    
    Returns:
        True if conexiunea reuseste
    
    Example:
        >>> tcp_connect("google.com", 443)
        True
        >>> tcp_connect("localhost", 12345)
        False
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, socket.error, OSError):
        return False


def tcp_banner(
    host: str,
    port: int,
    timeout: float = DEFAULT_TIMEOUT,
    max_bytes: int = 1024
) -> str:
    """
    Conecteaza TCP and returneaza banner-ul serviciului.
    
    Multe servicii trimit un banner la connection (SSH, FTP, SMTP).
    
    Args:
        host: Adresa IP or hostname
        port: Numar port
        timeout: Timeout for operatii
        max_bytes: Numarul maxim de bytes de citit
    
    Returns:
        Banner-ul serviciului (text)
    
    Raises:
        Exception: Daca conexiunea esueaza or timeout
    
    Example:
        >>> banner = tcp_banner("ssh.example.com", 22)
        >>> banner.startswith("SSH-")
        True
    """
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.settimeout(timeout)
        data = sock.recv(max_bytes)
    
    # Banner poate contine bytes non-UTF8
    return data.decode("utf-8", errors="replace").strip()


def http_get(
    host: str,
    port: int,
    path: str = "/",
    timeout: float = DEFAULT_TIMEOUT
) -> Tuple[int, Dict[str, str], bytes]:
    """
    Exewithta GET HTTP simplu (without TLS) for probe rapide.
    
    Args:
        host: Adresa server
        port: Port HTTP
        path: Calea resursei
        timeout: Timeout operatii
    
    Returns:
        Tuplu (status_code, headers, body)
    
    Example:
        >>> code, headers, body = http_get("example.com", 80, "/")
        >>> code
        200
        >>> "content-type" in headers
        True
    """
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Connection: close\r\n"
        f"User-Agent: LabClient/1.0\r\n"
        f"\r\n"
    ).encode("ascii")
    
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.sendall(request)
        
        # Citeste headere
        header_raw = recv_until(sock, CRLFCRLF, max_size=64 * 1024)
        start_line, headers = parse_http_headers(header_raw)
        
        # Extrage status code
        parsed = parse_http_start_line(start_line)
        status = int(parsed.get("status", 0))
        
        # Citeste body (simplificat: tot ce mai vine)
        body_chunks = []
        while True:
            chunk = sock.recv(8192)
            if not chunk:
                break
            body_chunks.append(chunk)
        
        body = b"".join(body_chunks)
    
    return status, headers, body

# ==============================================================================
# DNS MANUAL
# ==============================================================================

def dns_query_a(
    name: str,
    server: Tuple[str, int] = ("8.8.8.8", 53),
    timeout: float = DEFAULT_TIMEOUT
) -> List[str]:
    """
    Exewithta query DNS de tip A (manual, without dnslib).
    
    Aceasta function demonstreaza structura packetelor DNS
    without a folosi biblioteci externe.
    
    Args:
        name: Numele de domeniu de interogat
        server: Tuplu (adresa_server_dns, port)
        timeout: Timeout for raspuns
    
    Returns:
        Lista de adrese IPv4 gasite
    
    Example:
        >>> ips = dns_query_a("example.com")
        >>> len(ips) > 0
        True
        >>> all("." in ip for ip in ips)
        True
    """
    # Construire query DNS
    transaction_id = random.ranfromt(0, 65535).to_bytes(2, "big")
    
    # Flags: standard query (0x0100)
    flags = b"\x01\x00"
    
    # Counters: 1 question, 0 answers, 0 authority, 0 additional
    counts = b"\x00\x01\x00\x00\x00\x00\x00\x00"
    
    # Question section: encode name
    qname_parts = []
    for label in name.strip(".").split("."):
        qname_parts.append(bytes([len(label)]) + label.encode("ascii"))
    qname_parts.append(b"\x00")  # terminare
    qname = b"".join(qname_parts)
    
    # QTYPE=A (1), QCLASS=IN (1)
    qtype_qclass = b"\x00\x01\x00\x01"
    
    query = transaction_id + flags + counts + qname + qtype_qclass
    
    # Trimitere and primire
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        sock.sendto(query, server)
        response, _ = sock.recvfrom(4096)
    
    # Parsare raspuns (simplificat)
    if len(response) < 12:
        return []
    
    # Verification transaction ID
    if response[:2] != transaction_id:
        return []
    
    # ANCOUNT (offset 6-7)
    ancount = int.from_bytes(response[6:8], "big")
    
    if ancount == 0:
        return []
    
    # Sarim peste header and question section
    # Pentru simplitate, cautam direct recordurile A
    addresses = []
    idx = 12
    
    # Sari peste question
    while idx < len(response) and response[idx] != 0:
        idx += response[idx] + 1
    idx += 5  # null byte + QTYPE + QCLASS
    
    # Parse answers
    for _ in range(ancount):
        if idx >= len(response):
            break
        
        # Name (poate fi pointer)
        if response[idx] & 0xC0 == 0xC0:
            idx += 2
        else:
            while idx < len(response) and response[idx] != 0:
                idx += response[idx] + 1
            idx += 1
        
        if idx + 10 > len(response):
            break
        
        rtype = int.from_bytes(response[idx:idx+2], "big")
        idx += 2
        rclass = int.from_bytes(response[idx:idx+2], "big")
        idx += 2
        ttl = int.from_bytes(response[idx:idx+4], "big")
        idx += 4
        rdlength = int.from_bytes(response[idx:idx+2], "big")
        idx += 2
        
        if rtype == 1 and rclass == 1 and rdlength == 4:
            # Record A
            ip = ".".join(str(b) for b in response[idx:idx+4])
            addresses.append(ip)
        
        idx += rdlength
    
    return addresses

# ==============================================================================
# UTILITARE JSON
# ==============================================================================

def pretty_json(data: Any, indent: int = 2) -> str:
    """
    Formateaza date ca JSON citibil.
    
    Args:
        data: Orice structura serializabila JSON
        indent: Numarul de spatii for indentare
    
    Returns:
        String JSON formatat
    """
    return json.dumps(
        data,
        ensure_ascii=False,
        indent=indent,
        sort_keys=True
    )


def safe_json_loads(raw: bytes) -> Optional[Any]:
    """
    Parse JSON with gestionarea erorilor.
    
    Args:
        raw: Bytes reprezentand JSON
    
    Returns:
        Obiectul parsat or None if invalid
    """
    try:
        return json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
