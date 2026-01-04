#!/usr/bin/env python3
"""
Client TCP for protocolul text (length-prefixed framing).

INTERACTIVE USAGE:
----------------------
  python3 text_proto_client.py --host localhost --port 5400
  
  > PING
  < OK pong
  > SET name Alice
  < OK stored name
  > GET name
  < OK name Alice
  > COUNT
  < OK 1 keys
  > QUIT
  < OK bye

SCRIPTED USAGE:
-----------------------
  python3 text_proto_client.py --host localhost --port 5400 \\
      --command "SET name Alice" --command "GET name"
"""
from __future__ import annotations

import argparse
import socket
import sys

# Add utils directory to path
sys.path.insert(0, str(__file__).rsplit('/', 2)[0] + '/utils')
from io_utils import recv_until, recv_exact


def recv_framed(conn: socket.socket) -> str:
    """Receive a message with length-prefix framing."""
    raw = recv_until(conn, b" ", max_bytes=16)
    len_str = raw[:-1].decode("ascii", errors="strict").strip()
    if not len_str.isdigit():
        raise ValueError(f"invalid length prefix: {len_str!r}")
    payload_len = int(len_str)
    payload_bytes = recv_exact(conn, payload_len)
    return payload_bytes.decode("utf-8", errors="replace")


def send_framed(conn: socket.socket, payload: str) -> None:
    """Send a message with length-prefix framing."""
    payload_bytes = payload.encode("utf-8")
    header = f"{len(payload_bytes)} ".encode("ascii")
    conn.sendall(header + payload_bytes)


def interactive_mode(conn: socket.socket) -> None:
    """Mod interactiv: reads commands of to stdin."""
    print("Connected! Type commands (PING, SET, GET, DEL, COUNT, KEYS, QUIT)")
    print("Type 'exit' or Ctrl+C to disconnect\n")
    
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nDisconnecting...")
            break
        
        if not line:
            continue
        
        if line.lower() in ("exit", "quit"):
            try:
                send_framed(conn, "QUIT")
                resp = recv_framed(conn)
                print(f"< {resp}")
            except Exception:
                pass
            break
        
        try:
            send_framed(conn, line)
            resp = recv_framed(conn)
            print(f"< {resp}")
        except ConnectionError as e:
            print(f"Connection lost: {e}")
            break
        except Exception as e:
            print(f"Error: {e}")
            break


def command_mode(conn: socket.socket, commands: list[str], verbose: bool) -> int:
    """Mod batch: executa lista of commands and prints raspunsurile."""
    errors = 0
    
    for cmd in commands:
        if verbose:
            print(f"> {cmd}")
        
        try:
            send_framed(conn, cmd)
            resp = recv_framed(conn)
            
            if verbose or resp.startswith("ERR"):
                print(f"< {resp}")
            else:
                print(resp)
            
            if resp.startswith("ERR"):
                errors += 1
                
        except Exception as e:
            print(f"Error executing '{cmd}': {e}")
            errors += 1
            break
    
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Client TCP for protocolul text",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--host", default="localhost", help="Server hostname (default: localhost)")
    parser.add_argument("--port", type=int, default=5400, help="Server port (default: 5400)")
    parser.add_argument("--command", "-c", action="append", dest="commands",
                        help="Command to execute (can be repeated for batch mode)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show sent commands")
    
    args = parser.parse_args()
    
    # Conectare
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((args.host, args.port))
    except Exception as e:
        print(f"Connection failed: {e}")
        return 1
    
    try:
        if args.commands:
            # Batch mode
            return command_mode(conn, args.commands, args.verbose)
        else:
            # Interactive mode
            interactive_mode(conn)
            return 0
    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
