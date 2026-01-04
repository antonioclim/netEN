#!/usr/bin/env python3
"""
TEMPLATE: Server TCP with protocol text.

EXERCITIU:
----------
Completati functia process_command for a implementa comanda COUNT.

COUNT trebuie sa returneze number of of keys din state sub forma:
  "OK <n> keys"

Exemplu:
  Input:  "COUNT"
  Output: "OK 3 keys"  (daca sunt 3 keys in state)

HINT-uri:
- len(state) returns number of of keys dintr-un dictionar
- Formatati raspunsul folosind f-string
"""
from __future__ import annotations
import socket
import threading
import sys

sys.path.insert(0, str(__file__).rsplit('/', 2)[0] + '/utils')
from io_utils import recv_until, recv_exact


def recv_framed(conn: socket.socket) -> str:
    """Receive a message with length-prefix framing."""
    raw = recv_until(conn, b" ", max_bytes=16)
    len_str = raw[:-1].decode("ascii").strip()
    if not len_str.isdigit():
        raise ValueError(f"invalid length: {len_str!r}")
    payload = recv_exact(conn, int(len_str))
    return payload.decode("utf-8")


def send_framed(conn: socket.socket, payload: str) -> None:
    """Send a message with length-prefix framing."""
    pb = payload.encode("utf-8")
    header = f"{len(pb)} ".encode("ascii")
    conn.sendall(header + pb)


def process_command(state: dict, line: str) -> str:
    """
    Process o comanda and returns raspunsul.
    
    TODO: Implementati comanda COUNT (inlocuiti pass with codul vostru)
    """
    parts = line.strip().split()
    if not parts:
        return "ERR empty"
    
    cmd = parts[0].upper()
    
    if cmd == "PING":
        return "OK pong"
    
    if cmd == "SET":
        if len(parts) < 3:
            return "ERR usage: SET <key> <value>"
        key = parts[1]
        value = " ".join(parts[2:])
        state[key] = value
        return f"OK stored {key}"
    
    if cmd == "GET":
        if len(parts) != 2:
            return "ERR usage: GET <key>"
        key = parts[1]
        if key not in state:
            return "ERR not_found"
        return f"OK {key} {state[key]}"
    
    if cmd == "DEL":
        if len(parts) != 2:
            return "ERR usage: DEL <key>"
        key = parts[1]
        existed = key in state
        state.pop(key, None)
        return "OK deleted" if existed else "OK no_such_key"
    
    if cmd == "COUNT":
        # TODO: Implementati COUNT
        # Returnati "OK <n> keys" unof n este number of of keys din state
        pass  # <-- Inlocuiti aceasta linie
    
    return "ERR unknown_command"


def handle_client(conn: socket.socket, state: dict, lock: threading.Lock) -> None:
    """Handler for a client."""
    with conn:
        while True:
            try:
                line = recv_framed(conn)
            except (ConnectionError, ValueError):
                return
            
            with lock:
                resp = process_command(state, line)
            
            if resp is None:
                resp = "ERR not_implemented"
            
            send_framed(conn, resp)


def main() -> int:
    HOST, PORT = "0.0.0.0", 5400
    state = {}
    lock = threading.Lock()
    
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(8)
    
    print(f"[TEMPLATE] Text server on {HOST}:{PORT}")
    
    try:
        while True:
            conn, addr = srv.accept()
            t = threading.Thread(target=handle_client, args=(conn, state, lock), daemon=True)
            t.start()
    except KeyboardInterrupt:
        return 0
    finally:
        srv.close()


if __name__ == "__main__":
    raise SystemExit(main())
