#!/usr/bin/env python3
"""Week 10 - REST maturity levels (Richardson model).

This script provides a single Flask application that exposes four groups of
endpoints, each illustrating a different REST maturity level:

- Level 0: Single endpoint, RPC-style actions
- Level 1: Resource-oriented URIs but action-style subpaths
- Level 2: Proper use of HTTP verbs and status codes
- Level 3: Level 2 plus HATEOAS links in responses

Run
---
  python3 ex_10_02_rest_levels.py serve

Then open:
  http://127.0.0.1:5000/

Selftest
--------
  python3 ex_10_02_rest_levels.py selftest

References
----------
Richardson's maturity model (commonly used teaching tool).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, request, url_for


@dataclass
class User:
    id: int
    name: str
    email: str


class Store:
    def __init__(self) -> None:
        self._users: Dict[int, User] = {
            1: User(id=1, name="Alice Example", email="alice@example.test"),
            2: User(id=2, name="Bob Example", email="bob@example.test"),
        }
        self._next_id = 3

    def list_users(self) -> List[User]:
        return list(self._users.values())

    def get_user(self, uid: int) -> Optional[User]:
        return self._users.get(uid)

    def create_user(self, name: str, email: str) -> User:
        u = User(id=self._next_id, name=name, email=email)
        self._users[u.id] = u
        self._next_id += 1
        return u

    def update_user(self, uid: int, name: Optional[str], email: Optional[str]) -> Optional[User]:
        u = self._users.get(uid)
        if u is None:
            return None
        if name is not None:
            u.name = name
        if email is not None:
            u.email = email
        return u

    def delete_user(self, uid: int) -> bool:
        return self._users.pop(uid, None) is not None


STORE = Store()


def user_to_dict(u: User) -> Dict[str, Any]:
    return asdict(u)


def add_links(payload: Dict[str, Any], uid: int) -> Dict[str, Any]:
    payload = dict(payload)
    payload["_links"] = {
        "self": url_for("level3_get_user", uid=uid, _external=False),
        "collection": url_for("level3_list_users", _external=False),
        "update": url_for("level3_put_user", uid=uid, _external=False),
        "delete": url_for("level3_delete_user", uid=uid, _external=False),
    }
    return payload


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index() -> Any:
        return (
            "<h1>Week 10 - REST Maturity Levels</h1>"
            "<ul>"
            "<li>/level0/service (POST)</li>"
            "<li>/level1/users (GET, POST) and /level1/users/&lt;id&gt;/* (POST)</li>"
            "<li>/level2/users (GET, POST) and /level2/users/&lt;id&gt; (GET, PUT, DELETE)</li>"
            "<li>/level3/users (GET, POST) and /level3/users/&lt;id&gt; (GET, PUT, DELETE) with links</li>"
            "</ul>"
        )

    # ------------------------------------------------------------------
    # LEVEL 0 - RPC style
    # ------------------------------------------------------------------
    @app.post("/level0/service")
    def level0_service() -> Any:
        data = request.get_json(silent=True) or {}
        action = str(data.get("action", "")).strip()

        if action == "list_users":
            return jsonify({"users": [user_to_dict(u) for u in STORE.list_users()]})

        if action == "get_user":
            uid = int(data.get("id", 0))
            u = STORE.get_user(uid)
            if u is None:
                return jsonify({"error": "User not found"}), 404
            return jsonify(user_to_dict(u))

        if action == "create_user":
            user = data.get("user") or {}
            name = str(user.get("name", "")).strip()
            email = str(user.get("email", "")).strip()
            if not name or not email:
                return jsonify({"error": "Missing name or email"}), 400
            u = STORE.create_user(name=name, email=email)
            return jsonify(user_to_dict(u)), 201

        return jsonify({"error": "Unknown action"}), 400

    # ------------------------------------------------------------------
    # LEVEL 1 - Resource URIs with action endpoints
    # ------------------------------------------------------------------
    @app.get("/level1/users")
    def level1_list_users() -> Any:
        return jsonify({"users": [user_to_dict(u) for u in STORE.list_users()]})

    @app.post("/level1/users")
    def level1_create_user() -> Any:
        data = request.get_json(silent=True) or {}
        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip()
        if not name or not email:
            return jsonify({"error": "Missing name or email"}), 400
        u = STORE.create_user(name=name, email=email)
        return jsonify(user_to_dict(u)), 201

    @app.get("/level1/users/<int:uid>")
    def level1_get_user(uid: int) -> Any:
        u = STORE.get_user(uid)
        if u is None:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user_to_dict(u))

    @app.post("/level1/users/<int:uid>/update")
    def level1_update_user(uid: int) -> Any:
        data = request.get_json(silent=True) or {}
        name = data.get("name")
        email = data.get("email")
        u = STORE.update_user(uid, name=str(name).strip() if name is not None else None, email=str(email).strip() if email is not None else None)
        if u is None:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user_to_dict(u))

    @app.post("/level1/users/<int:uid>/delete")
    def level1_delete_user(uid: int) -> Any:
        if not STORE.delete_user(uid):
            return jsonify({"error": "User not found"}), 404
        return jsonify({"status": "deleted"})

    # ------------------------------------------------------------------
    # LEVEL 2 - Proper HTTP verbs
    # ------------------------------------------------------------------
    @app.get("/level2/users")
    def level2_list_users() -> Any:
        return jsonify({"users": [user_to_dict(u) for u in STORE.list_users()]})

    @app.post("/level2/users")
    def level2_create_user() -> Any:
        data = request.get_json(silent=True) or {}
        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip()
        if not name or not email:
            return jsonify({"error": "Missing name or email"}), 400
        u = STORE.create_user(name=name, email=email)
        return jsonify(user_to_dict(u)), 201

    @app.get("/level2/users/<int:uid>")
    def level2_get_user(uid: int) -> Any:
        u = STORE.get_user(uid)
        if u is None:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user_to_dict(u))

    @app.put("/level2/users/<int:uid>")
    def level2_put_user(uid: int) -> Any:
        data = request.get_json(silent=True) or {}
        name = data.get("name")
        email = data.get("email")
        u = STORE.update_user(uid, name=str(name).strip() if name is not None else None, email=str(email).strip() if email is not None else None)
        if u is None:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user_to_dict(u))

    @app.delete("/level2/users/<int:uid>")
    def level2_delete_user(uid: int) -> Any:
        if not STORE.delete_user(uid):
            return jsonify({"error": "User not found"}), 404
        return ("", 204)

    # ------------------------------------------------------------------
    # LEVEL 3 - HATEOAS
    # ------------------------------------------------------------------
    @app.get("/level3/users")
    def level3_list_users() -> Any:
        users = [add_links(user_to_dict(u), u.id) for u in STORE.list_users()]
        return jsonify({"users": users, "_links": {"self": url_for("level3_list_users", _external=False)}})

    @app.post("/level3/users")
    def level3_create_user() -> Any:
        data = request.get_json(silent=True) or {}
        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip()
        if not name or not email:
            return jsonify({"error": "Missing name or email"}), 400
        u = STORE.create_user(name=name, email=email)
        payload = add_links(user_to_dict(u), u.id)
        return jsonify(payload), 201

    @app.get("/level3/users/<int:uid>")
    def level3_get_user(uid: int) -> Any:
        u = STORE.get_user(uid)
        if u is None:
            return jsonify({"error": "User not found"}), 404
        return jsonify(add_links(user_to_dict(u), uid))

    @app.put("/level3/users/<int:uid>")
    def level3_put_user(uid: int) -> Any:
        data = request.get_json(silent=True) or {}
        name = data.get("name")
        email = data.get("email")
        u = STORE.update_user(uid, name=str(name).strip() if name is not None else None, email=str(email).strip() if email is not None else None)
        if u is None:
            return jsonify({"error": "User not found"}), 404
        return jsonify(add_links(user_to_dict(u), uid))

    @app.delete("/level3/users/<int:uid>")
    def level3_delete_user(uid: int) -> Any:
        if not STORE.delete_user(uid):
            return jsonify({"error": "User not found"}), 404
        return ("", 204)

    return app


def selftest() -> int:
    app = create_app()
    client = app.test_client()

    # Level 0
    r = client.post("/level0/service", json={"action": "list_users"})
    if r.status_code != 200:
        print("[ERROR] Level 0 list_users failed")
        return 1

    # Level 2 create -> update -> delete
    r = client.post("/level2/users", json={"name": "Charlie Example", "email": "charlie@example.test"})
    if r.status_code != 201:
        print("[ERROR] Level 2 create failed")
        return 1
    uid = int(r.get_json()["id"])  # type: ignore[index]

    r = client.put(f"/level2/users/{uid}", json={"name": "Charlie Updated"})
    if r.status_code != 200:
        print("[ERROR] Level 2 update failed")
        return 1

    r = client.delete(f"/level2/users/{uid}")
    if r.status_code != 204:
        print("[ERROR] Level 2 delete failed")
        return 1

    # Level 3 links
    r = client.get("/level3/users")
    if r.status_code != 200:
        print("[ERROR] Level 3 list failed")
        return 1
    payload = r.get_json()  # type: ignore[assignment]
    if "_links" not in payload:
        print("[ERROR] Level 3 missing top-level links")
        return 1

    print("[OK] REST maturity levels selftest passed")
    return 0


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Week 10 REST maturity levels")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_serve = sub.add_parser("serve", help="Start the Flask application")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=5000)

    sub.add_parser("selftest", help="Run a local selftest")

    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)

    if args.cmd == "selftest":
        return selftest()

    if args.cmd == "serve":
        app = create_app()
        app.run(host=args.host, port=args.port, debug=False)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
