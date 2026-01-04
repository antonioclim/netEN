#!/usr/bin/env python3
"""
Common Utilities for Starterkit S9 – File Protocols

This module centralises reusable functions:
- Binary framing (header + payload)
- Compression / decompression
- Hashing (SHA256, CRC32)
- Exact byte reception
- Endianness conversions

Used by: ex_9_01_endianness.py, ex_9_02_pseudo_ftp.py
Licence: MIT
"""

from __future__ import annotations

import gzip
import hashlib
import socket
import struct
import zlib
from typing import Optional, Tuple


# =============================================================================
# Protocol Constants
# =============================================================================

# Week 9 Port Plan
WEEK = 9
WEEK_PORT_BASE = 5100 + 100 * (WEEK - 1)  # 5900
TCP_APP_PORT = WEEK_PORT_BASE  # 5900
UDP_APP_PORT = WEEK_PORT_BASE + 1  # 5901
FTP_CONTROL_PORT = 2121
FTP_PASV_START = 30000
FTP_PASV_END = 30010

# Week 9 IP Plan
NETWORK_PREFIX = f"10.0.{WEEK}"  # 10.0.9
GATEWAY = f"{NETWORK_PREFIX}.1"
HOST_BASE = f"{NETWORK_PREFIX}.11"  # h1=.11, h2=.12, etc.
SERVER_IP = f"{NETWORK_PREFIX}.100"

# Framing constants
BUFFER_SIZE = 8192
DEFAULT_TIMEOUT = 30

# Binary header format: Magic(2) + Version(1) + Flags(1) + Length(4) + CRC32(4) = 12 bytes
HEADER_FORMAT = "!2sBBII"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
MAGIC = b"PF"  # Pseudo-FTP
VERSION = 1
FLAG_GZIP = 0x01
FLAG_SHA256 = 0x02


# =============================================================================
# Framing Functions (L6 - Presentation)
# =============================================================================

def pack_data(payload: bytes, use_gzip: bool = False, include_sha256: bool = False) -> bytes:
    """
    Pack payload with binary header for transfer.
    
    Demonstrates L6 (Presentation) concepts:
    - Framing: header with length for message delimitation
    - Compression: optional gzip
    - Integrity: CRC32 checksum
    
    Args:
        payload: Data to pack
        use_gzip: Enable gzip compression
        include_sha256: Add SHA256 hash after payload
        
    Returns:
        bytes: Header (12 bytes) + payload (optionally compressed)
    """
    flags = 0
    
    # Optional compression
    if use_gzip and len(payload) > 0:
        payload = gzip.compress(payload)
        flags |= FLAG_GZIP
    
    # Optional SHA256 (added at end of payload)
    if include_sha256:
        sha = hashlib.sha256(payload).digest()
        payload = payload + sha
        flags |= FLAG_SHA256
    
    length = len(payload)
    crc = zlib.crc32(payload) & 0xFFFFFFFF
    
    header = struct.pack(HEADER_FORMAT, MAGIC, VERSION, flags, length, crc)
    return header + payload


def unpack_data(data: bytes) -> Tuple[bytes, dict]:
    """
    Unpack received data with binary header.
    
    Args:
        data: Complete message (header + payload)
        
    Returns:
        Tuple[bytes, dict]: (decompressed payload, metadata)
        
    Raises:
        ValueError: If data is invalid
    """
    if len(data) < HEADER_SIZE:
        raise ValueError(f"Insufficient data: {len(data)} < {HEADER_SIZE}")
    
    magic, version, flags, length, crc = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])
    
    if magic != MAGIC:
        raise ValueError(f"Invalid magic: {magic} (expected {MAGIC})")
    
    payload = data[HEADER_SIZE:HEADER_SIZE + length]
    
    if len(payload) != length:
        raise ValueError(f"Incomplete payload: {len(payload)} != {length}")
    
    # CRC verification
    calc_crc = zlib.crc32(payload) & 0xFFFFFFFF
    if calc_crc != crc:
        raise ValueError(f"Invalid CRC: {calc_crc:08x} != {crc:08x}")
    
    # Extract SHA256 if present
    sha256_hash = None
    if flags & FLAG_SHA256:
        sha256_hash = payload[-32:]
        payload = payload[:-32]
    
    # Decompression if needed
    if flags & FLAG_GZIP:
        payload = gzip.decompress(payload)
    
    return payload, {
        "version": version,
        "flags": flags,
        "compressed": bool(flags & FLAG_GZIP),
        "has_sha256": bool(flags & FLAG_SHA256),
        "sha256": sha256_hash.hex() if sha256_hash else None,
        "wire_length": length,
        "crc": crc,
    }


# =============================================================================
# Socket Utilities
# =============================================================================

