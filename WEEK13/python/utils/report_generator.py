#!/usr/bin/env python3
"""Week 13 - Report generator (optional).

This utility reads artefacts produced by the kit and generates a small Markdown
summary report.

Inputs (best effort):
- artifacts/scan_results.json
- artifacts/validation.txt

Output:
- artifacts/report.md
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


ARTIFACTS_DIR = Path(__file__).resolve().parents[2] / "artifacts"
SCAN_JSON = ARTIFACTS_DIR / "scan_results.json"
VALIDATION_TXT = ARTIFACTS_DIR / "validation.txt"
REPORT_MD = ARTIFACTS_DIR / "report.md"


def load_scan() -> Optional[Dict[str, Any]]:
    if not SCAN_JSON.exists() or SCAN_JSON.stat().st_size == 0:
        return None
    js = json.loads(SCAN_JSON.read_text(encoding="utf-8"))
    return js.get("scan_report", js)


def load_validation() -> List[str]:
    if not VALIDATION_TXT.exists():
        return []
    return [line.strip() for line in VALIDATION_TXT.read_text(encoding="utf-8").splitlines() if line.strip()]


def summarise_scan(scan: Dict[str, Any]) -> str:
    hosts = scan.get("hosts", [])
    lines: List[str] = []
    for h in hosts:
        ip = h.get("ip") or h.get("host") or "unknown"
        ports = h.get("open_ports", [])
        ports_str = ", ".join(str(p) for p in ports) if ports else "(none)"
        lines.append(f"- **{ip}** open ports: {ports_str}")
    return "\n".join(lines) if lines else "_No hosts in scan output._"


def main() -> int:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    scan = load_scan()
    validation = load_validation()

    md: List[str] = []
    md.append("# Week 13 Lab Report")
    md.append("")
    md.append("## Validation")
    md.append("")
    if validation:
        md.extend([f"- {line}" for line in validation])
    else:
        md.append("_No validation file found._")

    md.append("")
    md.append("## Port scan summary")
    md.append("")
    if scan:
        md.append(summarise_scan(scan))
    else:
        md.append("_No scan_results.json found._")

    md.append("")
    md.append("## Notes")
    md.append("")
    md.append("This report is generated automatically from artefacts produced by the Week 13 kit.")

    REPORT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Report written to: {REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
