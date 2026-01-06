#!/usr/bin/env python3
"""Week 13 - Vulnerability checker (defensive and educational).

This script performs light-weight, defensive checks:
- service reachability
- basic fingerprinting (banners and HTTP headers)
- identification of *intentionally vulnerable* lab services (eg DVWA)

It does NOT exploit vulnerabilities and it does NOT attempt privilege escalation.

Supported services:
- http   (simple GET /, header inspection and basic DVWA fingerprint)
- ftp    (banner inspection)
- mqtt   (broker reachability via TCP connect only)

Exit codes:
  0 - checks completed and a report was produced
  1 - operational failure (connection error or invalid arguments)
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Optional, Tuple


@dataclass
class Finding:
    title: str
    severity: str  # informational, low, medium, high
    evidence: str


@dataclass
class Report:
    target: str
    port: int
    service: str
    timestamp_utc: str
    reachable: bool
    banner: Optional[str]
    http_headers: Optional[Dict[str, str]]
    findings: list[Finding]


def tcp_banner(host: str, port: int, timeout: float = 2.0) -> Optional[str]:
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.settimeout(timeout)
            # Stimulus for some services
            try:
                s.sendall(b"\r\n")
            except Exception:
                pass
            data = s.recv(1024)
        text = data.decode(errors="replace").strip()
        return text or None
    except Exception:
        return None


def http_probe(host: str, port: int, timeout: float = 3.0) -> Tuple[bool, Optional[str], Dict[str, str], Optional[str]]:
    """Return (reachable, status_line, headers, body_snippet)."""
    req = (
        f"GET / HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: week13-vuln-checker\r\n"
        f"Connection: close\r\n\r\n"
    ).encode()

    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.sendall(req)
            s.settimeout(timeout)
            raw = b""
            while len(raw) < 65536:
                chunk = s.recv(4096)
                if not chunk:
                    break
                raw += chunk
    except Exception:
        return False, None, {}, None

    text = raw.decode(errors="replace")
    head, _, body = text.partition("\r\n\r\n")
    lines = head.split("\r\n")
    status_line = lines[0].strip() if lines else None

    headers: Dict[str, str] = {}
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip()] = v.strip()

    snippet = body[:500].strip() or None
    return True, status_line, headers, snippet


def main() -> int:
    parser = argparse.ArgumentParser(description="Week 13 - Vulnerability checker (defensive)")
    parser.add_argument("--target", required=True, help="Target host, eg 127.0.0.1")
    parser.add_argument("--port", type=int, required=True, help="Target port")
    parser.add_argument("--service", choices=["http", "ftp", "mqtt"], required=True, help="Service type")
    parser.add_argument("--json-out", default=None, help="Optional JSON output path")
    args = parser.parse_args()

    findings: list[Finding] = []
    banner = None
    headers: Optional[Dict[str, str]] = None
    reachable = False

    if args.service == "http":
        reachable, status_line, http_headers, body_snippet = http_probe(args.target, args.port)
        headers = http_headers
        banner = status_line

        if reachable:
            server = http_headers.get("Server")
            if server:
                findings.append(Finding(
                    title="HTTP Server header observed",
                    severity="informational",
                    evidence=f"Server: {server}",
                ))

            # DVWA fingerprint (best effort)
            if body_snippet and "Damn Vulnerable Web Application" in body_snippet:
                findings.append(Finding(
                    title="DVWA detected (intentionally vulnerable lab target)",
                    severity="informational",
                    evidence="Page contains 'Damn Vulnerable Web Application'",
                ))
            elif body_snippet and "DVWA" in body_snippet:
                findings.append(Finding(
                    title="Possible DVWA instance detected (heuristic)",
                    severity="low",
                    evidence="Body snippet contains 'DVWA'",
                ))
        else:
            findings.append(Finding(
                title="HTTP service not reachable",
                severity="high",
                evidence=f"Could not connect to {args.target}:{args.port}",
            ))

    elif args.service == "ftp":
        banner = tcp_banner(args.target, args.port)
        reachable = banner is not None
        if reachable and banner:
            findings.append(Finding(
                title="FTP banner observed",
                severity="informational",
                evidence=banner,
            ))
            if "vsftpd" in banner.lower() and "2.3.4" in banner:
                findings.append(Finding(
                    title="vsftpd 2.3.4 detected",
                    severity="high",
                    evidence="This version is associated with CVE-2011-2523 in some distributions.",
                ))
        else:
            findings.append(Finding(
                title="FTP service not reachable or no banner received",
                severity="medium",
                evidence=f"Could not read banner from {args.target}:{args.port}",
            ))

    elif args.service == "mqtt":
        # Defensive reachability check only: TCP connect
        try:
            with socket.create_connection((args.target, args.port), timeout=2.0):
                reachable = True
        except Exception:
            reachable = False

        if reachable:
            findings.append(Finding(
                title="MQTT broker reachable (TCP connect)",
                severity="informational",
                evidence=f"Connected to {args.target}:{args.port}",
            ))
        else:
            findings.append(Finding(
                title="MQTT broker not reachable",
                severity="high",
                evidence=f"Could not connect to {args.target}:{args.port}",
            ))

    report = Report(
        target=args.target,
        port=args.port,
        service=args.service,
        timestamp_utc=datetime.utcnow().isoformat(timespec="seconds") + "Z",
        reachable=reachable,
        banner=banner,
        http_headers=headers,
        findings=findings,
    )

    # Human-readable output
    print("=" * 72)
    print("Week 13 - Vulnerability checker (defensive)")
    print("=" * 72)
    print(f"Target:  {report.target}")
    print(f"Service: {report.service}")
    print(f"Port:    {report.port}")
    print(f"Reachable: {report.reachable}")
    if report.banner:
        print(f"Banner/status: {report.banner}")
    if report.http_headers:
        print("\nHTTP headers:")
        for k, v in report.http_headers.items():
            print(f"  {k}: {v}")
    print("\nFindings:")
    if not report.findings:
        print("  (none)")
    else:
        for f in report.findings:
            print(f"  - [{f.severity}] {f.title}")
            print(f"    Evidence: {f.evidence}")

    if args.json_out:
        out = asdict(report)
        out["findings"] = [asdict(x) for x in report.findings]
        with open(args.json_out, "w", encoding="utf-8") as fp:
            json.dump(out, fp, indent=2)
        print(f"\nJSON report written to: {args.json_out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
