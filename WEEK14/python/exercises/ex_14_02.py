#!/usr/bin/env python3
"""ex_14_02.py — Verification harness for the team project.

Features:
  - Verifies connectivity (ping)
  - Verifies open TCP ports
  - Verifies HTTP endpoints
  - Generates JSON report

Usage:
  python3 ex_14_02.py --config project_config.json --out report.json
"""

from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


def log(msg: str) -> None:
    """Logging with timestamp."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [harness] {msg}")


def check_ping(host: str, timeout: int = 2) -> Dict[str, Any]:
    """Verifies ICMP connectivity."""
    result = {
        "type": "ping",
        "host": host,
        "success": False,
        "latency_ms": None,
        "error": None,
    }
    
    try:
        cmd = ["ping", "-c", "1", "-W", str(timeout), host]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 1)
        
        if proc.returncode == 0:
            result["success"] = True
            # Parse latency from output
            for line in proc.stdout.split("\n"):
                if "time=" in line:
                    import re
                    match = re.search(r"time=(\d+\.?\d*)", line)
                    if match:
                        result["latency_ms"] = float(match.group(1))
                        break
        else:
            result["error"] = "ping failed"
    except subprocess.TimeoutExpired:
        result["error"] = "timeout"
    except Exception as e:
        result["error"] = str(e)
    
    return result


def check_tcp_port(host: str, port: int, timeout: int = 3) -> Dict[str, Any]:
    """Verifies if a TCP port is open."""
    result = {
        "type": "tcp",
        "host": host,
        "port": port,
        "success": False,
        "connect_time_ms": None,
        "error": None,
    }
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    
    try:
        start = time.time()
        sock.connect((host, port))
        result["success"] = True
        result["connect_time_ms"] = round((time.time() - start) * 1000, 2)
    except socket.timeout:
        result["error"] = "timeout"
    except ConnectionRefusedError:
        result["error"] = "connection refused"
    except OSError as e:
        result["error"] = str(e)
    finally:
        sock.close()
    
    return result


def check_http(url: str, expected_status: int = 200, timeout: int = 5) -> Dict[str, Any]:
    """Verifies an HTTP endpoint."""
    result = {
        "type": "http",
        "url": url,
        "success": False,
        "status": None,
        "latency_ms": None,
        "error": None,
    }
    
    try:
        req = Request(url, method="GET")
        start = time.time()
        
        with urlopen(req, timeout=timeout) as response:
            result["status"] = response.status
            result["latency_ms"] = round((time.time() - start) * 1000, 2)
            result["success"] = (response.status == expected_status)
    
    except HTTPError as e:
        result["status"] = e.code
        result["success"] = (e.code == expected_status)
    except URLError as e:
        result["error"] = str(e.reason)
    except Exception as e:
        result["error"] = str(e)
    
    return result


def run_checks(config: Dict) -> Dict[str, Any]:
    """Runs all checks from configuration."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "config_name": config.get("project_name", "unknown"),
        "targets": [],
        "summary": {
            "total_checks": 0,
            "passed": 0,
            "failed": 0,
        },
    }
    
    timeouts = config.get("timeouts", {})
    default_ping_timeout = timeouts.get("ping", 2)
    default_tcp_timeout = timeouts.get("tcp", 3)
    default_http_timeout = timeouts.get("http", 5)
    
    for target in config.get("targets", []):
        target_name = target.get("name", "unknown")
        target_host = target.get("host", "127.0.0.1")
        
        log(f"Checking target: {target_name} ({target_host})")
        
        target_result = {
            "name": target_name,
            "host": target_host,
            "checks": [],
        }
        
        for check in target.get("checks", []):
            check_type = check.get("type")
            
            if check_type == "ping":
                timeout = check.get("timeout", default_ping_timeout)
                result = check_ping(target_host, timeout)
            
            elif check_type == "tcp":
                port = check.get("port", 80)
                timeout = check.get("timeout", default_tcp_timeout)
                result = check_tcp_port(target_host, port, timeout)
            
            elif check_type == "http":
                url = check.get("url", f"http://{target_host}/")
                expected = check.get("expected_status", 200)
                timeout = check.get("timeout", default_http_timeout)
                result = check_http(url, expected, timeout)
            
            else:
                result = {
                    "type": check_type,
                    "success": False,
                    "error": f"unknown check type: {check_type}",
                }
            
            target_result["checks"].append(result)
            report["summary"]["total_checks"] += 1
            
            if result.get("success"):
                report["summary"]["passed"] += 1
                status = "✓"
            else:
                report["summary"]["failed"] += 1
                status = "✗"
            
            log(f"  {status} {check_type}: {result.get('error') or 'OK'}")
        
        report["targets"].append(target_result)
    
    return report


def load_config(path: str) -> Dict:
    """Loads configuration from JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Project verification harness W14")
    parser.add_argument("--config", required=True, help="JSON configuration file")
    parser.add_argument("--out", help="Output file for JSON report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Detailed output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    
    log(f"Loading configuration: {args.config}")
    config = load_config(args.config)
    
    log("Starting verification...")
    report = run_checks(config)
    
    # Summary
    summary = report["summary"]
    total = summary["total_checks"]
    passed = summary["passed"]
    failed = summary["failed"]
    
    print("\n" + "=" * 50)
    print(f"  Verification complete: {passed}/{total} passed")
    print("=" * 50)
    
    # Output
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        log(f"Report saved to: {args.out}")
    elif args.verbose:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
