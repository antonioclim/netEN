#!/usr/bin/env python3
"""
Template: Server Protocol BINARY TCP
=====================================

Completati functiile marcate with TODO for a implementa a server
care foloseste protocol binar with header fix.

Structura header (14 bytes):
  [0:2]   magic: "NP" (0x4E50)
  [2]     version: 1
  [3]     type: 0x01=DATA, 0x02=ACK, 0xFF=ERROR
  [4:6]   payload_len: uint16 BE
  [6:10]  seq_num: uint32 BE
  [10:14] crc32: uint32 BE

Autor: Revolvix&Hypotheticalandrei
Week 4 - Template server BINARY
"""

import socket
import struct
import zlib
import threading

# Constante protocol
MAGIC = b'NP'
VERSION = 1
TYPE_DATA = 0x01
TYPE_ACK = 0x02
TYPE_ERROR = 0xFF
HEADER_SIZE = 14
DEFAULT_PORT = 5401


def calculate_crc32(data: bytes) -> int:
    """Calculate CRC32 for date."""
    return zlib.crc32(data) & 0xFFFFFFFF


def recv_exact(sock: socket.socket, n: int) -> bytes:
    """
    Receive exact n bytes of pe socket.
    
    TODO: Implementati aceasta function
    Hint: Folositi un loop and concatenati bytes pana aveti n
    """
    # TODO: Implementare
    # data = b''
    # while len(data) < n:
    #     chunk = sock.recv(n - len(data))
    #     if not chunk:
    #         raise ConnectionError("Conexiune inchisa prematur")
    #     data += chunk
    # return data
    pass


def pack_header(msg_type: int, payload_len: int, seq_num: int, crc: int) -> bytes:
    """
    Impacheteaza header-ul binar.
    
    TODO: Implementati aceasta function
    Hint: struct.pack('>2sBBHII', MAGIC, VERSION, msg_type, payload_len, seq_num, crc)
    """
    # TODO: Implementare
    pass


def unpack_header(header: bytes) -> tuple:
    """
    Despacheaza header-ul binar.
    
    Returns:
        tuple: (magic, version, msg_type, payload_len, seq_num, crc)
    
    TODO: Implementati aceasta function
    """
    # TODO: Implementare
    pass


def validate_header(magic: bytes, version: int, crc_received: int, payload: bytes) -> bool:
    """
    Valideaza header-ul and CRC-ul.
    
    TODO: Implementati aceasta function
    """
    # TODO: Implementare
    # if magic != MAGIC:
    #     return False
    # if version != VERSION:
    #     return False
    # crc_calculated = calculate_crc32(payload)
    # return crc_received == crc_calculated
    pass


def handle_client(client_socket: socket.socket, address: tuple):
    """
    Handle a client.
    
    TODO: Implementati aceasta function
    Pasi:
    1. Receive header (HEADER_SIZE bytes)
    2. Despacheaza and valideaza
    3. Receive payload
    4. Process and trimite ACK
    """
    print(f"[+] Client conectat: {address}")
    
    # TODO: Implementare
    
    client_socket.close()
    print(f"[-] Client deconectat: {address}")


def start_server(host: str = '0.0.0.0', port: int = DEFAULT_PORT):
    """
    Porneste serverul.
    
    TODO: Implementati aceasta function
    """
    # TODO: Implementare
    pass


if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    start_server(port=port)