def recv_all(sock: socket.socket, length: int, timeout: Optional[float] = None) -> bytes:
    """
    Receive exactly `length` bytes from socket.
    
    Args:
        sock: Open socket
        length: Exact number of bytes to receive
        timeout: Optional timeout in seconds
        
    Returns:
        bytes: Exactly `length` bytes
        
    Raises:
        ConnectionError: Connection closed prematurely
        socket.timeout: Timeout exceeded
    """
    if timeout:
        sock.settimeout(timeout)
    
    data = b""
    while len(data) < length:
        chunk = sock.recv(min(length - len(data), BUFFER_SIZE))
        if not chunk:
            raise ConnectionError(f"Connection closed after {len(data)}/{length} bytes")
        data += chunk
    
    return data


def recv_framed(sock: socket.socket, timeout: Optional[float] = None) -> Tuple[bytes, dict]:
    """
    Receive a complete message with framing (header + payload).
    
    Args:
        sock: Open socket
        timeout: Optional timeout
        
    Returns:
        Tuple[bytes, dict]: (payload, metadata)
    """
    # Read header
    header = recv_all(sock, HEADER_SIZE, timeout)
    magic, version, flags, length, crc = struct.unpack(HEADER_FORMAT, header)
    
    if magic != MAGIC:
        raise ValueError(f"Invalid magic: {magic}")
    
    # Read payload
    payload = recv_all(sock, length, timeout) if length > 0 else b""
    
    return unpack_data(header + payload)


def send_framed(sock: socket.socket, payload: bytes, use_gzip: bool = False) -> int:
    """
    Send a message with complete framing.
    
    Args:
        sock: Open socket
        payload: Data to send
        use_gzip: Enable compression
        
    Returns:
        int: Number of bytes sent
    """
    packed = pack_data(payload, use_gzip=use_gzip)
    sock.sendall(packed)
    return len(packed)


# =============================================================================
# Hashing Utilities
# =============================================================================

def compute_sha256(data: bytes) -> str:
    """Calculate SHA256 hash and return hex string."""
    return hashlib.sha256(data).hexdigest()


def compute_crc32(data: bytes) -> int:
    """Calculate CRC32 and return unsigned int."""
    return zlib.crc32(data) & 0xFFFFFFFF


def verify_sha256(data: bytes, expected_hash: str) -> bool:
    """Verify SHA256 hash."""
    return compute_sha256(data) == expected_hash.lower()


# =============================================================================
# Compression Utilities
# =============================================================================

def compress_gzip(data: bytes, level: int = 9) -> bytes:
    """Compress with gzip."""
    return gzip.compress(data, compresslevel=level)


def decompress_gzip(data: bytes) -> bytes:
    """Decompress gzip."""
    return gzip.decompress(data)


def compression_ratio(original: bytes, compressed: bytes) -> float:
    """Calculate compression ratio."""
    if len(original) == 0:
        return 1.0
    return len(compressed) / len(original)


# =============================================================================
# Endianness Helpers
# =============================================================================

def to_network_order_u32(value: int) -> bytes:
    """Convert a uint32 to network byte order (big-endian)."""
    return struct.pack("!I", value)


def from_network_order_u32(data: bytes) -> int:
    """Convert from network byte order to int."""
    return struct.unpack("!I", data)[0]


def to_network_order_u16(value: int) -> bytes:
    """Convert a uint16 to network byte order."""
    return struct.pack("!H", value)


def from_network_order_u16(data: bytes) -> int:
    """Convert from network byte order to int."""
    return struct.unpack("!H", data)[0]


# =============================================================================
# Self-test
# =============================================================================

def _selftest():
    """Verify module functionality."""
    print("═" * 50)
    print("  net_utils.py - Self-test")
    print("═" * 50)
    
    # Test pack/unpack
    print("\n▶ Test pack_data / unpack_data...")
    original = b"Hello, S9! \xc8\x9a\xc4\x83"  # Includes UTF-8
    packed = pack_data(original, use_gzip=True)
    unpacked, meta = unpack_data(packed)
    assert unpacked == original, "Payload mismatch"
    assert meta["compressed"] is True
    print("   ✓ pack/unpack OK")
    
    # Test without compression
    print("▶ Test without compression...")
    packed = pack_data(original, use_gzip=False)
    unpacked, meta = unpack_data(packed)
    assert unpacked == original
    assert meta["compressed"] is False
    print("   ✓ OK")
    
    # Test hashing
    print("▶ Test SHA256...")
    h = compute_sha256(b"test")
    assert len(h) == 64
    assert verify_sha256(b"test", h)
    print("   ✓ OK")
    
    # Test endianness
    print("▶ Test endianness helpers...")
    val = 0x12345678
    net_bytes = to_network_order_u32(val)
    assert net_bytes == b"\x12\x34\x56\x78"
    assert from_network_order_u32(net_bytes) == val
    print("   ✓ OK")
    
    print("\n═" * 50)
    print("  All tests passed!")
    print("═" * 50)


if __name__ == "__main__":
    _selftest()
