#!/usr/bin/env python3
"""Week 13 - Packet sniffer (educational).

This script captures traffic for the Week 13 lab and prints a compact summary of:
- TCP/UDP flows
- basic service identification via ports (HTTP, FTP, MQTT)
- payload snippets for plaintext MQTT when possible

Important
---------
Packet capture typically requires elevated privileges. On Linux, run with sudo:
  sudo python3 python/exercises/ex_03_packet_sniffer.py --iface any --timeout 20

This tool is intended for local lab use only.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import binascii
from typing import Optional

try:
    from scapy.all import sniff, wrpcap  # type: ignore
    from scapy.layers.inet import IP, TCP, UDP  # type: ignore
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "Scapy is required for this exercise. Install via: make setup\n"
        f"Import error: {exc}"
    )


PORT_LABELS = {
    21: "FTP",
    80: "HTTP",
    1883: "MQTT",
    8883: "MQTT-TLS",
    6200: "STUB-BACKDOOR",
}


def now_ts() -> str:
    return _dt.datetime.now().strftime("%H:%M:%S")


def label_port(port: int) -> str:
    return PORT_LABELS.get(port, "")


def payload_snippet(pkt, max_bytes: int = 32) -> Optional[str]:
    try:
        raw = bytes(pkt[TCP].payload)
    except Exception:
        return None
    if not raw:
        return None
    snip = raw[:max_bytes]
    # Try text, otherwise hex
    try:
        txt = snip.decode("utf-8")
        txt = txt.replace("\r", "\\r").replace("\n", "\\n")
        return f"text:{txt}"
    except Exception:
        return f"hex:{binascii.hexlify(snip).decode()}"


def handle_packet(pkt) -> None:
    if IP not in pkt:
        return

    ip = pkt[IP]
    proto = "IP"
    src = ip.src
    dst = ip.dst

    sport = dport = None
    l4 = None

    if TCP in pkt:
        proto = "TCP"
        l4 = pkt[TCP]
        sport = int(l4.sport)
        dport = int(l4.dport)
    elif UDP in pkt:
        proto = "UDP"
        l4 = pkt[UDP]
        sport = int(l4.sport)
        dport = int(l4.dport)

    if sport is None or dport is None:
        print(f"[{now_ts()}] {proto} {src} -> {dst} len={len(pkt)}")
        return

    sp = f"{sport}"
    dp = f"{dport}"
    sl = label_port(sport)
    dl = label_port(dport)

    tags = []
    if sl:
        tags.append(sl)
    if dl and dl != sl:
        tags.append(dl)

    tag = f" ({', '.join(tags)})" if tags else ""

    extra = ""
    if proto == "TCP" and (sport == 1883 or dport == 1883):
        snip = payload_snippet(pkt)
        if snip:
            extra = f" | {snip}"

    print(f"[{now_ts()}] {proto} {src}:{sp} -> {dst}:{dp}{tag} len={len(pkt)}{extra}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Week 13 - Packet sniffer (educational)")
    parser.add_argument("--iface", default="any", help="Interface name (default: any)")
    parser.add_argument("--count", type=int, default=0, help="Number of packets to capture (0 = unlimited)")
    parser.add_argument("--timeout", type=int, default=20, help="Capture timeout in seconds (default: 20)")
    parser.add_argument(
        "--bpf",
        default="tcp port 1883 or tcp port 8883 or tcp port 80 or tcp port 21 or tcp port 6200",
        help="BPF filter (default targets Week 13 lab ports)",
    )
    parser.add_argument("--pcap-out", default=None, help="Optional PCAP output path")
    args = parser.parse_args()

    print("=" * 72)
    print("Week 13 - Packet sniffer (educational)")
    print("=" * 72)
    print(f"Interface: {args.iface}")
    print(f"Timeout: {args.timeout}s")
    print(f"Count: {args.count}")
    print(f"BPF: {args.bpf}")
    if args.pcap_out:
        print(f"PCAP output: {args.pcap_out}")
    print()

    packets = sniff(
        iface=args.iface,
        filter=args.bpf,
        prn=handle_packet,
        timeout=args.timeout,
        count=args.count if args.count > 0 else 0,
        store=bool(args.pcap_out),
    )

    if args.pcap_out:
        wrpcap(args.pcap_out, packets)
        print(f"\nPCAP written to: {args.pcap_out}")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
