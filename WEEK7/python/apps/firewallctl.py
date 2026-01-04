"""Firewall rule helper for Week 7.

This tool applies small iptables rule profiles from `configs/firewall_profiles.json`.
It is intended for a lab router namespace created by Mininet.

Usage examples:
- sudo python3 python/apps/firewallctl.py --profile baseline
- sudo python3 python/apps/firewallctl.py --profile block_tcp_9090
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

# Add parent directory to path for utils import
import sys
_script_dir = Path(__file__).resolve().parent
_utils_dir = _script_dir.parent / "utils"
if str(_utils_dir.parent) not in sys.path:
    sys.path.insert(0, str(_utils_dir.parent))

from utils.net_utils import run_cmd, is_root


def build_parser() -> argparse.ArgumentParser:
    # Default config path relative to script location (WEEK7/python/apps/ -> WEEK7/configs/)
    default_config = str(Path(__file__).resolve().parent.parent.parent / "configs" / "firewall_profiles.json")
    p = argparse.ArgumentParser(description="Apply iptables profiles (Week 7).")
    p.add_argument("--profile", required=True, help="Profile name from configs/firewall_profiles.json")
    p.add_argument("--config", default=default_config, help="Path to profiles json")
    p.add_argument("--dry-run", action="store_true", help="Print commands but do not execute")
    return p


def iptables(argv: list[str], dry_run: bool) -> None:
    if dry_run:
        print("[dry-run]", " ".join(argv))
        return
    run_cmd(argv, timeout=10, check=True)


def main() -> int:
    args = build_parser().parse_args()
    if not is_root() and not args.dry_run:
        print("This tool needs root privileges, use sudo")
        return 2

    cfg_path = Path(args.config)
    data: dict[str, Any] = json.loads(cfg_path.read_text(encoding="utf-8"))
    if args.profile not in data:
        print(f"Unknown profile: {args.profile}")
        print(f"Available profiles: {', '.join(sorted(data.keys()))}")
        return 3

    profile = data[args.profile]
    rules = profile.get("rules", [])
    forward_policy = profile.get("forward_policy", "ACCEPT")

    # Clear FORWARD chain and set policy
    iptables(["iptables", "-F", "FORWARD"], args.dry_run)
    iptables(["iptables", "-P", "FORWARD", forward_policy], args.dry_run)

    # Apply rules in order
    for rule in rules:
        chain = rule.get("chain", "FORWARD")
        proto = rule.get("proto")
        action = rule.get("action", "ACCEPT")
        dport = rule.get("dport")
        argv = ["iptables", "-A", chain]
        if proto:
            argv += ["-p", str(proto)]
        if dport is not None:
            argv += ["--dport", str(dport)]
        argv += ["-j", str(action)]
        iptables(argv, args.dry_run)

    # Show resulting FORWARD rules for transparency
    if not args.dry_run:
        out = run_cmd(["iptables", "-L", "FORWARD", "-n", "-v"], timeout=10, check=False)
        print(out.stdout)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
