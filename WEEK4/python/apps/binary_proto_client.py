#!/usr/bin/env python3
"""
Client TCP for protocolul binar (header fix + CRC32).

INTERACTIVE USAGE:
----------------------
  python3 binary_proto_client.py --host localhost --port 5401
  
  > echo Hello World
  < ECHO_RESP: b'Hello World'
  > put name Alice
  < PUT_RESP: b'OK'
  > get name
  < GET_RESP: Alice
  > count
  < COUNT_RESP: 1
  > keys
  < KEYS_RESP: ['name']
  > quit

SCRIPTED USAGE:
-----------------------
  python3 binary_proto_client.py --host localhost --port 5401 \\
      --command "put name Alice" --command "get name"
"""
from __future__ import annotations

import argparse
import socket
import struct
import sys

# Add utils directory to path
sys.path.insert(0, str(__file__).rsplit('/', 2)[0] + '/utils')
from io_utils import recv_exact
from proto_common import (
    BIN_HEADER_LEN,
    TYPE_ECHO_REQ, TYPE_ECHO_RESP,
    TYPE_PUT_REQ, TYPE_PUT_RESP,
    TYPE_GET_REQ, TYPE_GET_RESP,
    TYPE_COUNT_REQ, TYPE_COUNT_RESP,
    TYPE_KEYS_REQ, TYPE_KEYS_RESP,
    TYPE_ERR,
    unpack_bin_header, pack_bin_message, validate_bin_message,
    encode_kv, encode_key
)


class BinaryClient:
    """Client for protocolul binar."""
    
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.conn: socket.socket | None = None
        self.seq = 0
    
    def connect(self) -> None:
        """Stabileste conexiunea."""
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.host, self.port))
    
    def close(self) -> None:
        """Inchiof conexiunea."""
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn = None
    
    def _next_seq(self) -> int:
        """Returns urmatorul sequence number."""
        self.seq += 1
        return self.seq
    
    def _send_recv(self, mtype: int, payload: bytes) -> tuple[int, bytes]:
        """
        Send a message and primeste raspunsul.
        
        Returns:
            Tuple of (response_type, response_payload)
        """
        if not self.conn:
            raise ConnectionError("Not connected")
        
        # Construim and trimitem mesajul
        seq = self._next_seq()
        msg = pack_bin_message(mtype, payload, seq)
        self.conn.sendall(msg)
        
        # Receive header response
        header_bytes = recv_exact(self.conn, BIN_HEADER_LEN)
        header = unpack_bin_header(header_bytes)
        
        # Receive payload
        resp_payload = recv_exact(self.conn, header.payload_len)
        
        # Verifym CRC
        if not validate_bin_message(header, resp_payload):
            raise ValueError("Response CRC mismatch")
        
        # Verifym seq (optional)
        if header.seq != seq:
            print(f"Warning: seq mismatch (expected {seq}, got {header.seq})")
        
        return header.mtype, resp_payload
    
    def echo(self, data: bytes) -> bytes:
        """Send ECHO and returns raspunsul."""
        rtype, payload = self._send_recv(TYPE_ECHO_REQ, data)
        if rtype == TYPE_ERR:
            raise RuntimeError(f"Server error: {payload.decode()}")
        return payload
    
    def put(self, key: str, value: str) -> bool:
        """Stocheaza o pereche key-value. Returns True daca reusit."""
        payload = encode_kv(key, value)
        rtype, resp = self._send_recv(TYPE_PUT_REQ, payload)
        if rtype == TYPE_ERR:
            raise RuntimeError(f"Server error: {resp.decode()}")
        return rtype == TYPE_PUT_RESP
    
    def get(self, key: str) -> str | None:
        """Returns valoarea or None daca nu exists."""
        payload = encode_key(key)
        rtype, resp = self._send_recv(TYPE_GET_REQ, payload)
        if rtype == TYPE_ERR:
            if b"not_found" in resp:
                return None
            raise RuntimeError(f"Server error: {resp.decode()}")
        return resp.decode("utf-8")
    
    def count(self) -> int:
        """Returns number of of keys."""
        rtype, resp = self._send_recv(TYPE_COUNT_REQ, b"")
        if rtype == TYPE_ERR:
            raise RuntimeError(f"Server error: {resp.decode()}")
        return struct.unpack("!I", resp)[0]
    
    def keys(self) -> list[str]:
        """Returns lista cheilor."""
        rtype, resp = self._send_recv(TYPE_KEYS_REQ, b"")
        if rtype == TYPE_ERR:
            raise RuntimeError(f"Server error: {resp.decode()}")
        
        # Decodam: num_keys(2B) + [key_len(1B) + key(N)]...
        if len(resp) < 2:
            return []
        
        num_keys = struct.unpack("!H", resp[:2])[0]
        keys = []
        offset = 2
        
        for _ in range(num_keys):
            if offset >= len(resp):
                break
            klen = resp[offset]
            offset += 1
            key = resp[offset:offset+klen].decode("utf-8")
            keys.append(key)
            offset += klen
        
        return keys


