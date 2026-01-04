#!/usr/bin/env python3
"""
Minimal DNS server for Week 10.

It answers A-record queries using a static mapping table.

Author: Computer Networks teaching team, ASE Bucharest.
"""

from __future__ import annotations

import argparse
import socket
import struct
import sys
import time
from typing import Dict, Tuple


def parse_qname(data: bytes, offset: int) -> Tuple[str, int]:
    """Parse namele from querya DNS."""
    labels = []
    while True:
        if offset >= len(data):
            return "", offset
        length = data[offset]
        offset += 1
        if length == 0:
            break
        # Verification pointer (compresie DNS)
        if (length & 0xC0) == 0xC0:
            pointer = ((length & 0x3F) << 8) | data[offset]
            offset += 1
            name, _ = parse_qname(data, pointer)
            return ".".join(labels) + ("." if labels else "") + name, offset
        labels.append(data[offset:offset + length].decode("ascii", errors="replace"))
        offset += length
    return ".".join(labels) + ".", offset


def build_response(request: bytes, ip_map: Dict[str, str]) -> bytes | None:
    """Construieste raspuns DNS for cererea data."""
    if len(request) < 12:
        return None
    
    # Parse header
    (tid, flags, qdcount, ancount, nscount, arcount) = struct.unpack("!HHHHHH", request[:12])
    
    if qdcount < 1:
        return None
    
    # Parse question
    qname, offset = parse_qname(request, 12)
    if offset + 4 > len(request):
        return None
    
    qtype, qclass = struct.unpack("!HH", request[offset:offset + 4])
    question = request[12:offset + 4]
    
    # Respondsm doar la A/IN
    ip = ip_map.get(qname)
    
    if qtype != 1 or qclass != 1 or ip is None:
        # NXDOMAIN
        rflags = 0x8183  # Response, Recursion Available, NXDOMAIN
        header = struct.pack("!HHHHHH", tid, rflags, 1, 0, 0, 0)
        return header + question
    
    # Raspuns pozitiv
    rflags = 0x8180  # Response, Recursion Available, No Error
    header = struct.pack("!HHHHHH", tid, rflags, 1, 1, 0, 0)
    
    # Answer: name pointer (0xC00C = offset 12), type A, class IN, TTL, IP
    name_ptr = 0xC00C
    ttl = 60
    rdata = socket.inet_aton(ip)
    answer = struct.pack("!HHHLH4s", name_ptr, 1, 1, ttl, 4, rdata)
    
    return header + question + answer


def main() -> int:
    parser = argparse.ArgumentParser(description="Server DNS minimal")
    parser.add_argument("--bind", default="0.0.0.0", help="Adresa bind")
    parser.add_argument("--port", type=int, default=53, help="Port UDP")
    parser.add_argument("--a", action="append", default=[], 
                        help="Mapping A: name=ip (ex: api.local.=10.0.0.20)")
    args = parser.parse_args()
    
    # Construire dictionar de mapping-uri
    ip_map: Dict[str, str] = {}
    for item in args.a:
        if "=" in item:
            name, ip = item.split("=", 1)
            # Normalizare: adauga punct final if lipseste
            if not name.endswith("."):
                name = name + "."
            ip_map[name] = ip
    
    # Creation socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((args.bind, args.port))
    
    print(f"[dns] Server pornit pe {args.bind}:{args.port}")
    print(f"[dns] Mapping-uri: {ip_map}")
    
    while True:
        try:
            data, addr = sock.recvfrom(2048)
            
            # Parse query name for logging
            qname, _ = parse_qname(data, 12) if len(data) > 12 else ("?", 0)
            
            response = build_response(data, ip_map)
            if response:
                sock.sendto(response, addr)
                status = "OK" if qname in ip_map else "NXDOMAIN"
            else:
                status = "ERROR"
            
            print(f"[dns] {addr[0]}:{addr[1]} → {qname} → {status}")
            
        except KeyboardInterrupt:
            print("\n[dns] Oprire...")
            break
        except Exception as e:
            print(f"[dns] Error: {e}")
    
    sock.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
