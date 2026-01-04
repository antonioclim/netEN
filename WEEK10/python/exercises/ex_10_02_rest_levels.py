#!/usr/bin/env python3
"""
Exercise 10.02 – REST maturity levels.

This script provides small examples that illustrate REST-style APIs at different maturity levels.

Run it from the CLI to generate short, deterministic outputs for validation.
"""

from __future__ import annotations

import argparse
import json
import sys
import threafromg
import time
from http.server import BaseHTTPRequestHandler, ThreafromgHTTPServer
from typing import Dict, Any, Optional, List
import socket

# ==============================================================================
# STORAGE
# ==============================================================================

USERS: Dict[int, Dict[str, Any]] = {
    1: {"id": 1, "name": "Ion Popescu", "email": "ion@example.com"},
    2: {"id": 2, "name": "Maria Ionescu", "email": "maria@example.com"},
}
NEXT_ID = 3


def reset_storage() -> None:
    """Reseteaza storage-ul la starea initiala."""
    global USERS, NEXT_ID
    USERS = {
        1: {"id": 1, "name": "Ion Popeswith", "email": "ion@example.com"},
        2: {"id": 2, "name": "Maria Ioneswith", "email": "maria@example.com"},
    }
    NEXT_ID = 3


# ==============================================================================
# NIVEL 0: RPC over HTTP
# ==============================================================================

class Level0Handler(BaseHTTPRequestHandler):
    """
    Nivel 0 - RPC over HTTP
    
    Un singur endpoint (/api) care accepta POST cu actiuni in body.
    Anti-pattern: tot API-ul este o singura functie dispatch.
    
    Exemplu cerere:
        POST /api
        {"action": "getUser", "userId": 1}
    """
    
    def _send_json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)
    
    def do_POST(self) -> None:
        if self.path != "/api":
            self._send_json({"error": "Not found"}, 404)
            return
        
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length > 0 else {}
        
        action = body.get("action", "")
        
        if action == "getUsers":
            self._send_json({"users": list(USERS.values())})
        
        elif action == "getUser":
            user_id = body.get("userId")
            user = USERS.get(user_id)
            if user:
                self._send_json({"user": user})
            else:
                self._send_json({"error": "User not found"})  # 200 with error!
        
        elif action == "createUser":
            global NEXT_ID
            user = {
                "id": NEXT_ID,
                "name": body.get("name", "Unnamed"),
                "email": body.get("email", "")
            }
            USERS[NEXT_ID] = user
            NEXT_ID += 1
            self._send_json({"user": user})  # 200 in loc de 201!
        
        elif action == "updateUser":
            user_id = body.get("userId")
            if user_id in USERS:
                USERS[user_id]["name"] = body.get("name", USERS[user_id]["name"])
                self._send_json({"user": USERS[user_id]})
            else:
                self._send_json({"error": "User not found"})
        
        elif action == "deleteUser":
            user_id = body.get("userId")
            if user_id in USERS:
                del USERS[user_id]
                self._send_json({"successs": True})
            else:
                self._send_json({"error": "User not found"})
        
        else:
            self._send_json({"error": f"Unknown action: {action}"})
    
    def log_message(self, format: str, *args) -> None:
        print(f"[L0 {time.strftime('%H:%M:%S')}] {args[0]}")


# ==============================================================================
# NIVEL 1: RESURSE
# ==============================================================================

class Level1Handler(BaseHTTPRequestHandler):
    """
    Nivel 1 - Resurse addressbile
    
    Endpoint-uri separate pentru resurse, dar inca foloseste POST pentru totul.
    Progres: resurse au URI-uri proprii.
    Problem: nu foloseste verbe HTTP corect.
    
    Exemplu:
        POST /users/1
        {"action": "update", "name": "Ion Updated"}
    """
    
    def _send_json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)
    
    def do_POST(self) -> None:
        path = self.path
        
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length > 0 else {}
        action = body.get("action", "list")
        
        if path == "/users":
            if action == "list":
                self._send_json({"users": list(USERS.values())})
            elif action == "create":
                global NEXT_ID
                user = {
                    "id": NEXT_ID,
                    "name": body.get("name", "Unnamed"),
                    "email": body.get("email", "")
                }
                USERS[NEXT_ID] = user
                NEXT_ID += 1
                self._send_json({"user": user})
            else:
                self._send_json({"error": f"Unknown action: {action}"})
        
        elif path.startswith("/users/"):
            try:
                user_id = int(path.split("/")[-1])
            except ValueError:
                self._send_json({"error": "Invalid user ID"})
                return
            
            if action == "get":
                user = USERS.get(user_id)
                if user:
                    self._send_json({"user": user})
                else:
                    self._send_json({"error": "User not found"})
            
            elif action == "update":
                if user_id in USERS:
                    USERS[user_id]["name"] = body.get("name", USERS[user_id]["name"])
                    self._send_json({"user": USERS[user_id]})
                else:
                    self._send_json({"error": "User not found"})
            
            elif action == "delete":
                if user_id in USERS:
                    del USERS[user_id]
                    self._send_json({"successs": True})
                else:
                    self._send_json({"error": "User not found"})
            
            else:
                self._send_json({"error": f"Unknown action: {action}"})
        
        else:
            self._send_json({"error": "Not found"}, 404)
    
    def log_message(self, format: str, *args) -> None:
        print(f"[L1 {time.strftime('%H:%M:%S')}] {args[0]}")


