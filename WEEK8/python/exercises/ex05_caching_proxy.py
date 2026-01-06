#!/usr/bin/env python3
"""
EXERCISE CHALLENGE: Caching Proxy
===================================
Subject: Computer Networks, Week 8
Level: Expert
estimated time: 45 minutes

OBJECTIVES:
- Implementarea a cache HTTP in reverse proxy
- Intelegerea headers de cache (Cache-Control, ETag, Last-Modified)
- Optimizarea performantei through reducerea incarcarii backend-ului
- Implementarea statisticilor and managementului cache-ului

INSTRUCTIONS:
1. Complete the functions marked with TODO
2. Testati cu multiple cereri repetate
3. Verificati hit rate cu /cache/stats

EVALUATION:
- Cache storage: 20%
- TTL and expirare: 20%
- Cache-Control parsing: 20%
- Statistics: 20%
- Invalidare: 20%

© Revolvix&Hypotheticalandrei
"""

import socket
import time
import threading
import json
import hashlib
import argparse
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import OrderedDict

# ============================================================================
# CONSTANTS
# ============================================================================

DEFAULT_TTL = 300  # 5 minutes
MAX_CACHE_SIZE = 100  # numar maxim de entries
MAX_ENTRY_SIZE = 1024 * 1024  # 1 MB per entry


# ============================================================================
# STRUCTURI DE DATE
# ============================================================================

@dataclass
class CacheEntry:
    """O intrare in cache."""
    response: bytes           # Raspunsul HTTP complete
    created_at: float         # Timestamp creare
    expires_at: float         # Timestamp expirare
    etag: Optional[str] = None          # ETag For validare
    last_modified: Optional[str] = None  # Last-Modified For validare
    hit_count: int = 0        # Numar de hit-uri
    
    def is_expired(self) -> bool:
        """Check if entry-ul a expirat."""
        return time.time() > self.expires_at
    
    def remaining_ttl(self) -> int:
        """Returns TTL-ul ramas in secunde."""
        return max(0, int(self.expires_at - time.time()))


# ============================================================================
# TODO: Implement this CLASA
# ============================================================================

