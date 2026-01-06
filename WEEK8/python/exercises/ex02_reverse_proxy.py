#!/usr/bin/env python3
"""
EXERCISE 2: Completare Reverse Proxy
======================================
Subject: Computer Networks, Week 8
Level: Advanced
estimated time: 30 minutes

OBJECTIVES:
- Intelegerea conceptului de reverse proxy
- Implementarea forward-arii cererilor
- Adaugarea headers de proxy (X-Forwarded-For, Via)
- Implementarea health check For backend-uri

INSTRUCTIONS:
1. Complete the functions marked with TODO
2. Run the tests: python3 -m pytest tests/test_ex02.py -v
3. Test manually:
   - Terminal 1: python3 demo_http_server.py --port 8081
   - Terminal 2: python3 demo_http_server.py --port 8082
   - Terminal 3: python3 ex02_reverse_proxy.py --port 8080 --backends localhost:8081,localhost:8082

EVALUATION:
- Forward corect: 30%
- Headers proxy: 30%
- Round Robin: 20%
- Health check: 20%

© Revolvix&Hypotheticalandrei
"""

import socket
import argparse
import threading
import time
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass

# ============================================================================
# CONSTANTS
# ============================================================================

CRLF = "\r\n"
DOUBLE_CRLF = "\r\n\r\n"
BUFFER_SIZE = 4096
CONNECT_TIMEOUT = 5.0
READ_TIMEOUT = 10.0


# ============================================================================
# STRUCTURI DE DATE
# ============================================================================

@dataclass
class Backend:
    """Reprezentarea a backend server."""
    host: str
    port: int
    healthy: bool = True
    last_check: float = 0.0
    
    def __str__(self):
        status = "✓" if self.healthy else "✗"
        return f"{self.host}:{self.port} [{status}]"
    
    @property
    def address(self) -> Tuple[str, int]:
        return (self.host, self.port)


# ============================================================================
# TODO: Implement this CLASA
# ============================================================================

class RoundRobinBalancer:
    """
    Load balancer cu algoritm Round Robin.
    
    Functionare:
    - Mentine o lista de backend-uri
    - to fiecare apel next_backend(), returneaza urmatorul backend sanatos
    - Cicleaza through backend-uri in ordine
    
    Thread Safety:
    - Trebuie sa fie thread-safe (use Lock)
    - Mai multe thread-uri pot apela next_backend() simultan
    
    Exemple:
        >>> backends = [Backend("localhost", 8081), Backend("localhost", 8082)]
        >>> balancer = RoundRobinBalancer(backends)
        >>> balancer.next_backend().port
        8081
        >>> balancer.next_backend().port
        8082
        >>> balancer.next_backend().port  # revine to primul
        8081
    """
    
    def __init__(self, backends: List[Backend]):
        """
        Initializeaza balancer-ul cu lista de backend-uri.
        
        TODO: Implement:
        - Stocare lista backend-uri
        - Index curent (incepe from 0)
        - Lock For thread safety
        """
        # TODO: Implement initializarea
        raise NotImplementedError("TODO: Implement __init__")
    
    def next_backend(self) -> Optional[Backend]:
        """
        Returns urmatorul backend sanatos.
        
        Returns:
            Backend-ul selectat or None if niciunul nu e sanatos
        
        TODO: Implement:
        1. obtain lock-ul
        2. Cautati primul backend healthy incepand from index curent
        3. Actualizati indexul For urmatorul apel
        4. Returnati backend-ul or None
        
        HINT:
        - use with self.lock For thread safety
        - Parcurgeti circular (modulo len(backends))
        - Verificati maximum len(backends) backend-uri
        """
        # TODO: Implement selectia round robin
        raise NotImplementedError("TODO: Implement next_backend")
    
    def mark_unhealthy(self, backend: Backend):
        """
        Marcheaza un backend ca nesanatos.
        
        TODO: Setati backend.healthy = False
        """
        # TODO: Implement
        raise NotImplementedError("TODO: Implement mark_unhealthy")
    
    def mark_healthy(self, backend: Backend):
        """
        Marcheaza un backend ca sanatos.
        
        TODO: Setati backend.healthy = True
        """
        # TODO: Implement
        raise NotImplementedError("TODO: Implement mark_healthy")
    
    def get_stats(self) -> Dict[str, any]:
        """
        Returns statistici despre backend-uri.
        
        Returns:
            Dict cu: total, healthy, unhealthy, backends
        """
        # TODO: Implement statistici
        raise NotImplementedError("TODO: Implement get_stats")


