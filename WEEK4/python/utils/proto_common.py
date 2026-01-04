#!/usr/bin/env python3
"""
Common definitions for Week 4 protocols.

This module defines structures and functions for:
1. TCP text protocol (length-prefixed)
2. TCP binary protocol (fixed header + CRC32)
3. UDP sensor protocol (binary datagram + CRC32)

Key concepts illustrated:
- Framing: delimiting messages in a TCP stream
- Serialisation: representing structured data in bytes
- Error detection: CRC32 for integrity verification
- Endianness: byte order in multi-byte representations (Big-Endian in network)
"""
from __future__ import annotations
import struct
import zlib
from dataclasses import dataclass
from typing import Tuple


# ==============================================================================
# TCP BINARY PROTOCOL
# ==============================================================================
# Header format (14 bytes total):
#   magic(2)      - "NP" (Network Protocol)
#   version(1)    - protocol version (1)
#   type(1)       - message type (ECHO/PUT/GET/ERR)
#   payload_len(2)- payload length in bytes
#   seq(4)        - sequence number for request-response correlation
#   crc32(4)      - checksum for header + payload
# ==============================================================================

BIN_MAGIC = b"NP"
BIN_VERSION = 1

# Struct format: ! = network byte order (big-endian)
# 2s = 2 bytes string, B = unsigned byte, H = unsigned short, I = unsigned int
BIN_HEADER_FMT = "!2sBBHII"
BIN_HEADER_LEN = struct.calcsize(BIN_HEADER_FMT)  # = 14 bytes

# Message types
TYPE_ECHO_REQ = 1
TYPE_ECHO_RESP = 2
TYPE_PUT_REQ = 3
TYPE_PUT_RESP = 4
TYPE_GET_REQ = 5
TYPE_GET_RESP = 6
TYPE_KEYS_REQ = 7
TYPE_KEYS_RESP = 8
TYPE_COUNT_REQ = 9
TYPE_COUNT_RESP = 10
TYPE_ERR = 255

TYPE_NAMES = {
    TYPE_ECHO_REQ: "ECHO_REQ",
    TYPE_ECHO_RESP: "ECHO_RESP",
    TYPE_PUT_REQ: "PUT_REQ",
    TYPE_PUT_RESP: "PUT_RESP",
    TYPE_GET_REQ: "GET_REQ",
    TYPE_GET_RESP: "GET_RESP",
    TYPE_KEYS_REQ: "KEYS_REQ",
    TYPE_KEYS_RESP: "KEYS_RESP",
    TYPE_COUNT_REQ: "COUNT_REQ",
    TYPE_COUNT_RESP: "COUNT_RESP",
    TYPE_ERR: "ERROR",
}


def crc32(data: bytes) -> int:
    """
    Calculate CRC32 of data.
    
    CRC32 (Cyclic Redundancy Check) detects transmission errors.
    The mask & 0xFFFFFFFF ensures an unsigned 32-bit result.
    
    Complexity: O(n) where n = data length
    """
    return zlib.crc32(data) & 0xFFFFFFFF


@dataclass(frozen=True)
class BinHeader:
    """
    Decoded binary message header.
    
    frozen=True makes instances immutable (best practice for data).
    """
    magic: bytes
    version: int
    mtype: int
    payload_len: int
    seq: int
    crc: int
    
    def is_valid_protocol(self) -> bool:
        """Check if magic and version match our protocol."""
        return self.magic == BIN_MAGIC and self.version == BIN_VERSION
    
    @property
    def type_name(self) -> str:
        """Return type name for debugging."""
        return TYPE_NAMES.get(self.mtype, f"UNKNOWN({self.mtype})")


