#!/usr/bin/env python3
"""
EXERCISE 4: Rate Limiting
===========================
Subject: Computer Networks, Week 8
Level: Intermediate
estimated time: 20 minutes

OBJECTIVES:
- Intelegerea conceptului de rate limiting
- Implementarea a algoritm de limitare cereri
- Protectia serverului impotriva abuzurilor
- Returna codului 429 Too Many Requests

INSTRUCTIONS:
1. Complete the functions marked with TODO
2. Run the tests: python3 -m pytest tests/test_ex04.py -v
3. Test manually:
   for i in {1..15}; do curl -w "%{http_code}\\n" http://localhost:8081/; done

EVALUATION:
- Algoritm corect: 40%
- Thread safety: 30%
- Response 429: 20%
- Cleanup expired: 10%

© Revolvix&Hypotheticalandrei
"""

import socket
import time
import threading
import argparse
from typing import Dict, List, Tuple
from collections import defaultdict
from dataclasses import dataclass, field

# ============================================================================
# CONSTANTS
# ============================================================================

DEFAULT_MAX_REQUESTS = 10  # cereri permise
DEFAULT_WINDOW_SECONDS = 60  # in this fereastra de timp
CLEANUP_INTERVAL = 60  # cat de des curatam timestamp-uri expirate


# ============================================================================
# TODO: Implement this CLASA
# ============================================================================

@dataclass
class RateLimiter:
    """
    Rate limiter folosind algoritm sliding window.
    
    Functionare:
    - For fiecare IP, mentine o lista de timestamp-uri ale cererilor
    - to fiecare request noua:
      1. Elimina timestamp-urile mai vechi decat window_seconds
      2. Check if numarul de cereri e sub max_requests
      3. If yes, append the current timestamp and allow the request
      4. If not, reject the request (429)
    
    Thread Safety:
    - Mai multe thread-uri pot apela check() simultan
    - use Lock For sincronizare
    
    Exemple:
        >>> limiter = RateLimiter(max_requests=2, window_seconds=60)
        >>> limiter.check("192.168.1.1")
        True
        >>> limiter.check("192.168.1.1")
        True
        >>> limiter.check("192.168.1.1")  # third request in aceeaand secunda
        False
    """
    
    max_requests: int = DEFAULT_MAX_REQUESTS
    window_seconds: int = DEFAULT_WINDOW_SECONDS
    
    # TODO: Adaugati campurile necesare:
    # - requests: Dict[str, List[float]] - IP -> lista timestamp-uri
    # - lock: threading.Lock() - For thread safety
    
    def __post_init__(self):
        """Initializare dupa crearea dataclass-ului."""
        # TODO: Initializati:
        # - self.requests = defaultdict(list)
        # - self.lock = threading.Lock()
        raise NotImplementedError("TODO: Implement __post_init__")
    
    def check(self, client_ip: str) -> bool:
        """
        Check if clientul poate face o request noua.
        
        Args:
            client_ip: Adresa IP a clientului
        
        Returns:
            True if requesta e permisa, False if limita e depaandta
        
        ALGORITM (sliding window):
        1. Obtine timestamp curent
        2. Cu lock tinut:
           a. Elimina timestamp-uri expirate (mai vechi decat window_seconds)
           b. Numara cererile ramase
           c. If < max_requests: append current timestamp, return True
           d. Altfel: return False
        
        HINT:
        - use time.time() For timestamp
        - cutoff = now - window_seconds
        - Pastrati doar timestamp-urile > cutoff
        """
        
        # TODO: Implement verificarea rate limit
        raise NotImplementedError("TODO: Implement check")
    
    def get_remaining(self, client_ip: str) -> int:
        """
        Returns cate cereri mai poate face clientul.
        
        Returns:
            Numarul de cereri ramase in fereastra curenta
        """
        
        # TODO: Implement calculul cererilor ramase
        raise NotImplementedError("TODO: Implement get_remaining")
    
    def get_reset_time(self, client_ip: str) -> float:
        """
        Returns cate secunde pana se reseteaza limita.
        
        Returns:
            Secundele pana cand cea mai veche request expira
        """
        
        # TODO: Implement calculul timpului de reset
        raise NotImplementedError("TODO: Implement get_reset_time")
    
    def cleanup_expired(self):
        """
        Curata toate timestamp-urile expirate din toate IP-urile.
        Apelata periodic de un thread de cleanup.
        """
        
        # TODO: Implement curatarea
        #
        # steps:
        # 1. Cu lock tinut
        # 2. For fiecare IP
        # 3. Elimina timestamp-uri expirate
        # 4. If the list is empty, remove the IP from the dictionary
        
        raise NotImplementedError("TODO: Implement cleanup_expired")
    
    def get_stats(self) -> Dict[str, any]:
        """
        Returns statistici despre rate limiter.
        
        Returns:
            Dict cu: total_ips, total_requests, config
        """
        
        # TODO: Implement statistici
        raise NotImplementedError("TODO: Implement get_stats")


