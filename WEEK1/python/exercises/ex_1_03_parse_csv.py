#!/usr/bin/env python3
"""Exercise 1.03: Parsing a tshark-style CSV (Week 1)

In later weeks you may export packet metadata as CSV and analyse it quickly.
This script demonstrates a minimal analysis that is stable enough for automated
checks.

If no input is provided, a small built-in sample is analysed.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Iterable


SAMPLE_ROWS = [
    {"frame.number": "1", "ip.src": "10.0.1.11", "ip.dst": "10.0.1.12", "ip.proto": "1"},
    {"frame.number": "2", "ip.src": "10.0.1.11", "ip.dst": "10.0.1.12", "ip.proto": "1"},
    {"frame.number": "3", "ip.src": "10.0.1.12", "ip.dst": "10.0.1.11", "ip.proto": "6"},
]


def read_rows(path: Path | None) -> Iterable[dict[str, str]]:
    if path is None:
        return SAMPLE_ROWS
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        return list(r)


def main() -> int:
    ap = argparse.ArgumentParser(description="Parse a CSV with packet metadata and print basic counts.")
    ap.add_argument("--input", type=Path, default=None, help="Path to a CSV file exported from tshark.")
    args = ap.parse_args()

    rows = list(read_rows(args.input))
    if not rows:
        print("CSV rows=0")
        return 0

    proto_counts = Counter(row.get("ip.proto", "?") for row in rows)
    src_counts = Counter(row.get("ip.src", "?") for row in rows)

    print(f"CSV rows={len(rows)} protos={dict(proto_counts)} top_src={src_counts.most_common(1)[0][0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