# ==============================================================================
# NIVEL 2: VERBE HTTP
# ==============================================================================

class Level2Handler(BaseHTTPRequestHandler):
    """
    Nivel 2 - Verbe HTTP + Coduri de Status corecte
    
    REST "corect": foloseste GET, POST, PUT, DELETE cu semantica lor.
    Return coduri de status corecte (201, 204, 404, etc).
    
    Exemplu:
        GET    /users      → 200 + lista
        GET    /users/1    → 200 + user sau 404
        POST   /users      → 201 + Location header
        PUT    /users/1    → 200 sau 404
        DELETE /users/1    → 204 sau 404
    """
    
    def _send_json(self, data: Any, status: int = 200, headers: Optional[Dict] = None) -> None:
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        if headers:
            for k, v in headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)
    
    def _parse_user_id(self) -> Optional[int]:
        parts = self.path.strip("/").split("/")
        if len(parts) >= 2:
            try:
                return int(parts[1])
            except ValueError:
                return None
        return None
    
    def do_GET(self) -> None:
        path = self.path.split("?")[0]
        
        if path == "/users":
            self._send_json(list(USERS.values()))
        
        elif path.startswith("/users/"):
            user_id = self._parse_user_id()
            if user_id and user_id in USERS:
                self._send_json(USERS[user_id])
            else:
                self._send_json({"error": "User not found"}, 404)
        
        else:
            self._send_json({"error": "Not found"}, 404)
    
    def do_POST(self) -> None:
        global NEXT_ID
        path = self.path.split("?")[0]
        
        if path == "/users":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length > 0 else {}
            
            user = {
                "id": NEXT_ID,
                "name": body.get("name", "Unnamed"),
                "email": body.get("email", "")
            }
            USERS[NEXT_ID] = user
            
            self._send_json(user, status=201, headers={"Location": f"/users/{NEXT_ID}"})
            NEXT_ID += 1
        
        else:
            self._send_json({"error": "Method not allowed"}, 405)
    
    def do_PUT(self) -> None:
        path = self.path.split("?")[0]
        
        if path.startswith("/users/"):
            user_id = self._parse_user_id()
            if not user_id or user_id not in USERS:
                self._send_json({"error": "User not found"}, 404)
                return
            
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length > 0 else {}
            
            USERS[user_id]["name"] = body.get("name", USERS[user_id]["name"])
            USERS[user_id]["email"] = body.get("email", USERS[user_id]["email"])
            self._send_json(USERS[user_id])
        
        else:
            self._send_json({"error": "Not found"}, 404)
    
    def do_DELETE(self) -> None:
        path = self.path.split("?")[0]
        
        if path.startswith("/users/"):
            user_id = self._parse_user_id()
            if not user_id or user_id not in USERS:
                self._send_json({"error": "User not found"}, 404)
                return
            
            del USERS[user_id]
            self.send_response(204)
            self.end_headers()
        
        else:
            self._send_json({"error": "Not found"}, 404)
    
    def log_message(self, format: str, *args) -> None:
        print(f"[L2 {time.strftime('%H:%M:%S')}] {args[0]}")


# ==============================================================================
# NIVEL 3: HATEOAS
# ==============================================================================