# ============================================================================
# TODO: IMPLEMENT THIS FUNCTION
# ============================================================================

def add_proxy_headers(request_str: str, client_ip: str, proxy_name: str = "proxy") -> str:
    """
    Adauga or actualizeaza headers specifice proxy-ului.
    
    Args:
        request_str: Request-ul HTTP ca string
        client_ip: IP-ul clientului original
        proxy_name: Numele proxy-ului For header Via
    
    Returns:
        Request-ul modificat cu headers adaugate
    
    HEADERS DE ADAUGAT:
    1. X-Forwarded-For: IP-ul clientului original
       - If exists deja, adaugati to sfarandtul listei: "ip1, ip2, ip3"
    2. X-Forwarded-Proto: "http" (presupunem HTTP)
    3. Via: "1.1 {proxy_name}" 
       - If exists deja, adaugati to sfarandtul listei
    
    Exemple:
        >>> req = "GET / HTTP/1.1\\r\\nHost: localhost\\r\\n\\r\\n"
        >>> modified = add_proxy_headers(req, "192.168.1.100", "myproxy")
        >>> "X-Forwarded-For: 192.168.1.100" in modified
        True
        >>> "Via: 1.1 myproxy" in modified
        True
    
    HINT:
    - Separati request line de headers
    - Parsati headers existente
    - Adaugati/actualizati headers necesare
    - Reconstruiti request-ul
    """
    
    # TODO: Implement adaugarea headers
    #
    # steps sugerati:
    # 1. Split pe DOUBLE_CRLF For a separa headers de body
    # 2. Split prima parte pe CRLF For to obtain lines
    # 3. Prima linie = request line (pastrati intact)
    # 4. Parsati restul ca headers in dictionar
    # 5. Actualizati/adaugati X-Forwarded-For, X-Forwarded-Proto, Via
    # 6. Reconstruiti request-ul
    
    raise NotImplementedError("TODO: Implement add_proxy_headers")


# ============================================================================
# TODO: IMPLEMENT THIS FUNCTION
# ============================================================================

def forward_request(request: bytes, backend: Backend, client_ip: str) -> Optional[bytes]:
    """
    Send request-ul catre un backend and returneaza responseul.
    
    Args:
        request: Request-ul HTTP original in bytes
        backend: Backend-ul tinta
        client_ip: IP-ul clientului original
    
    Returns:
        Raspunsul from backend in bytes, or None in caz de error
    
    steps:
    1. Decodifica request-ul
    2. Modifica Host header For backend
    3. Adauga headers proxy
    4. Deschide conexiune TCP catre backend
    5. Send request-ul modificat
    6. Read responseul complete
    7. Inchide conexiunea
    8. Returns responseul
    
    EDGE CASES:
    - Timeout to conectare
    - error de retea
    - Backend inavailable
    
    HINT:
    - use socket.settimeout() For timeout
    - Cititi responseul in bucle pana cand recv returneaza b""
    - Tratati exceptiile and returnati None to error
    """
    
    # TODO: Implement forwarding-ul
    #
    # steps sugerati:
    # 1. Decodifica request in string
    # 2. Modifica Host header (inlocuiti host original cu backend.host:backend.port)
    # 3. Adaugati headers proxy cu add_proxy_headers()
    # 4. Creati socket TCP
    # 5. Setati timeout
    # 6. Conectati to backend
    # 7. Sendti request-ul
    # 8. Cititi responseul (in bucle)
    # 9. Inchideti socket-ul
    # 10. Returnati responseul
    
    raise NotImplementedError("TODO: Implement forward_request")


# ============================================================================
# TODO: IMPLEMENT THIS FUNCTION
# ============================================================================

def check_backend_health(backend: Backend) -> bool:
    """
    Check if un backend este sanatos (raspunde to cereri).
    
    Args:
        backend: Backend-ul de verificat
    
    Returns:
        True if backend-ul raspunde, False altfel
    
    METODA:
    - Send un request HEAD /
    - Daca primeste response in timeout, e sanatos
    - Actualizeaza backend.last_check cu timestamp curent
    
    HINT:
    - Timeout scurt (2 secunde)
    - Nu conteaza continutul response, doar ca raspunde
    - Tratati toate exceptiile ca nesanatos
    """
    
    # TODO: Implement health check
    #
    # steps sugerati:
    # 1. Creati socket TCP
    # 2. Setati timeout scurt (2s)
    # 3. Incercati sa you conectati to backend
    # 4. Sendti "HEAD / HTTP/1.1\r\nHost: {host}\r\n\r\n"
    # 5. Incercati sa cititi response
    # 6. Actualizati backend.last_check = time.time()
    # 7. Returnati True/False
    
    raise NotImplementedError("TODO: Implement check_backend_health")


