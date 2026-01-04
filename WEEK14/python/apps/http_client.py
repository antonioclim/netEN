#!/usr/bin/env python3
"""http_client.py — HTTP client with logging for load balancer testing.

Features:
  - Sends multiple requests to a URL
  - Records latency, status, backend (from X-Backend header)
  - Generates summary at the end

Usage:
  python3 http_client.py --url http://10.0.0.10:8080/ --count 20 --interval 0.1
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


def make_request(url: str, timeout: float = 5.0) -> Dict:
    """Makes an HTTP request and returns the result."""
    start = time.time()
    result = {
        "timestamp": datetime.now().isoformat(),
        "url": url,
        "status": None,
        "backend": None,
        "latency_ms": None,
        "error": None,
    }
    
    try:
        req = Request(url, method="GET")
        with urlopen(req, timeout=timeout) as response:
            result["status"] = response.status
            result["backend"] = response.getheader("X-Backend", "-")
            _ = response.read()  # consume body
    except HTTPError as e:
        result["status"] = e.code
        result["backend"] = e.headers.get("X-Backend", "-")
    except URLError as e:
        result["error"] = str(e.reason)
    except Exception as e:
        result["error"] = str(e)
    
    result["latency_ms"] = round((time.time() - start) * 1000, 2)
    return result


def format_log_line(idx: int, result: Dict) -> str:
    """Formats a log line."""
    status = result["status"] if result["status"] else "ERR"
    backend = result["backend"] if result["backend"] else "-"
    latency = result["latency_ms"] if result["latency_ms"] else 0
    error = result["error"] if result["error"] else ""
    
    line = f"{idx:03d} status={status} backend={backend} latency_ms={latency:.2f}"
    if error:
        line += f" error={error}"
    return line


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="HTTP client for LB testing")
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument("--count", type=int, default=10, help="Number of requests")
    parser.add_argument("--interval", type=float, default=0.1, help="Interval between requests (s)")
    parser.add_argument("--timeout", type=float, default=5.0, help="Timeout per request (s)")
    parser.add_argument("--out", default=None, help="Log file (default: stdout)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    
    results: List[Dict] = []
    log_file = open(args.out, "w", encoding="utf-8") if args.out else sys.stdout
    
    try:
        for i in range(args.count):
            result = make_request(args.url, timeout=args.timeout)
            results.append(result)
            
            line = format_log_line(i, result)
            print(line, file=log_file)
            log_file.flush()
            
            if i < args.count - 1:
                time.sleep(args.interval)
    
    finally:
        if args.out:
            log_file.close()
    
    # Generate summary
    total = len(results)
    ok = sum(1 for r in results if r["status"] and 200 <= r["status"] < 300)
    errors = sum(1 for r in results if r["error"])
    
    backend_dist: Dict[str, int] = {}
    latencies: List[float] = []
    for r in results:
        if r["backend"]:
            backend_dist[r["backend"]] = backend_dist.get(r["backend"], 0) + 1
        if r["latency_ms"]:
            latencies.append(r["latency_ms"])
    
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    
    summary = {
        "total": total,
        "ok": ok,
        "errors": errors,
        "avg_latency_ms": round(avg_latency, 2),
        "backend_distribution": backend_dist,
    }
    
    # Write summary to stdout/stderr (separate from log)
    print(f"--- Summary ---", file=sys.stdout)
    print(f"Total: {total}, Success: {ok}, Errors: {errors}", file=sys.stdout)
    print(f"Average latency: {avg_latency:.2f} ms", file=sys.stdout)
    print(f"Backend distribution: {backend_dist}", file=sys.stdout)
    
    # JSON summary to stderr (for automated parsing)
    print(json.dumps(summary), file=sys.stderr)
    
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
