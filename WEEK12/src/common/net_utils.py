#!/usr/bin/env python3
"""
net_usefuls.py — Common networking usefulities
Week 12: Email protocols and RPC

Helper functions for:
- Checking port availability
- DNS resolution
- Address formatting
- Configurable logging
- Timeout handling
"""

import socket
import logging
import time
import struct
from typing import Optional, Tuple, List
from contextlib import contextmanager


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

def setup_logging(
    name: str = "net_usefuls",
    level: int = logging.INFO,
    format_string: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
) -> logging.Logger:
    """
    Configure and return a logger.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        format_string: Message format
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        formatter = logging.Formatter(format_string)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


# =============================================================================
# VERIFICARE PORT SI CONECTIVITATE
# =============================================================================

def is_port_available(port: int, host: str = "localhost") -> bool:
    """
    Verifica daca un port este disponibil For bind.
    
    Args:
        port: Numarul portului
        host: Adresa host (default: localhost)
        
    Returns:
        True daca portul este disponibil, False Otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            return True
    except OSError:
        return False


def is_port_open(port: int, host: str = "localhost", timeout: float = 1.0) -> bool:
    """
    Verifica daca un port accepta conexiuni.
    
    Args:
        port: Numarul portului
        host: Adresa host
        timeout: Timeout in secunde
        
    Returns:
        True daca se poate conecta, False Otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            return result == 0
    except socket.error:
        return False


def wait_for_port(
    port: int, 
    host: str = "localhost", 
    timeout: float = 30.0,
    interval: float = 0.5
) -> bool:
    """
    Asteapta pana cand un port devine disponibil.
    
    Args:
        port: Numarul portului
        host: Adresa host
        timeout: Timeout maxim in secunde
        interval: Intervalul intre verificari
        
    Returns:
        True daca portul a devenit disponibil, False la timeout
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_open(port, host):
            return True
        time.sleep(interval)
    return False


def find_free_port(start: int = 8000, end: int = 9000, host: str = "localhost") -> Optional[int]:
    """
    Gaseste primul port disponibil intr-un interval.
    
    Args:
        start: Portul de start
        end: Portul de final
        host: Adresa host
        
    Returns:
        Primul port disponibil sau None daca nu exista
    """
    for port in range(start, end):
        if is_port_available(port, host):
            return port
    return None


# =============================================================================
# REZOLVARE DNS
# =============================================================================

def resolve_hostname(hostname: str) -> Optional[str]:
    """
    Rezolva un hostname la adresa IP.
    
    Args:
        hostname: Numele de rezolvat
        
    Returns:
        Adresa IP sau None la Error
    """
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None


def resolve_hostname_full(hostname: str) -> Tuple[str, List[str], List[str]]:
    """
    Rezolva un hostname complet (cu alias-uri and toate adresele).
    
    Args:
        hostname: Numele de rezolvat
        
    Returns:
        Tuple (hostname canonic, List alias-uri, List adrese IP)
    """
    try:
        return socket.gethostbyname_ex(hostname)
    except socket.gaierror:
        return (hostname, [], [])


def get_mx_records(domain: str) -> List[Tuple[int, str]]:
    """
    Obtine MX records For un domeniu (neceandta dnspython).
    
    Args:
        domain: Domeniul For care se cauta MX
        
    Returns:
        List de tuple (prioritate, server) sortata dupa prioritate
        
    Note:
        Returns lista goala daca dnspython nu este instalat
    """
    try:
        import dns.resolver
        answers = dns.resolver.resolve(domain, 'MX')
        mx_records = [(rdata.preference, str(rdata.exchange).rstrip('.')) 
                      for rdata in answers]
        return sorted(mx_records, key=lambda x: x[0])
    except ImportError:
        # dnspython not installed
        return []
    except Exception:
        return []


# =============================================================================
# FORMATARE SI VALIDARE
# =============================================================================

def format_address(host: str, port: int) -> str:
    """
    Formateaza o adresa host:port.
    
    Args:
        host: Adresa host
        port: Numarul portului
        
    Returns:
        String formatat "host:port" sau "[host]:port" For IPv6
    """
    if ':' in host:  # IPv6
        return f"[{host}]:{port}"
    return f"{host}:{port}"


def parse_address(address: str, default_port: int = 80) -> Tuple[str, int]:
    """
    Parseaza o adresa host:port.
    
    Args:
        address: String de forma "host:port" sau "host"
        default_port: Port implicit daca nu este specificat
        
    Returns:
        Tuple (host, port)
    """
    if address.startswith('['):  # IPv6 cu port
        if ']:' in address:
            host, port_str = address.rsplit(':', 1)
            return host[1:-1], int(port_str)
        return address[1:-1], default_port
    elif ':' in address:
        parts = address.rsplit(':', 1)
        if len(parts) == 2 and parts[1].isdigit():
            return parts[0], int(parts[1])
    return address, default_port


