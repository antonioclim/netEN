#!/usr/bin/env python3
"""Week 10 - HTTPS and a minimal REST API.

This exercise provides a small HTTPS server implemented with the Python
standard library. The server exposes a JSON API to demonstrate:

- TLS termination (HTTPS)
- HTTP verbs and status codes
- Basic CRUD operations over a resource collection

Security note
-------------
A self-signed certificate is generated for local laboratory use. In a real
deployment you would use a certificate issued by a trusted CA and enforce
strict TLS validation on the client.
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8443
DEFAULT_CN = "lab.network.local"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TLS_DIR = PROJECT_ROOT / "output" / "tls"
DEFAULT_CERT = DEFAULT_TLS_DIR / "server.crt"
DEFAULT_KEY = DEFAULT_TLS_DIR / "server.key"


@dataclass
class Resource:
    id: int
    name: str
    value: Any


class ResourceStore:
    def __init__(self) -> None:
        self._items: Dict[int, Resource] = {}
        self._next_id = 1
        self._lock = threading.Lock()

    def list(self) -> list[dict[str, Any]]:
        with self._lock:
            return [self._to_dict(r) for r in self._items.values()]

    def create(self, name: str, value: Any) -> dict[str, Any]:
        with self._lock:
            rid = self._next_id
            self._next_id += 1
            res = Resource(id=rid, name=name, value=value)
            self._items[rid] = res
            return self._to_dict(res)

    def get(self, rid: int) -> Optional[dict[str, Any]]:
        with self._lock:
            res = self._items.get(rid)
            return None if res is None else self._to_dict(res)

    def update(self, rid: int, name: Optional[str], value: Any) -> Optional[dict[str, Any]]:
        with self._lock:
            res = self._items.get(rid)
            if res is None:
                return None
            if name is not None:
                res.name = name
            res.value = value
            return self._to_dict(res)

    def delete(self, rid: int) -> bool:
        with self._lock:
            return self._items.pop(rid, None) is not None

    @staticmethod
    def _to_dict(r: Resource) -> dict[str, Any]:
        return {"id": r.id, "name": r.name, "value": r.value}


STORE = ResourceStore()


class Handler(BaseHTTPRequestHandler):
    server_version = "ASE-Week10-HTTPS/1.0"

    def _send_json(self, status: int, payload: Any | None = None) -> None:
        body = b""
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _send_html(self, status: int, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> Tuple[Optional[dict[str, Any]], Optional[str]]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return None, "Missing JSON body"
        try:
            raw = self.rfile.read(length)
            data = json.loads(raw.decode("utf-8"))
            if not isinstance(data, dict):
                return None, "JSON body must be an object"
            return data, None
        except Exception as exc:
            return None, f"Invalid JSON: {exc}"

    def _route(self) -> Tuple[str, Optional[int]]:
        # Supported paths:
        #   /                    (HTML)
        #   /api/resources       (collection)
        #   /api/resources/<id>  (item)
        path = self.path.split("?", 1)[0]
        if path == "/":
            return "/", None
        if path == "/api/resources":
            return "/api/resources", None
        if path.startswith("/api/resources/"):
            try:
                rid = int(path.rsplit("/", 1)[1])
                return "/api/resources/:id", rid
            except ValueError:
                return "invalid", None
        return "unknown", None

    def do_GET(self) -> None:  # noqa: N802
        route, rid = self._route()
        if route == "/":
            self._send_html(
                200,
                """<!doctype html>
<html lang=\"en\">
<head><meta charset=\"utf-8\"><title>Week 10 - HTTPS REST API</title></head>
<body>
<h1>Week 10 - HTTPS REST API</h1>
<p>Available endpoints:</p>
<ul>
  <li><code>GET /api/resources</code></li>
  <li><code>POST /api/resources</code></li>
  <li><code>GET /api/resources/&lt;id&gt;</code></li>
  <li><code>PUT /api/resources/&lt;id&gt;</code></li>
  <li><code>DELETE /api/resources/&lt;id&gt;</code></li>