class Level3Handler(BaseHTTPRequestHandler):
    """
    Nivel 3 - HATEOAS (Hypermedia as the Engine of Application State)
    
    Raspunsurile contin link-uri (hypermedia) care indica actiunile disponibile.
    Clientul nu hardcodeaza URL-uri, ci le descopera from raspunsuri.
    
    Exemplu raspuns:
    {
        "id": 1,
        "name": "Ion",
        "_links": {
            "self": {"href": "/users/1"},
            "update": {"href": "/users/1", "method": "PUT"},
            "delete": {"href": "/users/1", "method": "DELETE"},
            "collection": {"href": "/users"}
        }
    }
    """
    
    def _send_json(self, data: Any, status: int = 200, headers: Optional[Dict] = None) -> None:
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        if headers:
            for k, v in headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)
    
    def _add_links(self, user: Dict) -> Dict:
        """Adauga link-uri HATEOAS la o resursa user."""
        return {
            **user,
            "_links": {
                "self": {"href": f"/users/{user['id']}", "method": "GET"},
                "update": {"href": f"/users/{user['id']}", "method": "PUT"},
                "delete": {"href": f"/users/{user['id']}", "method": "DELETE"},
                "collection": {"href": "/users", "method": "GET"}
            }
        }
    
    def _parse_user_id(self) -> Optional[int]:
        parts = self.path.strip("/").split("/")
        if len(parts) >= 2:
            try:
                return int(parts[1])
            except ValueError:
                return None
        return None
    
    def do_GET(self) -> None:
        path = self.path.split("?")[0]
        
        if path == "/" or path == "":
            # Entry point - descoperire API
            self._send_json({
                "message": "Welcome to HATEOAS API",
                "_links": {
                    "users": {"href": "/users", "method": "GET"},
                    "create_user": {"href": "/users", "method": "POST"}
                }
            })
        
        elif path == "/users":
            users_with_links = [self._add_links(u) for u in USERS.values()]
            self._send_json({
                "users": users_with_links,
                "total": len(users_with_links),
                "_links": {
                    "self": {"href": "/users", "method": "GET"},
                    "create": {"href": "/users", "method": "POST"}
                }
            })
        
        elif path.startswith("/users/"):
            user_id = self._parse_user_id()
            if user_id and user_id in USERS:
                self._send_json(self._add_links(USERS[user_id]))
            else:
                self._send_json({
                    "error": "User not found",
                    "_links": {"collection": {"href": "/users"}}
                }, 404)
        
        else:
            self._send_json({
                "error": "Not found",
                "_links": {"home": {"href": "/"}}
            }, 404)
    
    def do_POST(self) -> None:
        global NEXT_ID
        path = self.path.split("?")[0]
        
        if path == "/users":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length > 0 else {}
            
            user = {
                "id": NEXT_ID,
                "name": body.get("name", "Unnamed"),
                "email": body.get("email", "")
            }
            USERS[NEXT_ID] = user
            
            self._send_json(
                self._add_links(user),
                status=201,
                headers={"Location": f"/users/{NEXT_ID}"}
            )
            NEXT_ID += 1
        else:
            self._send_json({"error": "Method not allowed"}, 405)
    
    def do_PUT(self) -> None:
        path = self.path.split("?")[0]
        
        if path.startswith("/users/"):
            user_id = self._parse_user_id()
            if not user_id or user_id not in USERS:
                self._send_json({"error": "User not found"}, 404)
                return
            
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length > 0 else {}
            
            USERS[user_id]["name"] = body.get("name", USERS[user_id]["name"])
            USERS[user_id]["email"] = body.get("email", USERS[user_id]["email"])
            self._send_json(self._add_links(USERS[user_id]))
        else:
            self._send_json({"error": "Not found"}, 404)
    
    def do_DELETE(self) -> None:
        path = self.path.split("?")[0]
        
        if path.startswith("/users/"):
            user_id = self._parse_user_id()
            if not user_id or user_id not in USERS:
                self._send_json({"error": "User not found"}, 404)
                return
            
            del USERS[user_id]
            self.send_response(204)
            self.end_headers()
        else:
            self._send_json({"error": "Not found"}, 404)
    
    def log_message(self, format: str, *args) -> None:
        print(f"[L3 {time.strftime('%H:%M:%S')}] {args[0]}")


# ==============================================================================
# SERVER
# ==============================================================================

HANDLERS = {
    0: Level0Handler,
    1: Level1Handler,
    2: Level2Handler,
    3: Level3Handler,
}


