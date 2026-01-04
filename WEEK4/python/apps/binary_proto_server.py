#!/usr/bin/env python3
"""
Server TCP with protocol binar (header fix + CRC32).

PROTOCOL:
---------
Header (14 bytes):
  +--------+--------+--------+--------+--------+--------+
  | magic  |version | type   |payload_len| seq  | crc32  |
  | 2B     | 1B     | 1B     | 2B       | 4B   | 4B     |
  +--------+--------+--------+--------+--------+--------+
  
  magic: b"NP" (Network Protocol)
  version: 1
  type: tip mesaj (vezi mai jos)
  payload_len: payload length-ului in bytes
  seq: sequence number for corelatie request-response
  crc32: checksum peste header (fara crc) + payload

Payload (variabil):
  - For PUT: key_len(1B) + key(N) + value(M)
  - For GET: key_len(1B) + key(N)
  - For ECHO: orice bytes
  - For COUNT: gol
  - For KEYS: gol

TIPURI DE MESAJE:
-----------------
  ECHO_REQ(1)   → ECHO_RESP(2): ecou bytes
  PUT_REQ(3)    → PUT_RESP(4): stocheaza key-value
  GET_REQ(5)    → GET_RESP(6): returns valoarea
  COUNT_REQ(9)  → COUNT_RESP(10): number of of keys
  KEYS_REQ(7)   → KEYS_RESP(8): lista cheilor
  ERROR(255)    → eroare

DE CE ACEST DESIGN:
-------------------
- Parsing predictibil: header fix of 14 bytes
- Overhead mai mic decat text for volume mari
- CRC32 detects transmission errors
- Big-endian (network byte order) for interoperabilitate

UTILIZARE:
----------
  python3 binary_proto_server.py --port 4444 --verbose
"""
from __future__ import annotations

import argparse
import socket
import threading
import struct
import sys
from typing import Dict, Tuple

# Add utils directory to path
sys.path.insert(0, str(__file__).rsplit('/', 2)[0] + '/utils')
from io_utils import recv_exact
from proto_common import (
    BIN_HEADER_LEN, BIN_MAGIC, BIN_VERSION,
    TYPE_ECHO_REQ, TYPE_ECHO_RESP,
    TYPE_PUT_REQ, TYPE_PUT_RESP,
    TYPE_GET_REQ, TYPE_GET_RESP,
    TYPE_COUNT_REQ, TYPE_COUNT_RESP,
    TYPE_KEYS_REQ, TYPE_KEYS_RESP,
    TYPE_ERR,
    unpack_bin_header, pack_bin_message, validate_bin_message,
    decode_kv, decode_key
)


def handle_client(
    conn: socket.socket,
    addr: Tuple[str, int],
    state: Dict[str, str],
    lock: threading.Lock,
    verbose: bool
) -> None:
    """
    Handle comunicarea with un singur client.
    
    Loop of procesare mesaje:
    1. Citim header (14 bytes)
    2. Validam magic and version
    3. Citim payload (payload_len bytes)
    4. Verifym CRC
    5. Process comanda
    6. Sendm response
    """
    with conn:
        if verbose:
            print(f"[BIN] + connected {addr[0]}:{addr[1]}")
        
        try:
            while True:
                # 1. Citim header
                try:
                    header_bytes = recv_exact(conn, BIN_HEADER_LEN)
                except ConnectionError:
                    break
                
                # 2. Parsam header
                try:
                    header = unpack_bin_header(header_bytes)
                except Exception as e:
                    if verbose:
                        print(f"[BIN] ! invalid header from {addr}: {e}")
                    break
                
                # 3. Validam protocol
                if not header.is_valid_protocol():
                    if verbose:
                        print(f"[BIN] ! protocol mismatch from {addr}")
                    resp = pack_bin_message(TYPE_ERR, b"bad_protocol", header.seq)
                    conn.sendall(resp)
                    break
                
                # 4. Citim payload
                payload = recv_exact(conn, header.payload_len)
                
                # 5. Verifym CRC
                if not validate_bin_message(header, payload):
                    if verbose:
                        print(f"[BIN] ! CRC mismatch from {addr}")
                    resp = pack_bin_message(TYPE_ERR, b"crc_mismatch", header.seq)
                    conn.sendall(resp)
                    continue
                
                if verbose:
                    print(f"[BIN] < {addr[0]}:{addr[1]}: type={header.type_name} seq={header.seq} len={header.payload_len}")
                
                # 6. Process comanda
                resp = process_request(header.mtype, header.seq, payload, state, lock)
                
                # 7. Sendm response
                conn.sendall(resp)
                
                if verbose:
                    resp_header = unpack_bin_header(resp[:BIN_HEADER_LEN])
                    print(f"[BIN] > {addr[0]}:{addr[1]}: type={resp_header.type_name} seq={resp_header.seq}")
                    
        except Exception as e:
            if verbose:
                print(f"[BIN] ! error handling {addr}: {e}")
        
        if verbose:
            print(f"[BIN] - disconnected {addr[0]}:{addr[1]}")


