#!/usr/bin/env python3
"""
Concurrent TCP server with text protocol (length-prefixed framing).

PROTOCOL:
---------
Framing: <LENGTH> <PAYLOAD>
  - LENGTH: number of bytes in payload (ASCII decimal)
  - space: separator
  - PAYLOAD: message content (UTF-8)

Example: "11 SET name Alice"
         ^^  ^^^^^^^^^^^^^^
         |   payload (11 bytes)
         payload length

AVAILABLE COMMANDS:
-------------------
  PING              → OK pong
  SET <key> <value> → OK stored <key>
  GET <key>         → OK <key> <value> | ERR not_found
  DEL <key>         → OK deleted | OK no_such_key
  COUNT             → OK <n> keys
  KEYS              → OK <key1> <key2> ...
  QUIT              → OK bye (closes connection)

WHY THIS DESIGN:
----------------
- Easy to debug: visible in tcpdump/tshark
- Explicit framing: eliminates TCP stream ambiguity
- Human-readable: can be partially tested with netcat

USAGE:
------
  python3 text_proto_server.py --port 5400 --verbose

LICENCE: MIT - ASE-CSIE Teaching Material
"""
from __future__ import annotations

import argparse
import socket
import threading
import sys
from typing import Dict

# Add utils directory to path
sys.path.insert(0, str(__file__).rsplit('/', 2)[0] + '/utils')
from io_utils import recv_until, recv_exact


def recv_framed(conn: socket.socket) -> str:
    """
    Receive a message with length-prefix framing.
    
    Format: <LEN> <PAYLOAD>
    Where LEN is the length in bytes (ASCII digits) followed by space.
    
    Raises:
        ConnectionError: If connection is closed
        ValueError: If format does not match
    """
    # Read until space (separator after length)
    raw = recv_until(conn, b" ", max_bytes=16)
    len_str = raw[:-1].decode("ascii").strip()
    
    if not len_str.isdigit():
        raise ValueError(f"invalid length prefix: {len_str!r}")
    
    payload_len = int(len_str)
    if payload_len > 65535:
        raise ValueError(f"payload too large: {payload_len}")
    
    payload_bytes = recv_exact(conn, payload_len)
    return payload_bytes.decode("utf-8", errors="replace")


def send_framed(conn: socket.socket, payload: str) -> None:
    """
    Send a message with length-prefix framing.
    
    Format: <LEN> <PAYLOAD>
    """
    payload_bytes = payload.encode("utf-8")
    header = f"{len(payload_bytes)} ".encode("ascii")
    conn.sendall(header + payload_bytes)


def process_command(state: Dict[str, str], line: str) -> str:
    """
    Process a command and return the response.
    
    State is the shared dictionary (thread-safe via external lock).
    """
    parts = line.strip().split()
    if not parts:
        return "ERR empty_command"
    
    cmd = parts[0].upper()
    
    # PING - connectivity test
    if cmd == "PING":
        return "OK pong"
    
    # SET <key> <value> - store a value
    if cmd == "SET":
        if len(parts) < 3:
            return "ERR usage: SET <key> <value>"
        key = parts[1]
        value = " ".join(parts[2:])  # value may contain spaces
        state[key] = value
        return f"OK stored {key}"
    
    # GET <key> - read a value
    if cmd == "GET":
        if len(parts) != 2:
            return "ERR usage: GET <key>"
        key = parts[1]
        if key not in state:
            return "ERR not_found"
        return f"OK {key} {state[key]}"
    
    # DEL <key> - delete a key
    if cmd == "DEL":
        if len(parts) != 2:
            return "ERR usage: DEL <key>"
        key = parts[1]
        existed = key in state
        state.pop(key, None)
        return "OK deleted" if existed else "OK no_such_key"
    
    # COUNT - number of keys
    if cmd == "COUNT":
        return f"OK {len(state)} keys"
    
    # KEYS - list of keys
    if cmd == "KEYS":
        if not state:
            return "OK"
        return "OK " + " ".join(sorted(state.keys()))
    
    # QUIT - close connection
    if cmd == "QUIT":
        return "OK bye"
    
    return "ERR unknown_command"


def handle_client(
    conn: socket.socket,
    addr: tuple,
    state: Dict[str, str],
    lock: threading.Lock,
    verbose: bool
) -> None:
    """
    Handle communication with a client.
    
    Processing loop:
    1. Receive framed message
    2. Process command (with lock on state)
    3. Send response
    4. Repeat until QUIT or error
    """
    with conn:
        if verbose:
            print(f"[TEXT] + connected {addr[0]}:{addr[1]}")
        
        try:
            while True:
                # 1. Receive message
                try:
                    line = recv_framed(conn)
                except (ConnectionError, ValueError) as e:
                    if verbose:
                        print(f"[TEXT] ! recv error from {addr}: {e}")
                    break
                
                if verbose:
                    print(f"[TEXT] < {addr[0]}:{addr[1]}: {line}")
                
                # 2. Process command (thread-safe)
                with lock:
                    response = process_command(state, line)
                
                # 3. Send response
                send_framed(conn, response)
                
                if verbose:
                    print(f"[TEXT] > {addr[0]}:{addr[1]}: {response}")
                
                # 4. QUIT closes connection
                if line.strip().upper() == "QUIT":
                    break
                    
        except Exception as e:
            if verbose:
                print(f"[TEXT] ! error handling {addr}: {e}")
        
        if verbose:
            print(f"[TEXT] - disconnected {addr[0]}:{addr[1]}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="TCP server with text protocol (length-prefixed framing)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  python3 text_proto_server.py --port 5400 --verbose
  
Testing with client:
  python3 text_proto_client.py --host localhost --port 5400 -c "PING"
        """
    )
    parser.add_argument(
        "--host", default="0.0.0.0",
        help="Bind address (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=5400,
        help="Listening port (default: 5400 - WEEK4 standard)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Display processed messages"
    )
    
    args = parser.parse_args()
    
    # State shared between threads
    state: Dict[str, str] = {}
    lock = threading.Lock()
    
    # Create server socket
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        srv.bind((args.host, args.port))
        srv.listen(16)
        
        print(f"[TEXT] Server listening on {args.host}:{args.port}")
        print(f"[TEXT] Protocol: length-prefixed text (<LEN> <PAYLOAD>)")
        print(f"[TEXT] Commands: PING, SET, GET, DEL, COUNT, KEYS, QUIT")
        print(f"[TEXT] Press Ctrl+C to stop")
        
        while True:
            conn, addr = srv.accept()
            t = threading.Thread(
                target=handle_client,
                args=(conn, addr, state, lock, args.verbose),
                daemon=True
            )
            t.start()
            
    except KeyboardInterrupt:
        print("\n[TEXT] Shutting down...")
        return 0
    except Exception as e:
        print(f"[TEXT] Error: {e}")
        return 1
    finally:
        try:
            srv.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