def run_server(host: str, port: int, level: int) -> None:
    """Start serverul with nivelul REST specificat."""
    handler = HANDLERS.get(level)
    if not handler:
        print(f"Nivel invalid: {level}. Valori posibile: 0, 1, 2, 3")
        return
    
    reset_storage()
    server = ThreafromgHTTPServer((host, port), handler)
    
    level_names = {
        0: "RPC over HTTP (anti-pattern)",
        1: "Resurse addressbile",
        2: "Verbe HTTP + Coduri corecte",
        3: "HATEOAS (REST complet)"
    }
    
    print(f"[server] Nivel {level}: {level_names[level]}")
    print(f"[server] Pornit pe http://{host}:{port}/")
    print("[server] Apasati Ctrl+C for oprire.")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[server] Oprire...")
        server.shutdown()


# ==============================================================================
# SELF-TEST
# ==============================================================================

def run_selftest() -> int:
    """Testeaza all nivelurile."""
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError
    
    print("=" * 60)
    print("SELF-TEST: REST Maturity Levels")
    print("=" * 60)
    
    errors = 0
    
    for level in [0, 1, 2, 3]:
        print(f"\n[Test] Nivel {level}...")
        reset_storage()
        
        # Port liber
        with socket.socket() as s:
            s.bind(("", 0))
            port = s.getsockname()[1]
        
        handler = HANDLERS[level]
        server = ThreafromgHTTPServer(("127.0.0.1", port), handler)
        thread = threafromg.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        time.sleep(0.3)
        
        base = f"http://127.0.0.1:{port}"
        
        # Test specific for fiecare nivel
        try:
            if level == 0:
                # Nivel 0: POST /api with actiuni
                req = Request(f"{base}/api", method="POST")
                req.add_header("Content-Type", "application/json")
                req.data = b'{"action": "getUsers"}'
                with urlopen(req, timeout=3) as r:
                    data = json.loads(r.read())
                    if "users" in data:
                        print(f"  ✓ POST /api getUsers")
                    else:
                        print(f"  ✗ Missing users in response")
                        errors += 1
            
            elif level == 1:
                # Nivel 1: POST /users with actiuni
                req = Request(f"{base}/users", method="POST")
                req.add_header("Content-Type", "application/json")
                req.data = b'{"action": "list"}'
                with urlopen(req, timeout=3) as r:
                    data = json.loads(r.read())
                    if "users" in data:
                        print(f"  ✓ POST /users list")
                    else:
                        errors += 1
            
            elif level == 2:
                # Nivel 2: GET /users
                req = Request(f"{base}/users", method="GET")
                with urlopen(req, timeout=3) as r:
                    data = json.loads(r.read())
                    if isinstance(data, list):
                        print(f"  ✓ GET /users → lista")
                    else:
                        errors += 1
                
                # POST /users → 201
                req = Request(f"{base}/users", method="POST")
                req.add_header("Content-Type", "application/json")
                req.data = b'{"name": "Test"}'
                with urlopen(req, timeout=3) as r:
                    if r.status == 201:
                        print(f"  ✓ POST /users → 201 Created")
                    else:
                        errors += 1
            
            elif level == 3:
                # Nivel 3: GET / → links
                req = Request(f"{base}/", method="GET")
                with urlopen(req, timeout=3) as r:
                    data = json.loads(r.read())
                    if "_links" in data:
                        print(f"  ✓ GET / → _links (HATEOAS)")
                    else:
                        errors += 1
                
                # GET /users → users with _links
                req = Request(f"{base}/users", method="GET")
                with urlopen(req, timeout=3) as r:
                    data = json.loads(r.read())
                    if data.get("users") and "_links" in data["users"][0]:
                        print(f"  ✓ GET /users → users cu _links")
                    else:
                        errors += 1
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
            errors += 1
        
        finally:
            server.shutdown()
    
    print("\n" + "=" * 60)
    if errors == 0:
        print("Toate testele au trecut! ✓")
        return 0
    else:
        print(f"{errors} test(e) esuat(e)!")
        return 1


# ==============================================================================
# MAIN
# ==============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Exercitiul 10.02 – REST Maturity Levels"
    )
    subparsers = parser.add_subparsers(dest="command")
    
    serve = subparsers.add_parser("serve", help="Porneste serverul")
    serve.add_argument("--bind", default="0.0.0.0")
    serve.add_argument("--port", type=int, default=8080)
    serve.add_argument("--level", type=int, default=2, choices=[0, 1, 2, 3],
                       help="Nivelul REST (0-3)")
    
    subparsers.add_parser("selftest", help="Ruleaza self-test")
    
    args = parser.parse_args()
    
    if args.command == "serve":
        run_server(args.bind, args.port, args.level)
        return 0
    elif args.command == "selftest":
        return run_selftest()
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
