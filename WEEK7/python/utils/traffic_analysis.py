"""Small helper to create a reproducible summary from a pcap using tshark.

This script is intentionally conservative: if tshark is missing it will not fail the workflow.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from python.utils.net_utils import run_cmd


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Create a short tshark summary from a pcap file.")
    p.add_argument("--pcap", required=True, help="Path to pcap file")
    p.add_argument("--out", required=True, help="Output text file")
    return p


def main() -> int:
    args = build_parser().parse_args()
    pcap = Path(args.pcap)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    if not pcap.exists():
        out.write_text("pcap is missing, cannot analyse\n", encoding="utf-8")
        return 0

    if shutil.which("tshark") is None:
        out.write_text("tshark is not installed, skipping analysis\n", encoding="utf-8")
        return 0

    lines: list[str] = []
    lines.append(f"PCAP: {pcap}")
    lines.append("")

    # Conversation summaries
    tcp_conv = run_cmd(["tshark", "-r", str(pcap), "-q", "-z", "conv,tcp"], timeout=30)
    udp_conv = run_cmd(["tshark", "-r", str(pcap), "-q", "-z", "conv,udp"], timeout=30)

    lines.append("=== TCP conversations ===")
    lines.append(tcp_conv.stdout.strip() or "(no output)")
    lines.append("")
    lines.append("=== UDP conversations ===")
    lines.append(udp_conv.stdout.strip() or "(no output)")
    lines.append("")

    # Simple packet counts
    tcp_count = run_cmd(["bash", "-lc", f"tshark -r {pcap} -Y 'tcp.port==9090' | wc -l"], timeout=30)
    udp_count = run_cmd(["bash", "-lc", f"tshark -r {pcap} -Y 'udp.port==9091' | wc -l"], timeout=30)

    lines.append(f"Packets matching tcp.port==9090: {tcp_count.stdout.strip()}")
    lines.append(f"Packets matching udp.port==9091: {udp_count.stdout.strip()}")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