# ============================================================================
# TODO: IMPLEMENT THIS FUNCTION
# ============================================================================

def build_rate_limit_response(limiter: RateLimiter, client_ip: str) -> bytes:
    """
    Build responseul 429 Too Many Requests.
    
    Args:
        limiter: Instanta RateLimiter
        client_ip: IP-ul clientului
    
    Returns:
        Raspunsul HTTP 429 in bytes
    
    HEADERS SPECIALE:
    - Retry-After: numarul de secunde pana to reset
    - X-RateLimit-Limit: limita maxima
    - X-RateLimit-Remaining: cereri ramase (0)
    - X-RateLimit-Reset: timestamp Unix cand se reseteaza
    
    BODY:
        {
            "error": "Too Many Requests",
            "message": "Rate limit exceeded. Try again in X seconds.",
            "retry_after": X
        }
    """
    
    # TODO: Implement responseul 429
    #
    # steps:
    # 1. Calculati retry_after cu limiter.get_reset_time()
    # 2. Construiti body JSON
    # 3. Add special headers For rate limiting
    # 4. Construiti and returnati responseul HTTP complete
    
    raise NotImplementedError("TODO: Implement build_rate_limit_response")


# ============================================================================
# TODO: IMPLEMENT THIS FUNCTION
# ============================================================================

def add_rate_limit_headers(response: bytes, limiter: RateLimiter, client_ip: str) -> bytes:
    """
    Adauga headers de rate limit to un response existent.
    
    Args:
        response: Raspunsul HTTP original
        limiter: Instanta RateLimiter  
        client_ip: IP-ul clientului
    
    Returns:
        Raspunsul modificat cu headers adaugate
    
    HEADERS DE ADAUGAT:
    - X-RateLimit-Limit: limita maxima
    - X-RateLimit-Remaining: cereri ramase
    - X-RateLimit-Reset: timestamp cand se reseteaza
    
    HINT:
    - Gasiti pozitia lui \\r\\n\\r\\n in response
    - Inserati headers before de \\r\\n\\r\\n Final
    """
    
    # TODO: Implement adaugarea headers
    raise NotImplementedError("TODO: Implement add_rate_limit_headers")


# ============================================================================
# COD FURNIZAT - SERVER CU RATE LIMITING
# ============================================================================

def simple_response(status_code: int, body: str) -> bytes:
    """Build un response HTTP simplu."""
    status_text = {200: "OK", 404: "Not Found", 429: "Too Many Requests"}
    body_bytes = body.encode('utf-8')
    response = (
        f"HTTP/1.1 {status_code} {status_text.get(status_code, 'Unknown')}\r\n"
        f"Content-Type: text/plain\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        f"\r\n"
    ).encode('utf-8') + body_bytes
    return response


def run_server(host: str, port: int, max_requests: int, window_seconds: int):
    """starts serverul cu rate limiting."""
    limiter = RateLimiter(max_requests=max_requests, window_seconds=window_seconds)
    
    # Thread For cleanup periodic
    def cleanup_loop():
        while True:
            time.sleep(CLEANUP_INTERVAL)
            limiter.cleanup_expired()
            print(f"[CLEANUP] Stats: {limiter.get_stats()}")
    
    cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
    cleanup_thread.start()
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((host, port))
        server.listen(5)
        print(f"[INFO] Rate-limited server started on http://{host}:{port}/")
        print(f"[INFO] Limita: {max_requests} cereri / {window_seconds} secunde")
        print("[INFO] Press Ctrl+C to stop")
        
        while True:
            client, addr = server.accept()
            client_ip = addr[0]
            
            try:
                # Citim request (simplificat)
                request = client.recv(4096)
                if not request:
                    continue
                
                # Checkm rate limit
                if not limiter.check(client_ip):
                    print(f"[RATE] {client_ip} - BLOCKED")
                    response = build_rate_limit_response(limiter, client_ip)
                    client.sendall(response)
                else:
                    remaining = limiter.get_remaining(client_ip)
                    print(f"[OK] {client_ip} - {remaining} cereri ramase")
                    
                    # Raspuns normal
                    response = simple_response(200, f"Hello! You have {remaining} requests remaining.")
                    response = add_rate_limit_headers(response, limiter, client_ip)
                    client.sendall(response)
                    
            except Exception as e:
                print(f"[ERROR] {e}")
            finally:
                client.close()
                
    except KeyboardInterrupt:
        print("\n[INFO] Server oprit")
    finally:
        server.close()


def main():
    parser = argparse.ArgumentParser(description="Server HTTP cu Rate Limiting")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8081)
    parser.add_argument("--max-requests", type=int, default=10, help="Cereri permise")
    parser.add_argument("--window", type=int, default=60, help="Fereastra in secunde")
    
    args = parser.parse_args()
    run_server(args.host, args.port, args.max_requests, args.window)


if __name__ == "__main__":
    main()
