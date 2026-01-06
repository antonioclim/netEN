#!/usr/bin/env python3
"""
Exercise 9.01 – Binary Warm-up (Presentation Layer - L6)

═══════════════════════════════════════════════════════════════════════════════
OBJECTIVES:
═══════════════════════════════════════════════════════════════════════════════
1. Understanding binary data representation (endianness)
2. Building and parsing a protocol header (struct.pack/unpack)
3. The concept of framing: how we delimit messages on a TCP stream
4. Integrity verification with checksum (CRC32)

═══════════════════════════════════════════════════════════════════════════════
KEY CONCEPTS:
═══════════════════════════════════════════════════════════════════════════════

1. ENDIANNESS - Byte order in multi-byte number representation
   
   Example: The number 0x12345678 (4 bytes) in memory:
   
   Big-Endian (Network Order):    Little-Endian (Intel x86):
   ┌────┬────┬────┬────┐          ┌────┬────┬────┬────┐
   │ 12 │ 34 │ 56 │ 78 │          │ 78 │ 56 │ 34 │ 12 │
   └────┴────┴────┴────┘          └────┴────┴────┴────┘
   addr: 0    1    2    3          addr: 0    1    2    3
   
   - Big-Endian: MSB (Most Significant Byte) at lower address
   - Little-Endian: LSB (Least Significant Byte) at lower address
   
2. NETWORK BYTE ORDER - Standard for network protocols
   
   For portability, network protocols use Big-Endian.
   Conversion functions: htons(), htonl(), ntohs(), ntohl()
   In Python struct: "!" or ">" for big-endian, "<" for little-endian

3. FRAMING - Delimiting messages on a TCP stream
   
   TCP does not preserve message boundaries! A send() of 100 bytes can be
   received as: recv(30) + recv(50) + recv(20) or recv(100) or any combination.
   
   Solution: Header with length
   ┌──────────────┬─────────────────────────────────────┐
   │ Length (N)   │ Payload (N bytes)                   │
   └──────────────┴─────────────────────────────────────┘

4. CHECKSUM/CRC - Data integrity verification
   
   CRC32 detects transmission errors or corruption.
   Hashes (SHA256) also detect intentional modifications.

═══════════════════════════════════════════════════════════════════════════════
HEADER STRUCTURE (this exercise):
═══════════════════════════════════════════════════════════════════════════════

┌─────────┬──────────┬───────┬────────────┬──────────────┐
│ Magic   │ Msg Type │ Flags │ Length     │ CRC32        │
│ 2 bytes │ 1 byte   │ 1 B   │ 4 bytes    │ 4 bytes      │
└─────────┴──────────┴───────┴────────────┴──────────────┘
Total: 12 bytes

- Magic: "S9" - identifies the protocol, helps with resynchronisation
- Msg Type: message type (1=data, 2=ack, etc.)
- Flags: option bits (e.g.: compression, encryption)
- Length: payload length
- CRC32: checksum for integrity verification

═══════════════════════════════════════════════════════════════════════════════
USAGE:
═══════════════════════════════════════════════════════════════════════════════

# Selftest - implementation correctness verification
python3 ex_9_01_endianness.py --selftest

# Demo - detailed display of conversions
python3 ex_9_01_endianness.py --demo

# Both
python3 ex_9_01_endianness.py --selftest --demo
"""

from __future__ import annotations

import argparse
import struct
import zlib


# =============================================================================
# Protocol Configuration
# =============================================================================

# Header format: magic(2), msg_type(1), flags(1), length(4), crc32(4)
# Total: 12 bytes

# Network byte order (big-endian) - STANDARD for network protocols
HDR_BE = "!2sBBII"

# Little-endian - for didactic comparison
HDR_LE = "<2sBBII"

# Magic bytes - protocol identifier
MAGIC = b"S9"

# Message types (example)
MSG_TYPE_DATA = 1
MSG_TYPE_ACK = 2
MSG_TYPE_ERROR = 3


# =============================================================================
# Encoding/Decoding Functions
# =============================================================================

def pack_message(payload: bytes, msg_type: int = 1, flags: int = 0, endian: str = "be") -> bytes:
    """
    Packs a payload into a message with header.
    
    Process:
    1. Calculate payload length
    2. Calculate CRC32 of payload
    3. Build header with struct.pack()
    4. Concatenate header + payload
    
    Args:
        payload: Data to send (bytes)
        msg_type: Message type (default: 1)
        flags: Option bits (default: 0)
        endian: "be" for big-endian (network), "le" for little-endian
        
    Returns:
        bytes: Header (12 bytes) + payload
        
    Example:
        >>> msg = pack_message(b"Hello", msg_type=1, endian="be")
        >>> len(msg)
        17  # 12 bytes header + 5 bytes payload
    """
    # Select format based on endianness
    if endian == "be":
        fmt = HDR_BE
    elif endian == "le":
        fmt = HDR_LE
    else:
        raise ValueError("endian must be 'be' or 'le'")
    
    length = len(payload)
    
    # CRC32 returns a signed integer on some platforms
    # & 0xFFFFFFFF ensures we have an unsigned 32-bit
    crc = zlib.crc32(payload) & 0xFFFFFFFF
    
    # struct.pack() converts Python values to bytes according to format
    header = struct.pack(fmt, MAGIC, msg_type, flags, length, crc)
    
    return header + payload


