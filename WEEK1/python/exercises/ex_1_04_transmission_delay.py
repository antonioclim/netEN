#!/usr/bin/env python3
"""Exercise 1.04: Transmission delay calculator (Week 1)

Transmission delay is the time required to push all packet bits onto the link.

delay_seconds = (packet_size_bits) / (link_rate_bits_per_second)
"""

from __future__ import annotations

import argparse


def main() -> int:
    ap = argparse.ArgumentParser(description="Compute transmission delay for a packet on a link.")
    ap.add_argument("--size-bytes", type=int, default=1500, help="Packet size in bytes.")
    ap.add_argument("--rate-mbps", type=float, default=100.0, help="Link rate in megabits per second.")
    args = ap.parse_args()

    size_bits = args.size_bytes * 8
    rate_bps = args.rate_mbps * 1_000_000.0
    delay_s = size_bits / rate_bps
    delay_us = delay_s * 1_000_000.0

    print(f"TX_DELAY size_bytes={args.size_bytes} rate_mbps={args.rate_mbps} delay_us={delay_us:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
