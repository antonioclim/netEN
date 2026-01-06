#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
  Exercise 11.03 – Educational DNS Client
═══════════════════════════════════════════════════════════════════════════════

EDUCATIONAL PURPOSE:
  - Understanding DNS packet structure (RFC 1035)
  - Manual implementation of a DNS query
  - Parsing DNS responses for different record types
  - Visualising the DNS resolution process

FEATURES:
  - Support for types: A, AAAA, MX, NS, CNAME, TXT, SOA
  - Verbose mode for debugging
  - Packet hexdump display
  - Support for custom DNS server

DNS PACKET ARCHITECTURE:
  ┌─────────────────────────────────────────┐
  │              HEADER (12 bytes)          │
  │  ID | Flags | QDCOUNT | ANCOUNT | ...   │
  ├─────────────────────────────────────────┤
  │              QUESTION SECTION           │
  │  QNAME | QTYPE | QCLASS                 │
  ├─────────────────────────────────────────┤
  │              ANSWER SECTION             │
  │  NAME | TYPE | CLASS | TTL | RDATA      │
  └─────────────────────────────────────────┘

USAGE:
  python3 ex_11_03_dns_client.py --query google.com --type A
  python3 ex_11_03_dns_client.py --query google.com --type MX
  python3 ex_11_03_dns_client.py --query ase.ro --type NS -v
═══════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import argparse
import socket
import struct
import random
import sys
from dataclasses import dataclass
from typing import List, Tuple, Optional

# DNS Constants
DNS_PORT = 53
DEFAULT_DNS_SERVER = "8.8.8.8"

# DNS record types (RFC 1035 + extensions)
RECORD_TYPES = {
    "A": 1,        # IPv4 address
    "NS": 2,       # Nameserver
    "CNAME": 5,    # Canonical name
    "SOA": 6,      # Start of Authority
    "MX": 15,      # Mail exchange
    "TXT": 16,     # Text record
    "AAAA": 28,    # IPv6 address
}

RECORD_TYPES_REVERSE = {v: k for k, v in RECORD_TYPES.items()}

# DNS Classes
DNS_CLASS_IN = 1  # Internet

# Flags
DNS_FLAG_QR = 0x8000      # Query/Response
DNS_FLAG_RD = 0x0100      # Recursion Desired
DNS_FLAG_RA = 0x0080      # Recursion Available
DNS_FLAG_AA = 0x0400      # Authoritative Answer

# Response codes
RCODE_NAMES = {
    0: "NOERROR",
    1: "FORMERR",
    2: "SERVFAIL",
    3: "NXDOMAIN",
    4: "NOTIMP",
    5: "REFUSED",
}


@dataclass
class DNSRecord:
    """Representation of a DNS record."""
    name: str
    type_: int
    class_: int
    ttl: int
    rdata: str
    
    @property
    def type_name(self) -> str:
        return RECORD_TYPES_REVERSE.get(self.type_, f"TYPE{self.type_}")


def encode_domain_name(domain: str) -> bytes:
    """
    Encode a domain name in DNS format.
    
    Example: "www.google.com" → b'\x03www\x06google\x03com\x00'
    
    Format: each label is prefixed with its length, terminated with 0x00.
    """
    result = b""
    for label in domain.split("."):
        if label:
            encoded_label = label.encode("ascii")
            result += struct.pack("B", len(encoded_label)) + encoded_label
    result += b"\x00"
    return result


def decode_domain_name(data: bytes, offset: int) -> Tuple[str, int]:
    """
    Decode a domain name from DNS response.
    
    Handles pointer compression (RFC 1035, section 4.1.4):
    - If first 2 bits are 11, the following 14 bits are the pointer offset.
    
    Returns: (domain_name, new_offset)
    """
    labels = []
    original_offset = offset
    jumped = False
    
    while True:
        if offset >= len(data):
            break
            
        length = data[offset]
        
        # Check compression pointer (first 2 bits = 11)
        if (length & 0xC0) == 0xC0:
            if not jumped:
                original_offset = offset + 2
            # Calculate pointer offset (14 bits)
            pointer = ((length & 0x3F) << 8) | data[offset + 1]
            offset = pointer
            jumped = True
            continue
        
        if length == 0:
            offset += 1
            break
        
        offset += 1
        labels.append(data[offset:offset + length].decode("ascii", errors="replace"))
        offset += length
    
    return ".".join(labels), original_offset if jumped else offset