# ============================================================================
# COD FURNIZAT - NU MODIFICATI
# ============================================================================

class ReverseProxy:
    """
    Reverse proxy server.
    Cod partial furnizat - trebuie sa Implement metodele TODO.
    """
    
    def __init__(self, host: str, port: int, backends: List[Backend]):
        self.host = host
        self.port = port
        self.balancer = RoundRobinBalancer(backends)
        self.running = False
        self.server_socket = None
        
        # Health check thread
        self.health_check_interval = 30  # secunde
        self.health_thread = None
    
    def start_health_checks(self):
        """starts thread-ul de health check."""
        def health_loop():
            while self.running:
                for backend in self.balancer.backends:
                    is_healthy = check_backend_health(backend)
                    if is_healthy:
                        self.balancer.mark_healthy(backend)
                    else:
                        self.balancer.mark_unhealthy(backend)
                    print(f"[HEALTH] {backend}")
                time.sleep(self.health_check_interval)
        
        self.health_thread = threading.Thread(target=health_loop, daemon=True)
        self.health_thread.start()
    
    def handle_client(self, client_socket: socket.socket, client_addr: Tuple[str, int]):
        """Proceseaza o conexiune client."""
        client_ip = client_addr[0]
        
        try:
            request = client_socket.recv(BUFFER_SIZE)
            if not request:
                return
            
            # Selectam backend
            backend = self.balancer.next_backend()
            if not backend:
                error_response = (
                    b"HTTP/1.1 503 Service Unavailable\r\n"
                    b"Content-Type: text/plain\r\n"
                    b"Content-Length: 23\r\n\r\n"
                    b"No backends available"
                )
                client_socket.sendall(error_response)
                return
            
            print(f"[PROXY] {client_ip} -> {backend}")
            
            # Forward request
            response = forward_request(request, backend, client_ip)
            
            if response:
                client_socket.sendall(response)
            else:
                # Backend a esuat
                self.balancer.mark_unhealthy(backend)
                error_response = (
                    b"HTTP/1.1 502 Bad Gateway\r\n"
                    b"Content-Type: text/plain\r\n"
                    b"Content-Length: 15\r\n\r\n"
                    b"Backend failed"
                )
                client_socket.sendall(error_response)
                
        except Exception as e:
            print(f"[error] {e}")
        finally:
            client_socket.close()
    
    def run(self):
        """starts serverul proxy."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(100)
            self.running = True
            
            print(f"[INFO] Reverse proxy pornit pe http://{self.host}:{self.port}/")
            print(f"[INFO] Backend-uri: {[str(b) for b in self.balancer.backends]}")
            print("[INFO] Press Ctrl+C For oprire")
            
            # starts health checks
            self.start_health_checks()
            
            while self.running:
                try:
                    client_socket, client_addr = self.server_socket.accept()
                    # Handle in thread separat
                    thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_addr),
                        daemon=True
                    )
                    thread.start()
                except socket.error:
                    break
                    
        except KeyboardInterrupt:
            print("\n[INFO] Proxy stopped by user")
        finally:
            self.running = False
            if self.server_socket:
                self.server_socket.close()


def parse_backends(backends_str: str) -> List[Backend]:
    """Parseaza string-ul de backend-uri."""
    backends = []
    for backend_str in backends_str.split(","):
        host, port = backend_str.strip().split(":")
        backends.append(Backend(host=host, port=int(port)))
    return backends


def main():
    parser = argparse.ArgumentParser(description="Reverse Proxy")
    parser.add_argument("--host", default="0.0.0.0", help="Adresa de bind")
    parser.add_argument("--port", type=int, default=8080, help="Portul proxy")
    parser.add_argument(
        "--backends", 
        default="localhost:8081,localhost:8082",
        help="Lista de backend-uri (host:port,host:port,...)"
    )
    
    args = parser.parse_args()
    backends = parse_backends(args.backends)
    
    proxy = ReverseProxy(args.host, args.port, backends)
    proxy.run()


if __name__ == "__main__":
    main()