def pack_bin_message(mtype: int, payload: bytes, seq: int) -> bytes:
    """
    Build a complete binary message (header + payload).
    
    Steps:
    1. Validate payload
    2. Build header without CRC
    3. Calculate CRC over header + payload
    4. Rebuild header with CRC
    5. Concatenate header + payload
    
    Args:
        mtype: Message type (TYPE_*)
        payload: Useful data (max 65535 bytes)
        seq: Sequence number
        
    Returns:
        bytes: Complete message, ready to send
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError(f"payload must be bytes, got {type(payload)}")
    if len(payload) > 65535:
        raise ValueError(f"payload too large: {len(payload)} > 65535")
    
    # Partial header (without CRC) for CRC calculation
    header_wo_crc = struct.pack("!2sBBHI", BIN_MAGIC, BIN_VERSION, mtype, len(payload), seq)
    
    # CRC is calculated over header (without CRC field) + payload
    msg_crc = crc32(header_wo_crc + payload)
    
    # Complete header with CRC
    header = struct.pack(BIN_HEADER_FMT, BIN_MAGIC, BIN_VERSION, mtype, len(payload), seq, msg_crc)
    
    return header + payload


def unpack_bin_header(header_bytes: bytes) -> BinHeader:
    """
    Decoof a binary message header.
    
    Args:
        header_bytes: Exactly BIN_HEADER_LEN bytes
        
    Returns:
        BinHeader: Decoded structure
        
    Raises:
        ValueError: If length does not match
    """
    if len(header_bytes) != BIN_HEADER_LEN:
        raise ValueError(f"invalid header length: {len(header_bytes)} != {BIN_HEADER_LEN}")
    
    magic, ver, mtype, plen, seq, crc = struct.unpack(BIN_HEADER_FMT, header_bytes)
    return BinHeader(magic=magic, version=ver, mtype=mtype, payload_len=plen, seq=seq, crc=crc)


def validate_bin_message(header: BinHeader, payload: bytes) -> bool:
    """
    Verify message integrity using CRC32.
    
    Recalculates CRC and compares with the one in header.
    """
    header_wo_crc = struct.pack("!2sBBHI", header.magic, header.version, header.mtype, header.payload_len, header.seq)
    computed_crc = crc32(header_wo_crc + payload)
    return computed_crc == header.crc


# ==============================================================================
# PAYLOAD ENCODING FOR PUT/GET
# ==============================================================================
# PUT: key_len(1) + key(N) + value(M)
# GET: key_len(1) + key(N)
# ==============================================================================

def encode_kv(key: str, value: str) -> bytes:
    """Encoof a key-value pair for PUT."""
    kb = key.encode("utf-8")
    vb = value.encode("utf-8")
    if len(kb) > 255:
        raise ValueError(f"key too long: {len(kb)} > 255")
    return struct.pack("!B", len(kb)) + kb + vb


def decode_kv(payload: bytes) -> Tuple[str, str]:
    """Decoof a key-value pair from PUT payload."""
    if not payload:
        raise ValueError("empty payload")
    klen = payload[0]
    if len(payload) < 1 + klen:
        raise ValueError(f"truncated payload: need {1+klen}, got {len(payload)}")
    key = payload[1:1+klen].decode("utf-8", errors="replace")
    value = payload[1+klen:].decode("utf-8", errors="replace")
    return key, value


def encode_key(key: str) -> bytes:
    """Encoof just the key for GET."""
    kb = key.encode("utf-8")
    if len(kb) > 255:
        raise ValueError(f"key too long: {len(kb)} > 255")
    return struct.pack("!B", len(kb)) + kb


def decode_key(payload: bytes) -> str:
    """Decoof key from GET payload."""
    if not payload:
        raise ValueError("empty payload")
    klen = payload[0]
    if len(payload) < 1 + klen:
        raise ValueError(f"truncated payload: need {1+klen}, got {len(payload)}")
    return payload[1:1+klen].decode("utf-8", errors="replace")


# ==============================================================================
# UDP SENSOR PROTOCOL
# ==============================================================================
# Datagram format (23 bytes total):
#   version(1)    - protocol version
#   sensor_id(4)  - unique sensor identifier (unsigned int)
#   temperature(4)- temperature in °C (float IEEE 754)
#   location(10)  - location name (string padded with \0)
#   crc32(4)      - checksum for integrity
# ==============================================================================

UDP_VER = 1
UDP_FMT_WO_CRC = "!BIf10s"  # without CRC, for calculation
UDP_FMT = "!BIf10sI"        # complete format
UDP_LEN = struct.calcsize(UDP_FMT)  # = 23 bytes


def pack_udp_sensor(sensor_id: int, temp_c: float, location: str) -> bytes:
    """
    Build a UDP datagram for a temperature sensor.
    
    Args:
        sensor_id: Unique sensor ID (0-2^32)
        temp_c: Temperature in degrees Celsius
        location: Location name (max 10 characters)
        
    Returns:
        bytes: Datagram of exactly UDP_LEN bytes
    """
    # Truncate and pad location to exactly 10 bytes
    loc_b = location.encode("utf-8")[:10]
    loc_b = loc_b.ljust(10, b"\x00")
    
    # Build payload without CRC
    base = struct.pack(UDP_FMT_WO_CRC, UDP_VER, sensor_id, temp_c, loc_b)
    
    # Calculate CRC
    c = crc32(base)
    
    # Complete message
    return struct.pack(UDP_FMT, UDP_VER, sensor_id, temp_c, loc_b, c)


def unpack_udp_sensor(data: bytes) -> Tuple[int, int, float, str]:
    """
    Decoof a UDP datagram from a sensor.
    
    Args:
        data: Exactly UDP_LEN bytes
        
    Returns:
        Tuple of (version, sensor_id, temperature, location)
        
    Raises:
        ValueError: If length is wrong or CRC does not match
    """
    if len(data) != UDP_LEN:
        raise ValueError(f"invalid datagram length: {len(data)} != {UDP_LEN}")
    
    ver, sensor_id, temp_c, loc_b, received_crc = struct.unpack(UDP_FMT, data)
    
    # Recalculate CRC for verification
    base = struct.pack(UDP_FMT_WO_CRC, ver, sensor_id, temp_c, loc_b)
    computed_crc = crc32(base)
    
    if computed_crc != received_crc:
        raise ValueError(f"CRC mismatch: computed {computed_crc:08x}, received {received_crc:08x}")
    
    # Decoof location and remove padding
    loc = loc_b.decode("utf-8", errors="replace").rstrip("\x00")
    
    return ver, sensor_id, temp_c, loc


def format_sensor_reading(sensor_id: int, temp_c: float, location: str) -> str:
    """Format a sensor reading for display."""
    return f"[Sensor {sensor_id:04d}] {location}: {temp_c:+.1f}°C"