def interactive_mode(client: BinaryClient) -> None:
    """Mod interactiv."""
    print("Connected! Commands: echo <data>, put <key> <value>, get <key>, count, keys, quit")
    print()
    
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nDisconnecting...")
            break
        
        if not line:
            continue
        
        parts = line.split(maxsplit=2)
        cmd = parts[0].lower()
        
        try:
            if cmd == "quit" or cmd == "exit":
                break
            
            elif cmd == "echo":
                data = " ".join(parts[1:]) if len(parts) > 1 else ""
                result = client.echo(data.encode("utf-8"))
                print(f"< ECHO_RESP: {result!r}")
            
            elif cmd == "put":
                if len(parts) < 3:
                    print("Usage: put <key> <value>")
                    continue
                key = parts[1]
                value = parts[2]
                client.put(key, value)
                print(f"< PUT_RESP: OK")
            
            elif cmd == "get":
                if len(parts) < 2:
                    print("Usage: get <key>")
                    continue
                key = parts[1]
                value = client.get(key)
                if value is None:
                    print("< GET_RESP: (not found)")
                else:
                    print(f"< GET_RESP: {value}")
            
            elif cmd == "count":
                n = client.count()
                print(f"< COUNT_RESP: {n}")
            
            elif cmd == "keys":
                ks = client.keys()
                print(f"< KEYS_RESP: {ks}")
            
            else:
                print(f"Unknown command: {cmd}")
                
        except Exception as e:
            print(f"Error: {e}")


def command_mode(client: BinaryClient, commands: list[str], verbose: bool) -> int:
    """Executa commands batch."""
    errors = 0
    
    for cmd_line in commands:
        parts = cmd_line.split(maxsplit=2)
        cmd = parts[0].lower()
        
        if verbose:
            print(f"> {cmd_line}")
        
        try:
            if cmd == "echo":
                data = " ".join(parts[1:]) if len(parts) > 1 else ""
                result = client.echo(data.encode("utf-8"))
                print(f"ECHO: {result.decode()}")
            
            elif cmd == "put":
                if len(parts) < 3:
                    print("ERR: put requires key and value")
                    errors += 1
                    continue
                client.put(parts[1], parts[2])
                print("OK")
            
            elif cmd == "get":
                if len(parts) < 2:
                    print("ERR: get requires key")
                    errors += 1
                    continue
                value = client.get(parts[1])
                if value is None:
                    print("(not found)")
                else:
                    print(value)
            
            elif cmd == "count":
                print(client.count())
            
            elif cmd == "keys":
                print(client.keys())
            
            else:
                print(f"Unknown: {cmd}")
                errors += 1
                
        except Exception as e:
            print(f"Error: {e}")
            errors += 1
    
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Client TCP for protocolul binar"
    )
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5401)
    parser.add_argument("--command", "-c", action="append", dest="commands")
    parser.add_argument("--verbose", "-v", action="store_true")
    
    args = parser.parse_args()
    
    client = BinaryClient(args.host, args.port)
    
    try:
        client.connect()
        
        if args.commands:
            return command_mode(client, args.commands, args.verbose)
        else:
            interactive_mode(client)
            return 0
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