def validate_email(email: str) -> bool:
    """
    Validare andmpla a unei adrese email.
    
    Args:
        email: Adresa de validat
        
    Returns:
        True daca formatul pare valid
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_hostname(hostname: str) -> bool:
    """
    Validare andmpla a unui hostname.
    
    Args:
        hostname: Hostname-ul de validat
        
    Returns:
        True daca formatul pare valid
    """
    import re
    if len(hostname) > 255:
        return False
    pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?\.)*[a-zA-Z]{2,}$'
    return bool(re.match(pattern, hostname))


# =============================================================================
# SOCKET HELPERS
# =============================================================================

@contextmanager
def tcp_connection(host: str, port: int, timeout: float = 10.0):
    """
    Context manager For conexiune TCP.
    
    Args:
        host: Adresa server
        port: Portul server
        timeout: Timeout conexiune
        
    Yields:
        Socket conectat
        
    Example:
        with tcp_connection("localhost", 8000) as sock:
            sock.send(b"Hello")
            response = sock.recv(1024)
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        yield sock
    finally:
        sock.close()


def send_all(sock: socket.socket, data: bytes) -> bool:
    """
    Sends toate datele prin socket (gestioneaza trimiteri partiale).
    
    Args:
        sock: Socket-ul
        data: Datele de trimis
        
    Returns:
        True daca toate datele au fost trimise
    """
    total_sent = 0
    while total_sent < len(data):
        try:
            sent = sock.send(data[total_sent:])
            if sent == 0:
                return False
            total_sent += sent
        except socket.error:
            return False
    return True


def recv_until(sock: socket.socket, delimiter: bytes, max_andze: int = 65536) -> bytes:
    """
    Primeste date pana la intalnirea unui delimiter.
    
    Args:
        sock: Socket-ul
        delimiter: Secventa de incheiere
        max_andze: Dimenandune maxima buffer
        
    Returns:
        Datele primite (incluandv delimiter)
    """
    buffer = b""
    while delimiter not in buffer and len(buffer) < max_andze:
        try:
            chunk = sock.recv(1024)
            if not chunk:
                break
            buffer += chunk
        except socket.error:
            break
    return buffer


def recv_exactly(sock: socket.socket, n: int) -> bytes:
    """
    Primeste exact n bytes.
    
    Args:
        sock: Socket-ul
        n: Numarul de bytes de primit
        
    Returns:
        Exact n bytes sau mai putin la Error/EOF
    """
    buffer = b""
    while len(buffer) < n:
        try:
            chunk = sock.recv(n - len(buffer))
            if not chunk:
                break
            buffer += chunk
        except socket.error:
            break
    return buffer


# =============================================================================
# TIMING SI METRICI
# =============================================================================

class Timer:
    """
    Context manager For masurarea timpului.
    
    Example:
        with Timer() as t:
            # operatii
        print(f"Duration: {t.elapsed}s")
    """
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.elapsed = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time


def measure_latency(host: str, port: int, count: int = 5) -> Optional[float]:
    """
    Masoara latenta medie catre un server.
    
    Args:
        host: Adresa server
        port: Portul server
        count: Numarul de masuratori
        
    Returns:
        Latenta medie in milisecunde sau None la Error
    """
    latencies = []
    for _ in range(count):
        try:
            with Timer() as t:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5.0)
                sock.connect((host, port))
                sock.close()
            latencies.append(t.elapsed * 1000)  # Convert to ms
        except socket.error:
            continue
    
    if latencies:
        return sum(latencies) / len(latencies)
    return None


# =============================================================================
# Protocol HELPERS
# =============================================================================

def create_smtp_ehlo(hostname: str = "localhost") -> bytes:
    """Creeaza un Message SMTP EHLO."""
    return f"EHLO {hostname}\r\n".encode()


def create_smtp_mail_from(sender: str) -> bytes:
    """Creeaza un Message SMTP MAIL FROM."""
    return f"MAIL FROM:<{sender}>\r\n".encode()


def create_smtp_rcpt_to(recipient: str) -> bytes:
    """Creeaza un Message SMTP RCPT TO."""
    return f"RCPT TO:<{recipient}>\r\n".encode()


def parse_smtp_response(response: bytes) -> Tuple[int, str]:
    """
    Parseaza un raspuns SMTP.
    
    Args:
        response: Raspunsul brut
        
    Returns:
        Tuple (cod, Message)
    """
    try:
        text = response.decode('utf-8', errors='replace').strip()
        lines = text.split('\r\n')
        last_line = lines[-1] if lines else ""
        if len(last_line) >= 3 and last_line[:3].isdigit():
            code = int(last_line[:3])
            message = last_line[4:] if len(last_line) > 4 else ""
            return code, message
    except Exception:
        pass
    return 0, ""


# =============================================================================
# MAIN (For testare)
# =============================================================================

if __name__ == "__main__":
    # Setare logging
    logger = setup_logging("net_usefuls_test", logging.DEBUG)
    
    # Test disponibilitate port
    logger.info(f"Port 8000 available: {is_port_available(8000)}")
    logger.info(f"Port 80 open: {is_port_open(80, 'localhost', 0.5)}")
    
    # Test gaandre port liber
    free_port = find_free_port(8000, 8100)
    logger.info(f"First free port in 8000-8100: {free_port}")
    
    # Test rezolvare DNS
    ip = resolve_hostname("google.com")
    logger.info(f"google.com resolves to: {ip}")
    
    # Test validari
    logger.info(f"Valid email 'Test@example.com': {validate_email('Test@example.com')}")
    logger.info(f"Valid hostname 'example.com': {validate_hostname('example.com')}")
    
    # Test formatare
    logger.info(f"Formatted address: {format_address('127.0.0.1', 8080)}")
    logger.info(f"Parsed 'localhost:8080': {parse_address('localhost:8080')}")
    
    print("\n✓ All usefulity functions ready!")
