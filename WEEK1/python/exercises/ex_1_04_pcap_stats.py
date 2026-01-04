#!/usr/bin/env python3
"""Exercise 1.04: PCAP statistics (Week 1)

This script reads a PCAP file and prints a few basic statistics that are useful
in early labs: total packets, bytes and protocol counts.

It supports two backends:
- scapy (preferred, if installed)
- dpkt (fallback)

Examples
--------
python3 python/exercises/ex_1_04_pcap_stats.py --pcap artifacts/demo.pcap
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any


def stats_with_scapy(path: Path) -> dict[str, Any]:
    from scapy.all import rdpcap  # type: ignore

    pkts = rdpcap(str(path))
    proto = Counter()
    total_bytes = 0

    for p in pkts:
        total_bytes += len(p)
        if p.haslayer("ICMP"):
            proto["ICMP"] += 1
        elif p.haslayer("TCP"):
            proto["TCP"] += 1
        elif p.haslayer("UDP"):
            proto["UDP"] += 1
        else:
            proto["OTHER"] += 1

    return {"packets": len(pkts), "bytes": total_bytes, "protocols": dict(proto)}


def stats_with_dpkt(path: Path) -> dict[str, Any]:
    import dpkt  # type: ignore

    proto = Counter()
    total_bytes = 0
    packets = 0

    with path.open("rb") as f:
        pcap = dpkt.pcap.Reader(f)
        for _ts, buf in pcap:
            packets += 1
            total_bytes += len(buf)
            try:
                eth = dpkt.ethernet.Ethernet(buf)
                ip = eth.data
                if isinstance(ip, dpkt.ip.IP):
                    if ip.p == dpkt.ip.IP_PROTO_ICMP:
                        proto["ICMP"] += 1
                    elif ip.p == dpkt.ip.IP_PROTO_TCP:
                        proto["TCP"] += 1
                    elif ip.p == dpkt.ip.IP_PROTO_UDP:
                        proto["UDP"] += 1
                    else:
                        proto["IP_OTHER"] += 1
                else:
                    proto["NON_IP"] += 1
            except Exception:
                proto["PARSE_ERROR"] += 1

    return {"packets": packets, "bytes": total_bytes, "protocols": dict(proto)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Compute basic statistics from a PCAP file.")
    ap.add_argument("--pcap", type=Path, required=True, help="Path to a PCAP file.")
    ap.add_argument("--backend", choices=["auto", "scapy", "dpkt"], default="auto", help="Parser backend.")
    args = ap.parse_args()

    if not args.pcap.exists():
        print(f"PCAP missing: {args.pcap}")
        return 1

    backend = args.backend
    if backend == "auto":
        try:
            import scapy  # type: ignore  # noqa: F401
            backend = "scapy"
        except Exception:
            backend = "dpkt"

    s = stats_with_scapy(args.pcap) if backend == "scapy" else stats_with_dpkt(args.pcap)
    print(f"PCAP packets={s['packets']} bytes={s['bytes']} protocols={s['protocols']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