def build_dns_query(domain: str, record_type: int, transaction_id: int) -> bytes:
    """
    Build a DNS query packet.
    
    Header (12 bytes):
      - ID (2): transaction identifier
      - Flags (2): QR=0 (query), RD=1 (recursion desired)
      - QDCOUNT (2): 1 (single question)
      - ANCOUNT (2): 0
      - NSCOUNT (2): 0
      - ARCOUNT (2): 0
    
    Question:
      - QNAME: encoded domain
      - QTYPE (2): record type
      - QCLASS (2): IN (1)
    """
    # Header
    flags = DNS_FLAG_RD  # Recursion Desired
    header = struct.pack(
        ">HHHHHH",
        transaction_id,  # ID
        flags,           # Flags
        1,               # QDCOUNT
        0,               # ANCOUNT
        0,               # NSCOUNT
        0                # ARCOUNT
    )
    
    # Question section
    question = encode_domain_name(domain)
    question += struct.pack(">HH", record_type, DNS_CLASS_IN)
    
    return header + question


def parse_dns_response(data: bytes, verbose: bool = False) -> Tuple[int, List[DNSRecord]]:
    """
    Parse DNS response.
    
    Returns: (rcode, list of records)
    """
    if len(data) < 12:
        raise ValueError("DNS response too short")
    
    # Parse header
    (trans_id, flags, qdcount, ancount, nscount, arcount) = struct.unpack(">HHHHHH", data[:12])
    
    rcode = flags & 0x000F
    is_response = bool(flags & DNS_FLAG_QR)
    is_authoritative = bool(flags & DNS_FLAG_AA)
    recursion_available = bool(flags & DNS_FLAG_RA)
    
    if verbose:
        print(f"\n[DEBUG] Header:")
        print(f"  Transaction ID: 0x{trans_id:04X}")
        print(f"  Is Response: {is_response}")
        print(f"  Is Authoritative: {is_authoritative}")
        print(f"  Recursion Available: {recursion_available}")
        print(f"  RCODE: {rcode} ({RCODE_NAMES.get(rcode, 'UNKNOWN')})")
        print(f"  Questions: {qdcount}, Answers: {ancount}, NS: {nscount}, Additional: {arcount}")
    
    offset = 12
    
    # Skip question section
    for _ in range(qdcount):
        name, offset = decode_domain_name(data, offset)
        offset += 4  # QTYPE + QCLASS
    
    # Parse answer section
    records: List[DNSRecord] = []
    
    for section_name, count in [("Answer", ancount), ("Authority", nscount), ("Additional", arcount)]:
        for _ in range(count):
            if offset >= len(data):
                break
                
            name, offset = decode_domain_name(data, offset)
            
            if offset + 10 > len(data):
                break
            
            (rtype, rclass, ttl, rdlength) = struct.unpack(">HHIH", data[offset:offset + 10])
            offset += 10
            
            rdata_raw = data[offset:offset + rdlength]
            offset += rdlength
            
            # Parse RDATA based on type
            rdata = parse_rdata(rtype, rdata_raw, data)
            
            records.append(DNSRecord(
                name=name,
                type_=rtype,
                class_=rclass,
                ttl=ttl,
                rdata=rdata
            ))
    
    return rcode, records


def parse_rdata(rtype: int, rdata: bytes, full_packet: bytes) -> str:
    """Parse RDATA based on record type."""
    
    if rtype == RECORD_TYPES["A"]:  # IPv4
        if len(rdata) == 4:
            return ".".join(str(b) for b in rdata)
        return f"<invalid A: {rdata.hex()}>"
    
    elif rtype == RECORD_TYPES["AAAA"]:  # IPv6
        if len(rdata) == 16:
            parts = [f"{rdata[i]:02x}{rdata[i+1]:02x}" for i in range(0, 16, 2)]
            return ":".join(parts)
        return f"<invalid AAAA: {rdata.hex()}>"
    
    elif rtype == RECORD_TYPES["MX"]:  # Mail exchange
        if len(rdata) >= 2:
            preference = struct.unpack(">H", rdata[:2])[0]
            # MX exchange may use compression, so we need to parse with reference to the full packet
            # Simplification: assume no compression in RDATA
            exchange = decode_name_from_rdata(rdata[2:])
            return f"{preference} {exchange}"
        return f"<invalid MX: {rdata.hex()}>"
    
    elif rtype == RECORD_TYPES["NS"]:  # Nameserver
        return decode_name_from_rdata(rdata)
    
    elif rtype == RECORD_TYPES["CNAME"]:  # Canonical name
        return decode_name_from_rdata(rdata)
    
    elif rtype == RECORD_TYPES["TXT"]:  # Text
        # TXT: one or more <length><text> pairs
        texts = []
        pos = 0
        while pos < len(rdata):
            length = rdata[pos]
            pos += 1
            if pos + length <= len(rdata):
                texts.append(rdata[pos:pos + length].decode("utf-8", errors="replace"))
                pos += length
        return " ".join(f'"{t}"' for t in texts)
    
    elif rtype == RECORD_TYPES["SOA"]:  # Start of Authority
        try:
            mname = decode_name_from_rdata(rdata)
            return f"SOA {mname} ..."
        except:
            return f"<SOA: {rdata.hex()[:40]}...>"
    
    else:
        return f"<{RECORD_TYPES_REVERSE.get(rtype, f'TYPE{rtype}')}: {rdata.hex()}>"


