#!/usr/bin/env python3
"""Exercise 1.01: Measuring latency with ping (Week 1)

This script runs a small ping sample and extracts the average RTT when available.
It is designed to be safe on CLI-only minimal VMs.

Examples
--------
python3 python/exercises/ex_1_01_ping_latency.py --host 127.0.0.1 --count 3
"""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class PingResult:
    host: str
    transmitted: int
    received: int
    avg_rtt_ms: float | None


def run_ping(host: str, count: int, timeout_s: int) -> str:
    cmd = ["ping", "-n", "-c", str(count), "-W", str(timeout_s), host]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc.stdout + proc.stderr


def parse_ping(output: str, host: str, count: int) -> PingResult:
    transmitted = count
    received = 0
    avg = None

    m = re.search(r"(\d+) packets transmitted, (\d+) received", output)
    if m:
        transmitted = int(m.group(1))
        received = int(m.group(2))

    m = re.search(r"rtt min/avg/max/mdev = [^/]+/([^/]+)/", output)
    if m:
        try:
            avg = float(m.group(1))
        except ValueError:
            avg = None

    return PingResult(host=host, transmitted=transmitted, received=received, avg_rtt_ms=avg)


def main() -> int:
    ap = argparse.ArgumentParser(description="Run ping and report basic latency statistics.")
    ap.add_argument("--host", default="127.0.0.1", help="Target host or IP address.")
    ap.add_argument("--count", type=int, default=2, help="Number of ICMP echo requests.")
    ap.add_argument("--timeout-s", type=int, default=1, help="Per-packet timeout in seconds.")
    args = ap.parse_args()

    out = run_ping(args.host, args.count, args.timeout_s)
    res = parse_ping(out, args.host, args.count)

    avg_txt = f"{res.avg_rtt_ms:.3f} ms" if res.avg_rtt_ms is not None else "n/a"
    print(f"PING host={res.host} tx={res.transmitted} rx={res.received} avg_rtt={avg_txt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