def unpack_message(data: bytes, endian: str = "be") -> dict:
    """
    Unpacks a message with header.
    
    Process:
    1. Extract header (12 bytes)
    2. Parse header with struct.unpack()
    3. Extract payload according to length from header
    4. Verify CRC32
    
    Args:
        data: Complete message (header + payload)
        endian: "be" for big-endian (network), "le" for little-endian
        
    Returns:
        dict with:
            - magic: bytes (should be b"S9")
            - msg_type: int
            - flags: int
            - length: int
            - crc32: int (from header)
            - crc32_ok: bool (verification)
            - payload: bytes
    """
    if endian == "be":
        fmt = HDR_BE
    elif endian == "le":
        fmt = HDR_LE
    else:
        raise ValueError("endian must be 'be' or 'le'")
    
    hdr_len = struct.calcsize(fmt)
    
    if len(data) < hdr_len:
        raise ValueError(f"Insufficient data for header: {len(data)} < {hdr_len}")
    
    # Parse header
    magic, msg_type, flags, length, crc = struct.unpack(fmt, data[:hdr_len])
    
    # Extract payload
    payload = data[hdr_len:hdr_len + length]
    
    # Verify CRC
    calc_crc = zlib.crc32(payload) & 0xFFFFFFFF
    
    return {
        "magic": magic,
        "msg_type": msg_type,
        "flags": flags,
        "length": length,
        "crc32": crc,
        "crc32_ok": (calc_crc == crc),
        "payload": payload,
    }


# =============================================================================
# Demo - Endianness differences visualisation
# =============================================================================

def demo():
    """
    Visual demonstration of differences between Big-Endian and Little-Endian.
    """
    print("═" * 70)
    print("  DEMO: Endianness and Binary Framing (Presentation Layer - L6)")
    print("═" * 70)
    
    # Payload with UTF-8 characters to also demonstrate encoding
    payload = "Hello, S9 – UTF‑8 ✓ Romania".encode("utf-8")
    
    print(f"\n▶ Original payload:")
    print(f"  Text: 'Hello, S9 – UTF‑8 ✓ Romania'")
    print(f"  Bytes ({len(payload)}): {payload}")
    
    # Pack in both formats
    m_be = pack_message(payload, msg_type=2, flags=0xA5, endian="be")
    m_le = pack_message(payload, msg_type=2, flags=0xA5, endian="le")
    
    print(f"\n▶ Header length: {struct.calcsize(HDR_BE)} bytes")
    print(f"  Total message length: {len(m_be)} bytes")
    
    print("\n" + "─" * 70)
    print("  HEADER COMPARISON: Big-Endian vs Little-Endian")
    print("─" * 70)
    
    # Display headers byte by byte
    print("\n  Big-Endian (Network Order):")
    print("  ", end="")
    for i, b in enumerate(m_be[:12]):
        print(f"{b:02x} ", end="")
        if i == 1:
            print(" | ", end="")  # After magic
        elif i == 3:
            print(" | ", end="")  # After flags
        elif i == 7:
            print(" | ", end="")  # After length
    print()
    print("  ↑↑         ↑  ↑   ↑──────────↑   ↑──────────────────↑")
    print("  magic    type flags  length          crc32")
    
    print("\n  Little-Endian:")
    print("  ", end="")
    for i, b in enumerate(m_le[:12]):
        print(f"{b:02x} ", end="")
        if i == 1:
            print(" | ", end="")
        elif i == 3:
            print(" | ", end="")
        elif i == 7:
            print(" | ", end="")
    print()
    
    # Demonstrate concrete difference in length field
    print("\n" + "─" * 70)
    print("  FOCUS: Length Field (4 bytes)")
    print("─" * 70)
    print(f"\n  Value: {len(payload)} (0x{len(payload):08x})")
    print()
    print("  Big-Endian bytes:    ", end="")
    for b in m_be[4:8]:
        print(f"0x{b:02x} ", end="")
    print(f"  → read from left: {len(payload)}")
    
    print("  Little-Endian bytes: ", end="")
    for b in m_le[4:8]:
        print(f"0x{b:02x} ", end="")
    print(f"  → read from right: {len(payload)}")
    
    # Parse correctly
    print("\n" + "─" * 70)
    print("  CORRECT PARSING")
    print("─" * 70)
    
    parsed_be = unpack_message(m_be, endian="be")
    print(f"\n  Big-Endian parsed with BE format:")
    print(f"    magic: {parsed_be['magic']}")
    print(f"    msg_type: {parsed_be['msg_type']}")
    print(f"    flags: 0x{parsed_be['flags']:02x}")
    print(f"    length: {parsed_be['length']}")
    print(f"    crc32_ok: {parsed_be['crc32_ok']}")
    
    # Demonstrate the classic ERROR: wrong endianness
    print("\n" + "─" * 70)
    print("  ⚠ CLASSIC ERROR: Wrong endianness at parsing!")
    print("─" * 70)
    
    wrong = unpack_message(m_be, endian="le")  # BE data, LE format - WRONG!
    
    print(f"\n  BE message parsed with LE format:")
    print(f"    length: {wrong['length']}")
    print(f"      (should be {len(payload)}!)")
    print(f"    crc32_ok: {wrong['crc32_ok']}")
    print(f"      (CRC doesn't match - data appears corrupted!)")
    
    # Calculate what length would be obtained
    # Little-endian interprets bytes in reverse order
    be_length_bytes = struct.pack("!I", len(payload))
    wrong_length = struct.unpack("<I", be_length_bytes)[0]
    print(f"\n  Explanation: {len(payload)} in BE = bytes {list(be_length_bytes)}")
    print(f"    Interpreted as LE: {wrong_length}")
    
    print("\n" + "═" * 70)
    print("  CONCLUSION: Always use NETWORK BYTE ORDER (Big-Endian)")
    print("  in network protocols for portability!")
    print("═" * 70)