</ul>
</body></html>""",
            )
            return

        if route == "/api/resources":
            self._send_json(200, {"resources": STORE.list()})
            return

        if route == "/api/resources/:id" and rid is not None:
            item = STORE.get(rid)
            if item is None:
                self._send_json(404, {"error": "Resource not found"})
            else:
                self._send_json(200, item)
            return

        if route == "invalid":
            self._send_json(400, {"error": "Invalid resource id"})
            return

        self._send_json(404, {"error": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        route, _ = self._route()
        if route != "/api/resources":
            self._send_json(404, {"error": "Not found"})
            return

        data, err = self._read_json()
        if err is not None or data is None:
            self._send_json(400, {"error": err})
            return

        name = str(data.get("name", "")).strip()
        if not name:
            self._send_json(400, {"error": "Field 'name' is required"})
            return

        value = data.get("value")
        created = STORE.create(name=name, value=value)
        self._send_json(201, created)

    def do_PUT(self) -> None:  # noqa: N802
        route, rid = self._route()
        if route != "/api/resources/:id" or rid is None:
            self._send_json(404, {"error": "Not found"})
            return

        data, err = self._read_json()
        if err is not None or data is None:
            self._send_json(400, {"error": err})
            return

        name = data.get("name")
        if name is not None:
            name = str(name).strip()
            if not name:
                self._send_json(400, {"error": "Field 'name' must not be empty"})
                return

        value = data.get("value")
        updated = STORE.update(rid=rid, name=name, value=value)
        if updated is None:
            self._send_json(404, {"error": "Resource not found"})
            return
        self._send_json(200, updated)

    def do_DELETE(self) -> None:  # noqa: N802
        route, rid = self._route()
        if route != "/api/resources/:id" or rid is None:
            self._send_json(404, {"error": "Not found"})
            return

        if not STORE.delete(rid):
            self._send_json(404, {"error": "Resource not found"})
            return
        self._send_json(204, None)

    def log_message(self, fmt: str, *args: Any) -> None:
        # Keep logs concise.
        sys.stderr.write("[HTTP] %s - %s\n" % (self.address_string(), fmt % args))


def generate_self_signed_certificate(cert_path: Path, key_path: Path, common_name: str) -> None:
    cert_path.parent.mkdir(parents=True, exist_ok=True)

    if cert_path.exists() and key_path.exists():
        return

    openssl = "openssl"
    cmd = [
        openssl,
        "req",
        "-x509",
        "-newkey",
        "rsa:2048",
        "-nodes",
        "-keyout",
        str(key_path),
        "-out",
        str(cert_path),
        "-days",
        "365",
        "-subj",
        f"/C=RO/O=ASE-CSIE/OU=Computer Networks/CN={common_name}",
        "-addext",
        f"subjectAltName=DNS:{common_name},IP:127.0.0.1",
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        raise SystemExit("OpenSSL is required to generate the self-signed certificate")
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"OpenSSL failed to generate a certificate: {exc}")


def build_server(host: str, port: int, cert: Path, key: Path) -> ThreadingHTTPServer:
    httpd = ThreadingHTTPServer((host, port), Handler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=str(cert), keyfile=str(key))
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    return httpd


def serve(host: str, port: int, cert: Path, key: Path, common_name: str) -> None:
    generate_self_signed_certificate(cert, key, common_name)
    httpd = build_server(host, port, cert, key)

    print("[INFO] HTTPS server ready")
    print(f"[INFO] URL: https://{host}:{httpd.server_address[1]}/")
    print(f"[INFO] Certificate: {cert}")
    print("[INFO] Press Ctrl+C to stop")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        print("[INFO] Server stopped")


def selftest() -> int:
    try:
        import requests  # type: ignore
        import urllib3

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except Exception as exc:
        print(f"[ERROR] requests is required for selftest: {exc}")
        return 1

    cert = DEFAULT_CERT
    key = DEFAULT_KEY
    generate_self_signed_certificate(cert, key, DEFAULT_CN)

    server = build_server(DEFAULT_HOST, 0, cert, key)
    actual_port = server.server_address[1]

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    base = f"https://{DEFAULT_HOST}:{actual_port}"

    try:
        # Create
        r = requests.post(
            f"{base}/api/resources",
            json={"name": "example", "value": 123},
            timeout=5,
            verify=False,
        )
        assert r.status_code == HTTPStatus.CREATED, r.text
        created = r.json()
        rid = int(created["id"])

        # List
        r = requests.get(f"{base}/api/resources", timeout=5, verify=False)
        assert r.status_code == HTTPStatus.OK, r.text
        data = r.json()
        assert any(x["id"] == rid for x in data["resources"])

        # Update
        r = requests.put(
            f"{base}/api/resources/{rid}",
            json={"name": "example-updated", "value": 456},
            timeout=5,
            verify=False,
        )
        assert r.status_code == HTTPStatus.OK, r.text
        assert r.json()["name"] == "example-updated"

        # Delete
        r = requests.delete(f"{base}/api/resources/{rid}", timeout=5, verify=False)
        assert r.status_code == HTTPStatus.NO_CONTENT

        print("[OK] HTTPS selftest passed")
        return 0
    except AssertionError as exc:
        print(f"[ERROR] HTTPS selftest failed: {exc}")
        return 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Week 10 HTTPS REST API")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_serve = sub.add_parser("serve", help="Start the HTTPS server")
    p_serve.add_argument("--host", default=DEFAULT_HOST)
    p_serve.add_argument("--port", type=int, default=DEFAULT_PORT)
    p_serve.add_argument("--cert", default=str(DEFAULT_CERT))
    p_serve.add_argument("--key", default=str(DEFAULT_KEY))
    p_serve.add_argument("--cn", default=DEFAULT_CN, help="Certificate common name")

    p_cert = sub.add_parser("generate-cert", help="Generate a self-signed TLS certificate")
    p_cert.add_argument("--cert", default=str(DEFAULT_CERT))
    p_cert.add_argument("--key", default=str(DEFAULT_KEY))
    p_cert.add_argument("--cn", default=DEFAULT_CN)

    sub.add_parser("selftest", help="Run a local selftest")

    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    if args.cmd == "generate-cert":
        cert = Path(args.cert)
        key = Path(args.key)
        generate_self_signed_certificate(cert, key, args.cn)
        print(f"[OK] Certificate generated: {cert}")
        print(f"[OK] Key generated: {key}")
        return 0

    if args.cmd == "serve":
        serve(args.host, args.port, Path(args.cert), Path(args.key), args.cn)
        return 0

    if args.cmd == "selftest":
        return selftest()

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
