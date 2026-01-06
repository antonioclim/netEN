#!/usr/bin/env python3
"""Week 10 - Minimal custom DNS server (dnslib).

This container is used to demonstrate:
- UDP request/response behaviour
- DNS message structure (questions, answers and RCODE)
- The difference between Docker's embedded DNS and a custom authoritative server

The server responds with static A records for a small set of names.

Examples
--------
From the host:
  dig @127.0.0.1 -p 5353 myservice.lab.local +short

From the debug container:
  dig @dns-server -p 5353 api.lab.local +short
"""

from __future__ import annotations

import argparse
import socket
from typing import Dict

from dnslib import A, DNSRecord, QTYPE, RR


STATIC_RECORDS: Dict[str, str] = {
    "myservice.lab.local": "10.10.10.10",
    "api.lab.local": "10.10.10.20",
    "ssh.lab.local": "172.20.0.22",
    "ftp.lab.local": "172.20.0.21",
    "web.lab.local": "172.20.0.10",
}


def _normalise_name(name: str) -> str:
    # dnslib provides names with a trailing dot.
    return name.rstrip(".").lower()


def build_response(request: DNSRecord) -> DNSRecord:
    reply = request.reply()

    qname = _normalise_name(str(request.q.qname))
    qtype = QTYPE[request.q.qtype]

    if qtype != "A":
        # For teaching simplicity we only implement A queries.
        return reply

    if qname in STATIC_RECORDS:
        reply.add_answer(RR(qname, QTYPE.A, rdata=A(STATIC_RECORDS[qname]), ttl=60))
    else:
        # NXDOMAIN for unknown names.
        reply.header.rcode = 3

    return reply


def main() -> None:
    parser = argparse.ArgumentParser(description="Week 10 DNS server (dnslib)")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address")
    parser.add_argument("--port", type=int, default=5353, help="UDP port")
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.host, args.port))

    print("[INFO] Week 10 DNS server started")
    print(f"[INFO] Bind: {args.host}:{args.port} (UDP)")
    print("[INFO] Records:")
    for k, v in STATIC_RECORDS.items():
        print(f"  - {k} -> {v}")

    while True:
        try:
            data, addr = sock.recvfrom(512)
            request = DNSRecord.parse(data)
            qname = _normalise_name(str(request.q.qname))
            qtype = QTYPE[request.q.qtype]

            print(f"[DNS] Query from {addr[0]}:{addr[1]} - {qname} ({qtype})")

            reply = build_response(request)
            sock.sendto(reply.pack(), addr)
        except Exception as exc:  # pragma: no cover
            print(f"[WARN] Failed to process DNS query: {exc}")


if __name__ == "__main__":
    main()
