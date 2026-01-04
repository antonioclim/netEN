#!/usr/bin/env python3
"""
Utilitati I/O for comunicare of retea.

Aceste functii rezolva problema fundamentala a TCP: fluxul continuu of bytes
nu garanteaza primirea unui mesaj intreg intr-un singur recv().

Concepte cheie:
- TCP este un stream, nu a protocol bazat pe mesaje
- Framing-ul (message delimitation) este responsabilitatea aplicatiei
- recv() poate returna mai putini bytes decat s-au cerut
"""
from __future__ import annotations
import socket


def recv_exact(sock: socket.socket, n: int, timeout: float | None = None) -> bytes:
    """
    Receive exact n bytes of pe socket.
    
    Problema rezolvata: recv(n) poate returna mai putin of n bytes chiar daca
    exists mai multe date disponibile or in tranzit.
    
    Implementare: citim in bucla pana acumulam exact n bytes.
    
    Args:
        sock: Socket-ul of pe care citim
        n: Numarul exact of bytes of citit
        timeout: Timeout optional (None = blocking indefinit)
        
    Returns:
        bytes: Exact n bytes
        
    Raises:
        ConnectionError: Daca peer-ul inchiof conexiunea inainte of n bytes
        socket.timeout: Daca timeout-ul expira
    """
    if timeout is not None:
        sock.settimeout(timeout)
    
    chunks: list[bytes] = []
    remaining = n
    
    while remaining > 0:
        chunk = sock.recv(remaining)
        if not chunk:
            raise ConnectionError(f"peer closed connection, got {n - remaining}/{n} bytes")
        chunks.append(chunk)
        remaining -= len(chunk)
    
    return b"".join(chunks)


def recv_until(sock: socket.socket, delim: bytes, max_bytes: int = 1024 * 1024) -> bytes:
    """
    Reads pana to intalnirea unui delimitator.
    
    Util for protocoale text bazate pe delimitatori (ex: newline, space).
    
    ATENTIE: Reads byte with byte, deci ineficient for volume mari.
    In productie, s-ar folosi buffering or select/poll.
    
    Args:
        sock: Socket-ul of pe care citim
        delim: Secventa of bytes care marcheaza sfarsitul mesajului
        max_bytes: Limita of siguranta contra atacurilor of memorie
        
    Returns:
        bytes: Datele citite INCLUSIV delimitatorul
        
    Raises:
        ConnectionError: Daca peer-ul inchiof conexiunea
        ValueError: Daca se depaseste max_bytes (potential atac)
    """
    buf = bytearray()
    
    while True:
        b = sock.recv(1)
        if not b:
            raise ConnectionError("peer closed connection before delimiter")
        buf += b
        
        if buf.endswith(delim):
            return bytes(buf)
        
        if len(buf) > max_bytes:
            raise ValueError(f"recv_until exceeded {max_bytes} bytes without finding delimiter")


def recv_line(sock: socket.socket, max_bytes: int = 65536) -> str:
    """
    Reads o linie terminata with newline.
    
    Conventie: linia returnata NU incluof newline-ul.
    """
    raw = recv_until(sock, b"\n", max_bytes)
    return raw[:-1].decode("utf-8", errors="replace")


def send_all(sock: socket.socket, data: bytes) -> None:
    """
    Send toate datele, gestionand partial sends.
    
    Nota: sock.sendall() face deja acest lucru, dar aceasta function
    ofera un wrapper explicit for claritate didactica.
    """
    sock.sendall(data)