class HTTPCache:
    """
    Cache HTTP For responseuri.
    
    Functionalitati:
    - Stocare responseuri cu TTL
    - Cheie de cache: METHOD + URL (hash)
    - Respectare Cache-Control headers
    - LRU eviction cand cache-ul e plin
    - Thread-safe
    
    Exemple:
        >>> cache = HTTPCache(default_ttl=60)
        >>> cache.set("GET /index.html", response_bytes, ttl=120)
        >>> entry = cache.get("GET /index.html")
        >>> entry.response
        b'HTTP/1.1 200 OK...'
    """
    
    def __init__(self, default_ttl: int = DEFAULT_TTL, max_size: int = MAX_CACHE_SIZE):
        """
        Initializeaza cache-ul.
        
        TODO: Initializati:
        - self.default_ttl = default_ttl
        - self.max_size = max_size
        - self.cache = OrderedDict() - For LRU
        - self.lock = threading.Lock()
        - self.stats = {"hits": 0, "misses": 0, "evictions": 0}
        """
        raise NotImplementedError("TODO: Implement __init__")
    
    def _generate_key(self, method: str, url: str) -> str:
        """
        Genereaza cheia de cache din method and URL.
        
        HINT: use hash For a evita chei lungi
        """
        
        # TODO: Implement generarea cheii
        # Example: md5 hash al "GET /index.html"
        raise NotImplementedError("TODO: Implement _generate_key")
    
    def get(self, method: str, url: str) -> Optional[CacheEntry]:
        """
        Obtine o intrare din cache.
        
        Args:
            method: Metoda HTTP (GET)
            url: URL-ul cererii
        
        Returns:
            CacheEntry If exists and nu a expirat, None altfel
        
        COMPORTAMENT:
        1. Genereaza cheia
        2. Cu lock tinut:
           a. Check if cheia exista
           b. Check if entry-ul nu a expirat
           c. Actualizeaza hit_count
           d. Muta entry-ul to sfarandtul OrderedDict (LRU)
           e. Actualizeaza stats["hits"] or stats["misses"]
        """
        
        # TODO: Implement get
        raise NotImplementedError("TODO: Implement get")
    
    def set(self, method: str, url: str, response: bytes, 
            ttl: Optional[int] = None, etag: Optional[str] = None,
            last_modified: Optional[str] = None):
        """
        Adauga o intrare in cache.
        
        Args:
            method: Metoda HTTP
            url: URL-ul cererii
            response: Raspunsul HTTP complete
            ttl: Time-to-live in secunde (None = foloseste default)
            etag: ETag For validare
            last_modified: Last-Modified For validare
        
        COMPORTAMENT:
        1. Check if responseul e prea mare (> MAX_ENTRY_SIZE)
        2. Genereaza cheia
        3. Cu lock tinut:
           a. Daca cache-ul e plin, evict (LRU)
           b. Creeaza CacheEntry
           c. Adauga in cache
        """
        
        # TODO: Implement set
        raise NotImplementedError("TODO: Implement set")
    
    def delete(self, method: str, url: str) -> bool:
        """
        Sterge o intrare din cache.
        
        Returns:
            True if a fost sters, False if nu exista
        """
        
        # TODO: Implement delete
        raise NotImplementedError("TODO: Implement delete")
    
    def clear(self):
        """Goleste tot cache-ul."""
        
        # TODO: Implement clear
        raise NotImplementedError("TODO: Implement clear")
    
    def _evict_lru(self):
        """
        Elimina cea mai veche intrare (LRU - Least Recently Used).
        
        HINT: OrderedDict.popitem(last=False) elimina primul element
        """
        
        # TODO: Implement eviction
        raise NotImplementedError("TODO: Implement _evict_lru")
    
    def cleanup_expired(self) -> int:
        """
        Elimina toate intrarile expirate.
        
        Returns:
            Numarul de intrari eliminate
        """
        
        # TODO: Implement cleanup
        raise NotImplementedError("TODO: Implement cleanup_expired")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Returns statistici despre cache.
        
        Returns:
            Dict cu: hits, misses, hit_rate, size, entries
        """
        
        # TODO: Implement statistici
        # hit_rate = hits / (hits + misses) if total > 0
        raise NotImplementedError("TODO: Implement get_stats")


# ============================================================================
# TODO: IMPLEMENT THIS FUNCTION
# ============================================================================

def parse_cache_control(headers: Dict[str, str]) -> Dict[str, Any]:
    """
    Parseaza headerul Cache-Control.
    
    Args:
        headers: Dictionary with headers HTTP
    
    Returns:
        Dict cu directive parsate
    
    FORMAT INPUT:
        Cache-Control: max-age=3600, public, no-transform
    
    FORMAT OUTPUT:
        {
            "max-age": 3600,
            "public": True,
            "no-transform": True,
            "no-cache": False,
            "no-store": False,
            "private": False
        }
    
    DIRECTIVE IMPORTANTE:
    - max-age=N: TTL in secunde
    - no-cache: trebuie revalidat mereu
    - no-store: NU se pune in cache
    - private: doar cache client, nu proxy
    - public: poate fi cached de oricine
    """
    
    # TODO: Implement parsing Cache-Control
    #
    # steps:
    # 1. obtain valoarea header-ului "cache-control"
    # 2. Split pe ","
    # 3. For fiecare directiva:
    #    - Daca contine "=", parsati key=value
    #    - Altfel, e un flag (setati True)
    # 4. Returnati dictionarul
    
    raise NotImplementedError("TODO: Implement parse_cache_control")


# ============================================================================
# TODO: IMPLEMENT THIS FUNCTION
# ============================================================================

def is_cacheable(method: str, status_code: int, 
                 request_headers: Dict[str, str],
                 response_headers: Dict[str, str]) -> Tuple[bool, Optional[int]]:
    """
    Determina if un response poate fi pus in cache.
    
    Args:
        method: Metoda HTTP (doar GET e cacheable)
        status_code: Codul de status (doar 200, 301 sunt cacheable)
        request_headers: Headers din request
        response_headers: Headers din response
    
    Returns:
        Tuple (is_cacheable, ttl_seconds)
        - is_cacheable: True if se poate pune in cache
        - ttl_seconds: TTL-ul calculat or None For default
    
    REGULI:
    1. Doar GET e cacheable
    2. Doar status codes: 200, 203, 204, 206, 300, 301, 404, 405, 410, 414, 501
    3. no-store in request or response → NOT cacheable
    4. private in response → NOT cacheable (For proxy)
    5. max-age in response → foloseste ca TTL
    6. Expires header → calculeaza TTL
    """
    
    # TODO: Implement logica de cacheability
    raise NotImplementedError("TODO: Implement is_cacheable")


# ============================================================================
# TODO: IMPLEMENT THIS FUNCTION
# ============================================================================

def extract_etag_last_modified(response: bytes) -> Tuple[Optional[str], Optional[str]]:
    """
    Extrage ETag and Last-Modified din response.
    
    Args:
        response: Raspunsul HTTP complete
    
    Returns:
        Tuple (etag, last_modified)
    
    HINT:
    - Parsati headers din response
    - Cautati header-ele ETag and Last-Modified
    """
    
    # TODO: Implement extraction
    raise NotImplementedError("TODO: Implement extract_etag_last_modified")


# ============================================================================
# COD FURNIZAT - CACHING PROXY SERVER
# ============================================================================

class CachingProxy:
    """Reverse proxy cu caching."""
    
    def __init__(self, host: str, port: int, backend_host: str, backend_port: int,
                 cache_ttl: int = DEFAULT_TTL):
        self.host = host
        self.port = port
        self.backend = (backend_host, backend_port)
        self.cache = HTTPCache(default_ttl=cache_ttl)
        self.running = False
    
    def forward_to_backend(self, request: bytes) -> Optional[bytes]:
        """Forward request catre backend."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect(self.backend)
            sock.sendall(request)
            
            response = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            
            sock.close()
            return response
        except Exception as e:
            print(f"[ERROR] Backend error: {e}")
            return None
    
    def handle_cache_stats(self) -> bytes:
        """Handler For /cache/stats."""
        stats = self.cache.get_stats()
        body = json.dumps(stats, indent=2).encode('utf-8')
        return (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: application/json\r\n" +
            b"Content-Length: " + str(len(body)).encode() + b"\r\n" +
            b"\r\n" + body
        )
    
    def handle_cache_clear(self) -> bytes:
        """Handler For /cache/clear."""
        self.cache.clear()
        return (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/plain\r\n"
            b"Content-Length: 14\r\n\r\n"
            b"Cache cleared!"
        )
    
    def handle_client(self, client: socket.socket, addr: Tuple[str, int]):
        """Proceseaza un client."""
        try:
            request = client.recv(4096)
            if not request:
                return
            
            # Parse request line
            first_line = request.split(b"\r\n")[0].decode()
            parts = first_line.split(" ")
            method, path = parts[0], parts[1]
            
            # Handle cache management endpoints
            if path == "/cache/stats":
                client.sendall(self.handle_cache_stats())
                return
            if path == "/cache/clear":
                client.sendall(self.handle_cache_clear())
                return
            
            # Check cache For GET
            if method == "GET":
                entry = self.cache.get(method, path)
                if entry:
                    print(f"[CACHE HIT] {method} {path}")
                    # Adauga header X-Cache: HIT
                    response = entry.response
                    # Insert X-Cache header
                    idx = response.find(b"\r\n")
                    modified = response[:idx] + b"\r\nX-Cache: HIT" + response[idx:]
                    client.sendall(modified)
                    return
            
            print(f"[CACHE MISS] {method} {path}")
            
            # Forward to backend
            response = self.forward_to_backend(request)
            if not response:
                error = (
                    b"HTTP/1.1 502 Bad Gateway\r\n"
                    b"Content-Length: 11\r\n\r\n"
                    b"Bad Gateway"
                )
                client.sendall(error)
                return
            
            # Cache response if cacheable
            # Parse status code
            status_line = response.split(b"\r\n")[0].decode()
            status_code = int(status_line.split(" ")[1])
            
            # Parse headers
            headers_end = response.find(b"\r\n\r\n")
            headers_str = response[:headers_end].decode()
            headers = {}
            for line in headers_str.split("\r\n")[1:]:
                if ":" in line:
                    k, v = line.split(":", 1)
                    headers[k.strip().lower()] = v.strip()
            
            cacheable, ttl = is_cacheable(method, status_code, {}, headers)
            if cacheable:
                etag, last_mod = extract_etag_last_modified(response)
                self.cache.set(method, path, response, ttl=ttl, 
                              etag=etag, last_modified=last_mod)
                print(f"[CACHED] {method} {path} (TTL={ttl or 'default'})")
            
            # Add X-Cache: MISS header
            idx = response.find(b"\r\n")
            response = response[:idx] + b"\r\nX-Cache: MISS" + response[idx:]
            
            client.sendall(response)
            
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            client.close()
    
    def run(self):
        """starts proxy-ul."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Cleanup thread
        def cleanup_loop():
            while self.running:
                time.sleep(60)
                removed = self.cache.cleanup_expired()
                if removed > 0:
                    print(f"[CLEANUP] Removed {removed} expired entries")
        
        try:
            server.bind((self.host, self.port))
            server.listen(100)
            self.running = True
            
            cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
            cleanup_thread.start()
            
            print(f"[INFO] Caching proxy pe http://{self.host}:{self.port}/")
            print(f"[INFO] Backend: {self.backend[0]}:{self.backend[1]}")
            print(f"[INFO] Endpoints: /cache/stats, /cache/clear")
            
            while self.running:
                client, addr = server.accept()
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client, addr),
                    daemon=True
                )
                thread.start()
                
        except KeyboardInterrupt:
            print("\n[INFO] Proxy stopped")
        finally:
            self.running = False
            server.close()


def main():
    parser = argparse.ArgumentParser(description="Caching Reverse Proxy")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--backend-host", default="localhost")
    parser.add_argument("--backend-port", type=int, default=8081)
    parser.add_argument("--cache-ttl", type=int, default=300)
    
    args = parser.parse_args()
    proxy = CachingProxy(
        args.host, args.port,
        args.backend_host, args.backend_port,
        args.cache_ttl
    )
    proxy.run()


if __name__ == "__main__":
    main()