def decode_name_from_rdata(data: bytes) -> str:
    """Decode a domain name from RDATA (without compression)."""
    labels = []
    pos = 0
    while pos < len(data):
        length = data[pos]
        if length == 0:
            break
        pos += 1
        if pos + length <= len(data):
            labels.append(data[pos:pos + length].decode("ascii", errors="replace"))
            pos += length
    return ".".join(labels)


def hexdump(data: bytes, prefix: str = "") -> str:
    """Format binary data as hexdump."""
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{prefix}{i:04X}  {hex_part:<48}  {ascii_part}")
    return "\n".join(lines)


def dns_query(domain: str, record_type: str, server: str, timeout: float, verbose: bool) -> None:
    """Execute DNS query and display results."""
    
    if record_type not in RECORD_TYPES:
        print(f"[ERROR] Unknown type: {record_type}")
        print(f"Supported types: {', '.join(RECORD_TYPES.keys())}")
        sys.exit(1)
    
    rtype = RECORD_TYPES[record_type]
    transaction_id = random.randint(0, 0xFFFF)
    
    print(f"\n{'═' * 60}")
    print(f"DNS Query: {domain} ({record_type})")
    print(f"Server: {server}:{DNS_PORT}")
    print(f"{'═' * 60}")
    
    # Build query
    query = build_dns_query(domain, rtype, transaction_id)
    
    if verbose:
        print(f"\n[DEBUG] Query packet ({len(query)} bytes):")
        print(hexdump(query, "  "))
    
    # Send and receive
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        
        sock.sendto(query, (server, DNS_PORT))
        response, addr = sock.recvfrom(4096)
        
        if verbose:
            print(f"\n[DEBUG] Response packet ({len(response)} bytes):")
            print(hexdump(response, "  "))
        
        sock.close()
        
    except socket.timeout:
        print(f"\n[ERROR] Timeout after {timeout} seconds")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    
    # Parse response
    try:
        rcode, records = parse_dns_response(response, verbose)
    except Exception as e:
        print(f"\n[ERROR] Response parsing: {e}")
        sys.exit(1)
    
    # Display results
    print(f"\nStatus: {RCODE_NAMES.get(rcode, f'RCODE={rcode}')}")
    
    if rcode != 0:
        print(f"\n[!] Query failed with code: {RCODE_NAMES.get(rcode, rcode)}")
        return
    
    if not records:
        print("\n[!] No records found")
        return
    
    print(f"\nRecords ({len(records)}):")
    print("-" * 60)
    
    for rec in records:
        print(f"  {rec.name}")
        print(f"    Type: {rec.type_name}")
        print(f"    TTL: {rec.ttl}s")
        print(f"    Data: {rec.rdata}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Educational DNS client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --query google.com --type A
  %(prog)s --query google.com --type MX
  %(prog)s --query ase.ro --type NS -v

Supported types: A, AAAA, MX, NS, CNAME, TXT, SOA
        """
    )
    parser.add_argument("--query", "-q", required=True,
                        help="Domain to query")
    parser.add_argument("--type", "-t", default="A",
                        help="Record type (default: A)")
    parser.add_argument("--server", "-s", default=DEFAULT_DNS_SERVER,
                        help=f"DNS server (default: {DEFAULT_DNS_SERVER})")
    parser.add_argument("--timeout", type=float, default=5.0,
                        help="Timeout in seconds (default: 5)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Detailed output (debug)")
    
    args = parser.parse_args()
    dns_query(args.query, args.type.upper(), args.server, args.timeout, args.verbose)


if __name__ == "__main__":
    main()