# =============================================================================
# Self-test - Correctness verification
# =============================================================================

def selftest():
    """
    Verifies implementation correctness through automated tests.
    """
    print("═" * 50)
    print("  SELF-TEST: Implementation verification")
    print("═" * 50)
    
    # Test 1: Simple payload
    print("\n▶ Test 1: Simple payload...")
    p1 = b"abcd" * 10
    for endian in ["be", "le"]:
        m = pack_message(p1, msg_type=1, flags=0, endian=endian)
        u = unpack_message(m, endian=endian)
        assert u["magic"] == MAGIC, f"Wrong magic: {u['magic']}"
        assert u["payload"] == p1, "Wrong payload"
        assert u["crc32_ok"], "Wrong CRC"
        assert u["length"] == len(p1), f"Wrong length: {u['length']} != {len(p1)}"
    print("   ✓ OK")
    
    # Test 2: Empty payload
    print("▶ Test 2: Empty payload...")
    m = pack_message(b"", endian="be")
    u = unpack_message(m, endian="be")
    assert u["length"] == 0
    assert u["crc32_ok"]
    print("   ✓ OK")
    
    # Test 3: Large payload
    print("▶ Test 3: Large payload (64KB)...")
    p3 = bytes(range(256)) * 256  # 64KB
    m = pack_message(p3, endian="be")
    u = unpack_message(m, endian="be")
    assert u["payload"] == p3
    assert u["crc32_ok"]
    print("   ✓ OK")
    
    # Test 4: Flags
    print("▶ Test 4: All flags (0xFF)...")
    m = pack_message(b"test", flags=0xFF, endian="be")
    u = unpack_message(m, endian="be")
    assert u["flags"] == 0xFF
    print("   ✓ OK")
    
    # Test 5: All message types
    print("▶ Test 5: Message types (0-255)...")
    for mt in [0, 1, 127, 255]:
        m = pack_message(b"x", msg_type=mt, endian="be")
        u = unpack_message(m, endian="be")
        assert u["msg_type"] == mt, f"Wrong msg_type: {u['msg_type']} != {mt}"
    print("   ✓ OK")
    
    # Test 6: UTF-8
    print("▶ Test 6: UTF-8 payload (Romanian characters)...")
    utf8_text = "äöüßÄÖÜ – Unicode ✓".encode("utf-8")
    m = pack_message(utf8_text, endian="be")
    u = unpack_message(m, endian="be")
    assert u["payload"] == utf8_text
    assert u["payload"].decode("utf-8") == "äöüßÄÖÜ – Unicode ✓"
    print("   ✓ OK")
    
    print("\n" + "═" * 50)
    print("  [OK] All tests passed!")
    print("═" * 50)


# =============================================================================
# Main
# =============================================================================

def main():
    ap = argparse.ArgumentParser(
        description="Exercise L6: Endianness and Binary Framing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --selftest        Correctness verification
  %(prog)s --demo            Visual endianness demo
  %(prog)s --selftest --demo Both
        """
    )
    ap.add_argument("--demo", action="store_true", help="Run visual demo")
    ap.add_argument("--selftest", action="store_true", help="Run automated tests")
    args = ap.parse_args()
    
    if not (args.selftest or args.demo):
        ap.print_help()
        print("\n[!] Specify --selftest and/or --demo to run.")
        return
    
    if args.selftest:
        selftest()
        print()
    
    if args.demo:
        demo()


if __name__ == "__main__":
    main()