def process_request(
    mtype: int,
    seq: int,
    payload: bytes,
    state: Dict[str, str],
    lock: threading.Lock
) -> bytes:
    """
    Process un request and returns raspunsul impachetat.
    """
    # ECHO - returns payload-ul primit
    if mtype == TYPE_ECHO_REQ:
        return pack_bin_message(TYPE_ECHO_RESP, payload, seq)
    
    # PUT - stocheaza key-value
    if mtype == TYPE_PUT_REQ:
        try:
            key, value = decode_kv(payload)
        except Exception as e:
            return pack_bin_message(TYPE_ERR, f"bad_put_payload: {e}".encode(), seq)
        
        with lock:
            state[key] = value
        
        return pack_bin_message(TYPE_PUT_RESP, b"OK", seq)
    
    # GET - returns valoarea
    if mtype == TYPE_GET_REQ:
        try:
            key = decode_key(payload)
        except Exception as e:
            return pack_bin_message(TYPE_ERR, f"bad_get_payload: {e}".encode(), seq)
        
        with lock:
            value = state.get(key, "")
        
        if not value and key not in state:
            return pack_bin_message(TYPE_ERR, b"not_found", seq)
        
        return pack_bin_message(TYPE_GET_RESP, value.encode("utf-8"), seq)
    
    # COUNT - number of of keys
    if mtype == TYPE_COUNT_REQ:
        with lock:
            count = len(state)
        # Returnam count-ul ca unsigned int (4 bytes, big-endian)
        return pack_bin_message(TYPE_COUNT_RESP, struct.pack("!I", count), seq)
    
    # KEYS - lista cheilor
    if mtype == TYPE_KEYS_REQ:
        with lock:
            keys = list(state.keys())
        
        # Encodem lista: num_keys(2B) + [key_len(1B) + key(N)]...
        parts = [struct.pack("!H", len(keys))]
        for key in sorted(keys):
            kb = key.encode("utf-8")
            parts.append(struct.pack("!B", len(kb)) + kb)
        
        return pack_bin_message(TYPE_KEYS_RESP, b"".join(parts), seq)
    
    # Tip necunoscut
    return pack_bin_message(TYPE_ERR, f"unknown_type: {mtype}".encode(), seq)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Server TCP with protocol binar (header fix + CRC32)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--host", default="0.0.0.0", help="Adresa of bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5401, help="Portul of ascultare (default: 5401 - WEEK4 standard)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Afiseaza mesajele procesate")
    
    args = parser.parse_args()
    
    state: Dict[str, str] = {}
    lock = threading.Lock()
    
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        srv.bind((args.host, args.port))
        srv.listen(16)
        
        print(f"[BIN] Server listening on {args.host}:{args.port}")
        print(f"[BIN] Protocol: binary header (14B) + CRC32")
        print(f"[BIN] Press Ctrl+C to stop")
        
        while True:
            conn, addr = srv.accept()
            t = threading.Thread(
                target=handle_client,
                args=(conn, addr, state, lock, args.verbose),
                daemon=True
            )
            t.start()
            
    except KeyboardInterrupt:
        print("\n[BIN] Shutting down...")
        return 0
    except Exception as e:
        print(f"[BIN] Error: {e}")
        return 1
    finally:
        try:
            srv.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
