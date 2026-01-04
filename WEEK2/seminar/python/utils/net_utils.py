"""Utilitare S2 for analiza rapida of capturi exportate from tshark.

in laborator, este util sa extragem rapid cateva campuri şi sa le agregam (ex. TCP flags, ports).

This module evita dependente externe (pandas etc.) for a run on VM minimala.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import Iterable, Iterator


@dataclass
class FlowKey:
    src: str
    sport: str
    dst: str
    dport: str


def read_tshark_csv(path: str) -> Iterator[dict[str, str]]:
    """Citeşte un CSV produs of tshark (-T fields ... -E header=y -E separator=, -E quote=d)."""
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            yield {k: (v or "").strip() for k, v in row.items()}


def summarize_tcp_flags(rows: Iterable[dict[str, str]], flag_field: str = "tcp.flags") -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        flags = row.get(flag_field, "")
        if not flags:
            continue
        counts[flags] = counts.get(flags, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def summarize_ports(rows: Iterable[dict[str, str]], proto: str = "tcp") -> dict[str, int]:
    key = f"{proto}.dstport"
    counts: dict[str, int] = {}
    for row in rows:
        p = row.get(key, "")
        if not p:
            continue
        counts[p] = counts.get(p, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))
